"""
NHRA stylised hybrid model (v8)

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
from pydantic import BaseModel, ConfigDict, Field

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

class Params(BaseModel):
    # Funding / valuation
    nep_to_cost_ratio_metro: float = Field(default=0.90, ge=0.5, le=1.0)
    nep_to_cost_ratio_regional: float = Field(default=0.83, ge=0.5, le=1.0)
    nep_to_cost_ratio_remote: float = Field(default=0.75, ge=0.5, le=1.0)

    rurality_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    remote_weight: float = Field(default=0.07, ge=0.0, le=1.0)

    nominal_cth_share_target: float = Field(default=0.45, ge=0.3, le=0.6)
    effective_cth_share_base: float = Field(default=0.38, ge=0.2, le=0.6)

    cap_growth: float = Field(default=0.065, ge=0.0, le=0.2)
    has_cumulative_cap: bool = False
    use_equilibrium_bargaining: bool = False
    use_stage_game_equilibria: bool = True
    equilibrium_selection_rule: str = "payoff_dominant"

    # NEP scaffolding
    nep_per_nwau_start: float = 1.0
    nep_annual_growth: float = Field(default=0.03, ge=0.0, le=0.1)
    representative_nwau: float = 1.0

    # System dynamics
    demand_base: float = 1.00
    avoidable_ed_share: float = Field(default=0.18, ge=0.0, le=0.5)
    discharge_delay_base: float = Field(default=1.00, ge=0.1, le=3.0)
    bed_capacity_index: float = Field(default=1.00, ge=0.5, le=2.0)

    # Couplings
    cost_shifting_intensity: float = Field(default=0.35, ge=0.0, le=1.0)
    fragmentation_index: float = Field(default=1.00, ge=0.1, le=2.0)
    audit_pressure: float = Field(default=0.50, ge=0.0, le=1.0)
    admin_burden_weight: float = Field(default=0.25, ge=0.0, le=1.0)

    # Pressure mapping
    occupancy_base: float = Field(default=0.88, ge=0.5, le=1.0)
    offload_base_min: float = 18.0
    within4_base: float = Field(default=0.53, ge=0.0, le=1.0)

    # Risk proxy mapping
    rr_beta_pressure: float = 0.35
    rr_beta_offload: float = 0.015
    offload_threshold_min: float = 20.0

    # Behavioural weights
    tau: float = 0.25
    bargaining_cost: float = 0.12
    political_salience: float = Field(default=0.30, ge=0.0, le=1.0)

    # Randomness
    noise_sd: float = Field(default=0.03, ge=0.0, le=0.5)

    model_config = ConfigDict(frozen=True)


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


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    if p is None:
        p = Params()
    # Efficiency gap implied by rurality mix
    metro_ratio = p.nep_to_cost_ratio_metro
    reg_ratio = p.nep_to_cost_ratio_regional
    rem_ratio = p.nep_to_cost_ratio_remote
    ratio = (1 - p.rurality_weight) * metro_ratio + (p.rurality_weight - p.remote_weight) * reg_ratio + p.remote_weight * rem_ratio
    efficiency_gap = 1.0 / max(1e-9, ratio) - 1.0  # e.g., 0.20 means costs 20% above NEP

    return State(
        year=start_year,
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        effective_cth_share=p.effective_cth_share_base * (1.0 + efficiency_gap),  # store nominal share

        efficiency_gap=efficiency_gap,
        discharge_delay=p.discharge_delay_base,
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
        from nhra_game_theory.subgames.nash import all_nash, select_equilibrium

        gp = GameParams(
            pressure=float(s.pressure),
            efficiency_gap=float(s.efficiency_gap),
            discharge_delay=float(s.discharge_delay),
            political_salience=float(p.political_salience),
            audit_pressure=float(p.audit_pressure),
        )

        def _pick(game):
            eqs = all_nash(game)
            sel = select_equilibrium(eqs, rule=p.equilibrium_selection_rule, u_row=game.u_row, u_col=game.u_col)
            a = game.row_actions[int(np.argmax(sel.row))]
            return a

        DEF = _pick(definition_game(gp))
        BARG = _pick(bargaining_game(gp))
        SHIFT = _pick(cost_shifting_game(gp))
        DISC = _pick(discharge_coordination_game(gp))
        GOV = _pick(governance_integration_game(gp))
        COMP = _pick(compliance_game(gp))

    else:
        # Heuristic fallbacks (keep monotone relationships with pressure and efficiency gap)
        DEF = "R" if rng.random() < logistic(1.3 * (s.efficiency_gap - 0.25) + 0.9 * (s.pressure - 1.0)) else "E"
        BARG = "A" if rng.random() < logistic(0.6 * (1.2 - s.pressure) - 0.4 * p.political_salience) else "D"
        SHIFT = "I" if rng.random() < logistic(-1.1 * (s.pressure - 1.0) - 1.0 * s.efficiency_gap) else "S"
        DISC = "C" if rng.random() < logistic(-0.9 * (s.discharge_delay - 1.0) - 0.8 * (s.pressure - 1.0)) else "F"
        GOV = "I" if rng.random() < logistic(-0.8 * (s.pressure - 1.0) - 0.7 * p.political_salience) else "S"
        COMP = "T" if rng.random() < logistic(0.9 * p.audit_pressure - 0.7 * s.efficiency_gap) else "L"

    return {"SIGNAL": signal, "DEF": DEF, "BARG": BARG, "SHIFT": SHIFT, "DISC": DISC, "GOV": GOV, "COMP": COMP}
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
    eff_gap = s.efficiency_gap
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
        demand *= 1.02
        discharge *= 1.01

    # Compliance increases admin burden which slightly worsens pressure (less clinical time)
    admin_burden = (1.0 + p.admin_burden_weight * (1 if strategies["COMP"] == "T" else -0.25))
    admin_burden = clamp(admin_burden, 0.85, 1.35)

    # Occupancy update: demand ↑ and discharge delay ↑ increase occupancy; capacity index ↓ worsens
    occ = s.occupancy
    occ += 0.015 * (demand - 1.0) + 0.020 * (discharge - 1.0) + 0.008 * (admin_burden - 1.0)
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

    return State(
        year=s.year + 1,
        pressure=pidx,
        occupancy=occ,
        offload_min=off,
        within4=w4,
        effective_cth_share=eff_share,
        efficiency_gap=eff_gap,
        discharge_delay=discharge,
    )


# ----------------------------
# Scenarios & interventions
# ----------------------------

def apply_intervention(p: Params, name: str) -> Params:
    """
    Map policy interventions to parameter shifts.
    """
    name = name.lower().strip()
    if name in {"pooled_funding", "pooled"}:
        return replace(p, cost_shifting_intensity=clamp(p.cost_shifting_intensity * 0.75, 0.05, 0.60))
    if name in {"ucc_integration", "integration"}:
        return replace(p, fragmentation_index=clamp(p.fragmentation_index * 0.80, 0.60, 1.50))
    if name in {"nep_realism", "indexation"}:
        return replace(p,
                       nep_to_cost_ratio_metro=clamp(p.nep_to_cost_ratio_metro + 0.03, 0.6, 1.0),
                       nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.04, 0.6, 1.0),
                       nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.05, 0.6, 1.0),
                       )
    if name in {"aged_ndis_capacity", "discharge"}:
        return replace(p, discharge_delay_base=clamp(p.discharge_delay_base * 0.90, 0.6, 1.4))
    if name in {"middle_tier", "workforce"}:
        # reduces remote/regional cost penalties
        return replace(p,
                       nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.03, 0.6, 1.0),
                       nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.04, 0.6, 1.0),
                       )
    if name in {"cumulative_cap", "cap"}:
        return replace(p, has_cumulative_cap=True, cap_growth=0.070)
    if name in {"audit_relief"}:
        return replace(p, audit_pressure=clamp(p.audit_pressure * 0.70, 0.05, 1.0), admin_burden_weight=clamp(p.admin_burden_weight * 0.8, 0.05, 0.6))
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
            nep *= (1.0 + float(p.nep_annual_growth))
        rows.append(
            {
                "year": int(y),
                "nep_per_nwau": float(nep),
                "representative_nwau": float(p.representative_nwau),
                "efficient_payment": float(nep * float(p.representative_nwau)),
            }
        )
    return pd.DataFrame(rows)


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
        cost_shifting_intensity=base.cost_shifting_intensity + strength * (full.cost_shifting_intensity - base.cost_shifting_intensity),
        fragmentation_index=base.fragmentation_index + strength * (full.fragmentation_index - base.fragmentation_index),
        discharge_delay_base=base.discharge_delay_base + strength * (full.discharge_delay_base - base.discharge_delay_base),
        has_cumulative_cap=full.has_cumulative_cap if strength >= 0.5 else base.has_cumulative_cap,
        cap_growth=base.cap_growth + strength * (full.cap_growth - base.cap_growth),
        audit_pressure=base.audit_pressure + strength * (full.audit_pressure - base.audit_pressure),
        admin_burden_weight=base.admin_burden_weight + strength * (full.admin_burden_weight - base.admin_burden_weight),
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
            discharge_delay_base=float(np.clip(rng.normal(base.discharge_delay_base, 0.15), 0.5, 2.0)),
            cost_shifting_intensity=float(np.clip(rng.normal(base.cost_shifting_intensity, 0.08), 0.05, 0.8)),
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
    years: list[int],
    p: Params,
    seed: int = 123,
    n_mc: int = 300
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Monte Carlo rollouts of the hybrid model.
    Returns:
      - trajectories: mean + quantiles by year
      - strategy_freq: frequency table by year & game
    """
    rng = np.random.default_rng(seed)
    rows = []
    strat_rows = []

    for r in range(n_mc):
        s = baseline_state(start_year=years[0], p=p)
        # re-seed each rollout deterministically off the main RNG
        sub = np.random.default_rng(rng.integers(1, 2**32 - 1))
        for _ in years[1:]:
            strategies = decide_strategies(s, p, sub)
            # record strategies
            for g, lab in strategies.items():
                strat_rows.append({"rollout": r, "year": s.year, "game": g, "strategy": lab})
            s = step(s, p, strategies, sub)
            rr = relative_risk(s.pressure, s.offload_min, p)
            rows.append({
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
                "rr_proxy": rr,
            })

    df = pd.DataFrame(rows)
    strat = pd.DataFrame(strat_rows)

    # Aggregate trajectories
    agg = df.groupby("year").agg(
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
    ).reset_index()

    # Strategy frequencies (per year and game)
    freq = (
        strat.groupby(["year", "game", "strategy"])
        .size()
        .reset_index(name="n")
    )
    freq["share"] = freq["n"] / freq.groupby(["year", "game"])["n"].transform("sum")

    return agg, freq


def sensitivity_sample(base: Params, n: int, seed: int = 1234) -> pd.DataFrame:
    """
    Random sample over key parameters for global sensitivity (simple, dependency-free).
    """
    rng = np.random.default_rng(seed)
    samples = []
    for i in range(n):
        p = replace(
            base,
            rurality_weight=float(clamp(rng.normal(base.rurality_weight, 0.08), 0.05, 0.70)),
            cost_shifting_intensity=float(clamp(rng.normal(base.cost_shifting_intensity, 0.10), 0.05, 0.80)),
            fragmentation_index=float(clamp(rng.normal(base.fragmentation_index, 0.12), 0.60, 1.50)),
            discharge_delay_base=float(clamp(rng.normal(base.discharge_delay_base, 0.10), 0.70, 1.30)),
            admin_burden_weight=float(clamp(rng.normal(base.admin_burden_weight, 0.08), 0.05, 0.60)),
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
