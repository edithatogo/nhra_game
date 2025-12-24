"""
NHRA stylised hybrid model (v9) — dynamic NEP vs input cost drift

This is a *mechanism* model: it encodes several strategic "games" and a simple system-dynamics backbone.

Design goals:
- Clear mapping from policy levers → parameters → trajectories
- Scenario and sensitivity analysis out of the box
- Publication-friendly plots and an interactive network diagram

Limitations:
- Highly stylised; not a forecast; no inference about real-world mortality
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Any, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

# ----------------------------
# Utilities
# ----------------------------


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def softmax(u: NDArray[np.floating[Any]], tau: float = 0.25) -> NDArray[np.floating[Any]]:
    u = np.asarray(u, dtype=float)
    u = u - u.max()
    z = np.exp(u / max(1e-9, tau))
    return cast(NDArray[np.floating[Any]], np.asarray(z / z.sum(), dtype=float))


# ----------------------------
# Parameters and state
# ----------------------------


@dataclass(frozen=True)
class Params:
    # Funding / valuation
    nep_to_cost_ratio_metro: float = 0.90
    nep_to_cost_ratio_regional: float = 0.83
    nep_to_cost_ratio_remote: float = 0.75

    rurality_weight: float = 0.35  # fraction of activity outside metro
    remote_weight: float = 0.07  # subset weight in remote

    nominal_cth_share_target: float = 0.45
    effective_cth_share_base: float = 0.38

    cap_growth: float = 0.065  # "hard cap" annual
    has_cumulative_cap: bool = False
    use_equilibrium_bargaining: bool = False  # v14 option
    use_stage_game_equilibria: bool = True  # v15: solve and use all stage-game equilibria
    equilibrium_selection_rule: str = "payoff_dominant"  # payoff_dominant | row_favourable | random

    # NEP (National Efficient Price) scaffolding
    # NOTE: In IHACPA/ABF, NEP is an annual $/NWAU value which is multiplied by a service NWAU weight to form an efficient payment.
    # In this model, NEP is used mainly for *reporting and scenario comparison* (not detailed ABF accounting).
    nep_per_nwau_start: float = 1.0  # index units; set to actual $/NWAU if desired
    nep_annual_growth: float = 0.03
    representative_nwau: float = (
        1.0  # a single representative activity weight for illustrative calculations
    )

    # Input costs (index units per NWAU; proxies workforce + supply costs)
    input_cost_per_nwau_start: float = 1.0
    input_cost_annual_growth: float = 0.04

    # System dynamics
    demand_base: float = 1.00
    avoidable_ed_share: float = 0.18
    discharge_delay_base: float = 1.00  # multiplier
    bed_capacity_index: float = 1.00  # 1.0 baseline

    # Couplings
    cost_shifting_intensity: float = 0.35  # VFI spillover strength
    fragmentation_index: float = 1.00  # UCC/primary care integration etc
    audit_pressure: float = 0.50  # compliance scrutiny baseline
    admin_burden_weight: float = 0.25

    # Pressure mapping
    occupancy_base: float = 0.88
    offload_base_min: float = 18.0  # minutes
    within4_base: float = 0.53

    # Risk proxy mapping (relative, not absolute)
    rr_beta_pressure: float = 0.35
    rr_beta_offload: float = 0.015  # per minute above threshold (stylised)
    offload_threshold_min: float = 20.0

    # Behavioural weights
    tau: float = 0.25  # softmax temperature
    bargaining_cost: float = 0.12
    political_salience: float = 0.30

    # Bounded Rationality (v25 re-integration)
    use_quantal_response: bool = False  # If True, use logit-response instead of pure Nash
    qre_lambda: float = 4.0  # Sensitivity of response to payoff differences

    # Audit Burden Feedback Loop (v25 re-integration)
    use_burden_feedback: bool = False  # If True, pressure increases admin burden B_t
    burden_to_throughput_beta: float = 0.06  # Sensitivity of throughput to burden B_t

    # Randomness
    noise_sd: float = 0.03

    # Empirical Spine (optional)
    economic_spine: pd.DataFrame | None = None


@dataclass(frozen=True)
class State:
    year: int
    pressure: float
    occupancy: float
    offload_min: float
    within4: float
    effective_cth_share: float
    efficiency_gap: float
    discharge_delay: float
    political_capital: float


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    if p is None:
        p = Params()
    # Efficiency gap implied by rurality mix
    metro_ratio = p.nep_to_cost_ratio_metro
    reg_ratio = p.nep_to_cost_ratio_regional
    rem_ratio = p.nep_to_cost_ratio_remote
    ratio = (
        (1 - p.rurality_weight) * metro_ratio
        + (p.rurality_weight - p.remote_weight) * reg_ratio
        + p.remote_weight * rem_ratio
    )
    efficiency_gap = 1.0 / max(1e-9, ratio) - 1.0  # e.g., 0.20 means costs 20% above NEP

    return State(
        year=start_year,
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        effective_cth_share=p.effective_cth_share_base
        * (1.0 + efficiency_gap),  # store nominal share
        efficiency_gap=efficiency_gap,
        discharge_delay=p.discharge_delay_base,
        political_capital=1.0,
    )


# ----------------------------
# "Games" — minimal label set
# ----------------------------

GAME_NODES = {
    "BARG": "Bargaining",
    "DEF": "Definition",
    "SHIFT": "Cost-shifting",
    "DISC": "Discharge",
    "GOV": "Integration",
    "COMP": "Compliance",
    "SIGNAL": "Signalling",
}


def decide_strategies(s: State, p: Params, rng: np.random.Generator) -> dict[str, str]:
    """Choose strategies for the interacting 'games' layer.

    IMPORTANT: The returned keys and minimal labels are designed to match the model's mechanism map
    and the downstream transition function `step()`, which expects:

      - SIGNAL: H/L (high/low transparency)
      - DEF: R/E (realism vs strict efficient framing)
      - BARG: A/D (agree/converge vs defer/escalate)
      - DISC: C/F (coordinate discharge vs fragment)
      - GOV: I/S (integrated governance vs separate)
      - SHIFT: I/S (invest upstream vs shift downstream)
      - COMP: T/L (tight vs light compliance)

    v15: when `p.use_stage_game_equilibria` is True, each stage game is solved for *all* Nash equilibria
    (pure +, when applicable, mixed). An equilibrium is selected by the configured rule.
    """
    noise = float(rng.normal(0.0, p.noise_sd))

    # Signalling game kept as bounded-rational (it is a communication choice)
    u_H = +0.10 + 0.30 * (s.pressure - 1.0) + noise
    u_L = +0.05 - 0.10 * (s.pressure - 1.0) - noise
    prob_sig = softmax(np.array([u_L, u_H]), tau=p.tau)
    signal = "H" if rng.random() < prob_sig[1] else "L"

    if p.use_stage_game_equilibria:
        from nhra_game_theory.subgames.games import (
            GameParams,
            bargaining_game,
            compliance_game,
            cost_shifting_game,
            definition_game,
            discharge_coordination_game,
            governance_integration_game,
        )
        from nhra_game_theory.subgames.nash import TwoPlayerGame, all_nash, select_equilibrium

        gp = GameParams(
            pressure=float(s.pressure),
            efficiency_gap=float(s.efficiency_gap),
            discharge_delay=float(s.discharge_delay),
            political_salience=float(p.political_salience),
            audit_pressure=float(p.audit_pressure),
            cost_shifting_intensity=float(p.cost_shifting_intensity),
            political_capital=float(s.political_capital),
        )

        def _solve(game: TwoPlayerGame) -> tuple[str, str]:
            if p.use_quantal_response:
                # Quantal Response Equilibrium (v25 re-integration)
                # We use a simplified logit response to the minimax/dominant payoffs
                # for 2x2 games to ensure smooth transitions.
                # P(action) ~ exp(lambda * expected_payoff)

                # Assume opponent plays uniform random for the first-order response
                u_row_expected = np.mean(game.u_row, axis=1)
                u_col_expected = np.mean(game.u_col, axis=0)

                prob_row = softmax(u_row_expected, tau=1.0 / max(1e-9, p.qre_lambda))
                prob_col = softmax(u_col_expected, tau=1.0 / max(1e-9, p.qre_lambda))

                row_a = game.row_actions[1] if rng.random() < prob_row[1] else game.row_actions[0]
                col_a = game.col_actions[1] if rng.random() < prob_col[1] else game.col_actions[0]
                return row_a, col_a
            else:
                eqs = all_nash(game)
                sel = select_equilibrium(
                    eqs, rule=p.equilibrium_selection_rule, u_row=game.u_row, u_col=game.u_col
                )
                row_a = game.row_actions[int(np.argmax(sel.row))]
                col_a = game.col_actions[int(np.argmax(sel.col))]
                return row_a, col_a

        # Definition: if either plays E (Strict), the gap widens?
        # Or does Cth control definition? Let's say if Cth plays R (Realism), it helps.
        # But if State plays E (Strict), they demand more?
        # Current step() logic: if strategies["DEF"] == "R": eff_gap *= 0.93
        # Let's keep DEF as Row-driven (Cth narrative).
        r_def, _ = _solve(definition_game(gp))
        DEF = r_def

        # Bargaining: A if both Agree? If one Defers, delay.
        # Current: A -> eff_share converges fast. D -> slow.
        # Ideally, requires mutual agreement.
        r_barg, c_barg = _solve(bargaining_game(gp))
        BARG = "A" if (r_barg == "A" and c_barg == "A") else "D"

        # Cost Shifting: S if anyone Shifts.
        r_shift, c_shift = _solve(cost_shifting_game(gp))
        SHIFT = "S" if (r_shift == "S" or c_shift == "S") else "I"

        # Discharge: C only if both Coordinate.
        r_disc, c_disc = _solve(discharge_coordination_game(gp))
        DISC = "C" if (r_disc == "C" and c_disc == "C") else "F"

        # Governance: I only if both Integrate.
        r_gov, c_gov = _solve(governance_integration_game(gp))
        GOV = "I" if (r_gov == "I" and c_gov == "I") else "S"

        # Compliance: Row (Cth) drives audit intensity (T/L). Col (State) just responds.
        # But step() uses COMP to determine admin burden.
        # If Cth plays T, burden high.
        r_comp, _ = _solve(compliance_game(gp))
        COMP = r_comp

    else:
        # Heuristic fallbacks (keep monotone relationships with pressure and efficiency gap)
        DEF = (
            "R"
            if rng.random() < logistic(1.3 * (s.efficiency_gap - 0.25) + 0.9 * (s.pressure - 1.0))
            else "E"
        )
        BARG = (
            "A"
            if rng.random() < logistic(0.6 * (1.2 - s.pressure) - 0.4 * p.political_salience)
            else "D"
        )
        SHIFT = (
            "I"
            if rng.random() < logistic(-1.1 * (s.pressure - 1.0) - 1.0 * s.efficiency_gap)
            else "S"
        )
        DISC = (
            "C"
            if rng.random() < logistic(-0.9 * (s.discharge_delay - 1.0) - 0.8 * (s.pressure - 1.0))
            else "F"
        )
        GOV = (
            "I"
            if rng.random() < logistic(-0.8 * (s.pressure - 1.0) - 0.7 * p.political_salience)
            else "S"
        )
        COMP = (
            "T" if rng.random() < logistic(0.9 * p.audit_pressure - 0.7 * s.efficiency_gap) else "L"
        )

    return {
        "SIGNAL": signal,
        "DEF": DEF,
        "BARG": BARG,
        "SHIFT": SHIFT,
        "DISC": DISC,
        "GOV": GOV,
        "COMP": COMP,
    }


def pressure_index(occupancy: float, offload_min: float, discharge_delay: float) -> float:
    """
    Simple composite pressure index:
    - Occupancy above ~0.88 increases pressure sharply
    - Offload above ~20 minutes increases pressure
    - Discharge delay multiplies both
    """
    occ_term = logistic((occupancy - 0.88) / 0.03)
    off_term = logistic((offload_min - 20.0) / 8.0)
    return 0.8 + 0.8 * (0.55 * occ_term + 0.45 * off_term) * discharge_delay


def within4_from_pressure(pidx: float) -> float:
    # Calibrate so pidx=1 -> ~0.53
    return clamp(0.80 - 0.45 * logistic((pidx - 1.0) / 0.20), 0.05, 0.85)


def relative_risk(pidx: float, offload_min: float, p: Params) -> float:
    """
    Relative risk proxy combining 'pressure' and 'offload' contributions.
    """
    rr_p = math.exp(p.rr_beta_pressure * max(0.0, pidx - 1.0))
    rr_o = math.exp(p.rr_beta_offload * max(0.0, offload_min - p.offload_threshold_min))
    return rr_p * rr_o


def step(s: State, p: Params, strategies: dict[str, str], rng: np.random.Generator) -> State:
    # Funding/valuation effects
    # Definition realism reduces efficiency gap; strict NEP increases it
    # --- Macro drift: input costs vs NEP indexation (annual) ---

    if (
        p.economic_spine is not None
        and s.year in p.economic_spine["year"].values
        and (s.year + 1) in p.economic_spine["year"].values
    ):
        # Calculate year-on-year growth from spine
        row_curr = p.economic_spine[p.economic_spine["year"] == s.year].iloc[0]
        row_next = p.economic_spine[p.economic_spine["year"] == (s.year + 1)].iloc[0]

        growth_nep = (row_next["nep_per_nwau"] / row_curr["nep_per_nwau"]) - 1.0
        growth_wpi = (row_next["wpi_health_index"] / row_curr["wpi_health_index"]) - 1.0

        drift_factor = (1.0 + growth_wpi) / (1.0 + growth_nep)
    else:
        # Fallback to constant growth
        drift_factor = (1.0 + float(p.input_cost_annual_growth)) / (
            1.0 + float(p.nep_annual_growth)
        )

    # Apply drift to the *level* (1+gap), not just the gap.
    eff_gap = (1.0 + float(s.efficiency_gap)) * drift_factor - 1.0

    if strategies["DEF"] == "R":
        eff_gap *= 0.93
    else:
        eff_gap *= 1.03
    eff_gap = clamp(eff_gap, 0.05, 0.60)

    # Bargaining sets a *nominal* share (effective share is computed downstream using the efficiency gap).
    eff_share = s.effective_cth_share
    target = p.nominal_cth_share_target
    if strategies["BARG"] == "A":
        eff_share = eff_share + 0.25 * (target - eff_share)
    else:
        eff_share = eff_share + 0.10 * (target - eff_share)
    eff_share = clamp(eff_share, 0.30, 0.50)

    # Discharge capacity affects discharge delay
    discharge = s.discharge_delay
    if strategies["DISC"] == "C":
        discharge *= 0.90
    else:
        discharge *= 1.02

    # Audit Burden Feedback (v25 re-integration)
    if p.use_burden_feedback:
        # Pressure increases admin complexity, reducing effective discharge throughput
        discharge *= math.exp(p.burden_to_throughput_beta * max(0.0, s.pressure - 1.0))

    discharge = clamp(discharge, 0.75, 1.50)

    # Integration affects avoidable demand and fragmentation (externalities)
    fragmentation = p.fragmentation_index
    avoidable = p.avoidable_ed_share
    if strategies["GOV"] == "I":
        fragmentation *= 0.88
        avoidable *= 0.90
    else:
        fragmentation *= 1.02
        avoidable *= 1.01
    fragmentation = clamp(fragmentation, 0.70, 1.35)
    avoidable = clamp(avoidable, 0.08, 0.30)

    # Cost shifting / upstream investment affects demand and discharge multipliers
    demand = p.demand_base
    if strategies["SHIFT"] == "I":
        demand *= 0.96
        discharge *= 0.97
    else:
        demand *= 1.04
        discharge *= 1.02

    # Compliance increases admin burden which slightly worsens pressure (less clinical time)
    admin_burden = 1.0 + p.admin_burden_weight * (1 if strategies["COMP"] == "T" else -0.25)
    admin_burden = clamp(admin_burden, 0.85, 1.35)

    # Occupancy update: demand ↑ and discharge delay ↑ increase occupancy; capacity index ↓ worsens
    occ = s.occupancy
    occ += 0.015 * (demand - 1.0) + 0.035 * (discharge - 1.0) + 0.008 * (admin_burden - 1.0)
    # Efficiency gap acts like a recurrent variance, tightening capacity indirectly (stylised)
    occ += 0.012 * (eff_gap - 0.15)
    occ -= 0.010 * (p.bed_capacity_index - 1.0)
    occ = clamp(occ, 0.78, 0.98)

    # Offload update: responds to occupancy and fragmentation
    off = s.offload_min
    off += 8.0 * (occ - 0.88) + 3.0 * (fragmentation - 1.0) + rng.normal(0, 0.8)
    off = clamp(off, 5.0, 120.0)

    pidx = pressure_index(occ, off, discharge)
    w4 = within4_from_pressure(pidx)

    # Political Capital update (v25 re-integration)
    pol_cap = s.political_capital
    if strategies["BARG"] == "A":
        pol_cap += 0.05  # Agreement restores capital
    else:
        pol_cap -= 0.10  # Conflict depletes capital
    pol_cap = clamp(pol_cap, 0.0, 2.0)

    return State(
        year=s.year + 1,
        pressure=pidx,
        occupancy=occ,
        offload_min=off,
        within4=w4,
        effective_cth_share=eff_share,
        efficiency_gap=eff_gap,
        discharge_delay=discharge,
        political_capital=pol_cap,
    )


# ----------------------------
# Scenarios & interventions
# ----------------------------


def apply_intervention(p: Params, name: str) -> Params:
    """
    Map policy interventions to parameter shifts.
    """
    name = name.lower().strip().replace(" ", "_")
    if name in {"pooled_funding", "pooled"}:
        return replace(
            p, cost_shifting_intensity=clamp(p.cost_shifting_intensity * 0.75, 0.05, 0.60)
        )
    if name in {"ucc_integration", "integration"}:
        return replace(p, fragmentation_index=clamp(p.fragmentation_index * 0.80, 0.60, 1.50))
    if name in {"nep_realism", "indexation"}:
        return replace(
            p,
            nep_to_cost_ratio_metro=clamp(p.nep_to_cost_ratio_metro + 0.03, 0.6, 1.0),
            nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.04, 0.6, 1.0),
            nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.05, 0.6, 1.0),
        )
    if name in {"aged_ndis_capacity", "discharge"}:
        return replace(p, discharge_delay_base=clamp(p.discharge_delay_base * 0.90, 0.6, 1.4))
    if name in {"middle_tier", "workforce"}:
        # reduces remote/regional cost penalties
        return replace(
            p,
            nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.03, 0.6, 1.0),
            nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.04, 0.6, 1.0),
        )
    if name in {"cumulative_cap", "cap"}:
        return replace(p, has_cumulative_cap=True, cap_growth=0.070)
    if name in {"audit_relief"}:
        return replace(
            p,
            audit_pressure=clamp(p.audit_pressure * 0.70, 0.05, 1.0),
            admin_burden_weight=clamp(p.admin_burden_weight * 0.8, 0.05, 0.6),
        )
    return p


def scenario_params(base: Params, interventions: Iterable[str]) -> Params:
    p = base
    for iv in interventions:
        p = apply_intervention(p, iv)
    return p


def nep_series(years: list[int], p: Params) -> pd.DataFrame:
    """Return an illustrative NEP series.

    NEP is represented as an *index* by default (`nep_per_nwau_start=1.0`), but you may
    set it to the IHACPA $/NWAU level and growth schedule if you want dollar outputs.

    Returns columns:
      - year
      - nep_per_nwau
      - efficient_payment = nep_per_nwau * representative_nwau
    """
    nep = float(p.nep_per_nwau_start)
    rows = []
    for i, y in enumerate(years):
        if i > 0:
            nep *= 1.0 + float(p.nep_annual_growth)
        rows.append(
            {
                "year": int(y),
                "nep_per_nwau": float(nep),
                "representative_nwau": float(p.representative_nwau),
                "efficient_payment": float(nep * float(p.representative_nwau)),
            }
        )
    return pd.DataFrame(rows)


def input_cost_series(years: list[int], p: Params) -> pd.DataFrame:
    """Return an illustrative input-cost series (index units per NWAU).

    This is intended as a proxy for the *average* input cost per NWAU (wages, agency premiums,
    supplies). In an empirically grounded build, `input_cost_annual_growth` should be set using
    an evidence-based proxy (e.g., ABS Wage Price Index for Health Care & Social Assistance plus
    a locum/agency premium series where available).

    Returns columns:
      - year
      - input_cost_per_nwau
    """
    cost = float(p.input_cost_per_nwau_start)
    rows = []
    for i, y in enumerate(years):
        if i > 0:
            cost *= 1.0 + float(p.input_cost_annual_growth)
        rows.append({"year": int(y), "input_cost_per_nwau": float(cost)})
    return pd.DataFrame(rows)


def nep_vs_cost_series(years: list[int], p: Params) -> pd.DataFrame:
    """Combine NEP and input-cost indices.

    Adds:
      - nep_per_nwau
      - input_cost_per_nwau
      - nep_to_cost_ratio_index = nep / cost
      - cost_over_nep_index = cost / nep
    """
    nep_df = nep_series(years, p)[["year", "nep_per_nwau"]]
    cost_df = input_cost_series(years, p)
    out = nep_df.merge(cost_df, on="year", how="inner")
    out["nep_to_cost_ratio_index"] = out["nep_per_nwau"] / out["input_cost_per_nwau"]
    out["cost_over_nep_index"] = out["input_cost_per_nwau"] / out["nep_per_nwau"]
    return out


def apply_intervention_partial(base: Params, name: str, strength: float) -> Params:
    """Apply an intervention at partial strength (0..1).

    This is a pragmatic way to represent staged implementation or partial uptake.
    """
    strength = float(clamp(strength, 0.0, 1.0))
    if strength == 0.0:
        return base
    full = apply_intervention(base, name)
    # Linear interpolation of a subset of key parameters used in intervention mappings.
    return replace(
        base,
        cost_shifting_intensity=base.cost_shifting_intensity
        + strength * (full.cost_shifting_intensity - base.cost_shifting_intensity),
        fragmentation_index=base.fragmentation_index
        + strength * (full.fragmentation_index - base.fragmentation_index),
        discharge_delay_base=base.discharge_delay_base
        + strength * (full.discharge_delay_base - base.discharge_delay_base),
        has_cumulative_cap=full.has_cumulative_cap if strength >= 0.5 else base.has_cumulative_cap,
        cap_growth=base.cap_growth + strength * (full.cap_growth - base.cap_growth),
        audit_pressure=base.audit_pressure + strength * (full.audit_pressure - base.audit_pressure),
        admin_burden_weight=base.admin_burden_weight
        + strength * (full.admin_burden_weight - base.admin_burden_weight),
    )


def scenario_summary(
    years: list[int],
    base: Params,
    scenarios: dict[str, list[str]],
    seed: int = 123,
    n_mc: int = 250,
) -> pd.DataFrame:
    """Run named intervention bundles and return end-year summaries."""
    rows: list[dict[str, float | str | int]] = []
    for name, interventions in scenarios.items():
        p = scenario_params(base, interventions)
        traj, _ = run_hybrid(years, p, seed=seed, n_mc=n_mc)
        end = traj.iloc[-1].to_dict()
        rows.append(
            {
                "scenario": name,
                "interventions": ",".join(interventions) if interventions else "",
                "end_year": int(years[-1]),
                "pressure_mean": float(end["pressure_mean"]),
                "offload_mean": float(end["offload_mean"]),
                "within4_mean": float(end["within4_mean"]),
                "rr_mean": float(end["rr_mean"]),
                "cth_nominal_mean": float(end.get("cth_nominal_mean", float("nan"))),
                "cth_effective_mean": float(end.get("cth_effective_mean", float("nan"))),
                "effgap_mean": float(end.get("effgap_mean", float("nan"))),
                "discharge_mean": float(end.get("discharge_mean", float("nan"))),
            }
        )
    return pd.DataFrame(rows)


def one_way_sensitivity(
    years: list[int],
    base: Params,
    grid: dict[str, list[float]],
    seed: int = 123,
    n_mc: int = 150,
) -> pd.DataFrame:
    """One-way sensitivity analysis over a small parameter grid."""
    rows: list[dict[str, float | str]] = []
    for param, values in grid.items():
        for v in values:
            p = replace(base, **{param: float(v)}) if hasattr(base, param) else base
            traj, _ = run_hybrid(years, p, seed=seed, n_mc=n_mc)
            end = traj.iloc[-1]
            rows.append(
                {
                    "param": str(param),
                    "value": float(v),
                    "rr_end": float(end["rr_mean"]),
                    "pressure_end": float(end["pressure_mean"]),
                    "within4_end": float(end["within4_mean"]),
                    "offload_end": float(end["offload_mean"]),
                }
            )
    return pd.DataFrame(rows)


def probabilistic_sensitivity(
    years: list[int],
    base: Params,
    interventions: list[str],
    seed: int = 123,
    n_param: int = 200,
    n_mc: int = 120,
) -> pd.DataFrame:
    """Simple PSA over a few key parameters (stylised)."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, float]] = []
    for i in range(int(n_param)):
        p = replace(
            base,
            noise_sd=float(np.clip(rng.normal(base.noise_sd, base.noise_sd * 0.25), 0.001, 0.2)),
            discharge_delay_base=float(
                np.clip(rng.normal(base.discharge_delay_base, 0.15), 0.5, 2.0)
            ),
            cost_shifting_intensity=float(
                np.clip(rng.normal(base.cost_shifting_intensity, 0.08), 0.05, 0.8)
            ),
        )
        p = scenario_params(p, interventions)
        traj, _ = run_hybrid(years, p, seed=int(seed + i), n_mc=n_mc)
        end = traj.iloc[-1]
        rows.append(
            {
                "rr_end": float(end["rr_mean"]),
                "pressure_end": float(end["pressure_mean"]),
                "within4_end": float(end["within4_mean"]),
                "offload_end": float(end["offload_mean"]),
            }
        )
    return pd.DataFrame(rows)


def run_hybrid(
    years: list[int], p: Params, seed: int = 123, n_mc: int = 300, recorder: Any | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Monte Carlo rollouts of the hybrid model.
    Returns:
      - trajectories: mean + quantiles by year
      - strategy_freq: frequency table by year & game
    """
    if recorder:
        recorder.start_experiment(
            experiment_name=f"hybrid_sim_{years[0]}_{years[-1]}",
            seed=seed,
            n_mc=n_mc,
            params=p.__dict__ if hasattr(p, "__dict__") else str(p),
        )

    rng = np.random.default_rng(seed)
    rows = []
    strat_rows = []

    for r in range(n_mc):
        s = baseline_state(start_year=years[0], p=p)
        # Record initial state
        rr = relative_risk(s.pressure, s.offload_min, p)
        rows.append(
            {
                "rollout": r,
                "year": s.year,
                "pressure": s.pressure,
                "occupancy": s.occupancy,
                "offload_min": s.offload_min,
                "within4": s.within4,
                "cth_share_nominal": s.effective_cth_share,
                "cth_share_effective": s.effective_cth_share / (1.0 + s.efficiency_gap),
                "efficiency_gap": s.efficiency_gap,
                "discharge_delay": s.discharge_delay,
                "political_capital": s.political_capital,
                "rr_proxy": rr,
            }
        )
        # re-seed each rollout deterministically off the main RNG
        sub = np.random.default_rng(rng.integers(1, 2**32 - 1))
        for _ in years[1:]:
            strategies = decide_strategies(s, p, sub)
            # record strategies
            for g, lab in strategies.items():
                strat_rows.append({"rollout": r, "year": s.year, "game": g, "strategy": lab})
            s = step(s, p, strategies, sub)
            rr = relative_risk(s.pressure, s.offload_min, p)
            rows.append(
                {
                    "rollout": r,
                    "year": s.year,
                    "pressure": s.pressure,
                    "occupancy": s.occupancy,
                    "offload_min": s.offload_min,
                    "within4": s.within4,
                    "cth_share_nominal": s.effective_cth_share,
                    "cth_share_effective": s.effective_cth_share / (1.0 + s.efficiency_gap),
                    "efficiency_gap": s.efficiency_gap,
                    "discharge_delay": s.discharge_delay,
                    "political_capital": s.political_capital,
                    "rr_proxy": rr,
                }
            )

    df = pd.DataFrame(rows)
    strat = pd.DataFrame(strat_rows)

    # Aggregate trajectories
    agg = (
        df.groupby("year")
        .agg(
            pressure_mean=("pressure", "mean"),
            pressure_p10=("pressure", lambda x: x.quantile(0.10)),
            pressure_p90=("pressure", lambda x: x.quantile(0.90)),
            occupancy_mean=("occupancy", "mean"),
            occupancy_p10=("occupancy", lambda x: x.quantile(0.10)),
            occupancy_p90=("occupancy", lambda x: x.quantile(0.90)),
            offload_mean=("offload_min", "mean"),
            offload_p10=("offload_min", lambda x: x.quantile(0.10)),
            offload_p90=("offload_min", lambda x: x.quantile(0.90)),
            within4_mean=("within4", "mean"),
            within4_p10=("within4", lambda x: x.quantile(0.10)),
            within4_p90=("within4", lambda x: x.quantile(0.90)),
            rr_mean=("rr_proxy", "mean"),
            rr_p10=("rr_proxy", lambda x: x.quantile(0.10)),
            rr_p90=("rr_proxy", lambda x: x.quantile(0.90)),
            cth_nominal_mean=("cth_share_nominal", "mean"),
            cth_effective_mean=("cth_share_effective", "mean"),
            effgap_mean=("efficiency_gap", "mean"),
            discharge_mean=("discharge_delay", "mean"),
            polcap_mean=("political_capital", "mean"),
        )
        .reset_index()
    )

    # Strategy frequencies (per year and game)
    if not strat.empty:
        freq = strat.groupby(["year", "game", "strategy"]).size().reset_index(name="n")
        freq["share"] = freq["n"] / freq.groupby(["year", "game"])["n"].transform("sum")
    else:
        freq = pd.DataFrame(columns=["year", "game", "strategy", "n", "share"])

    if recorder:
        recorder.end_experiment()

    return agg, freq


def sensitivity_sample(base: Params, n: int, seed: int = 1234) -> pd.DataFrame:
    """
    Random sample over key parameters for global sensitivity (simple, dependency-free).
    """
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(n):
        p = replace(
            base,
            rurality_weight=float(clamp(rng.normal(base.rurality_weight, 0.08), 0.05, 0.70)),
            cost_shifting_intensity=float(
                clamp(rng.normal(base.cost_shifting_intensity, 0.10), 0.05, 0.80)
            ),
            fragmentation_index=float(
                clamp(rng.normal(base.fragmentation_index, 0.12), 0.60, 1.50)
            ),
            discharge_delay_base=float(
                clamp(rng.normal(base.discharge_delay_base, 0.10), 0.70, 1.30)
            ),
            admin_burden_weight=float(
                clamp(rng.normal(base.admin_burden_weight, 0.08), 0.05, 0.60)
            ),
            political_salience=float(clamp(rng.normal(base.political_salience, 0.12), 0.05, 0.80)),
            rr_beta_pressure=float(clamp(rng.normal(base.rr_beta_pressure, 0.08), 0.10, 0.70)),
            rr_beta_offload=float(clamp(rng.normal(base.rr_beta_offload, 0.005), 0.002, 0.040)),
        )
        samples.append(p)
    # convert to df
    rows = []
    for i, p in enumerate(samples):
        rows.append({k: getattr(p, k) for k in Params().__dict__})
        rows[-1]["sample_id"] = i
    return pd.DataFrame(rows)


def summarise_outcome(agg: pd.DataFrame) -> dict[str, float]:
    # take 2030 values as headline
    last = agg.sort_values("year").iloc[-1]
    return {
        "pressure_2030": float(last["pressure_mean"]),
        "within4_2030": float(last["within4_mean"]),
        "offload_2030": float(last["offload_mean"]),
        "rr_2030": float(last["rr_mean"]),
        "effshare_nominal_2030": float(last["cth_nominal_mean"]),
        "effshare_effective_2030": float(last["cth_effective_mean"]),
        "effgap_2030": float(last["effgap_mean"]),
    }
