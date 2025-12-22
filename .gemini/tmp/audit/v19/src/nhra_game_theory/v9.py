"""
NHRA stylised hybrid model (v9).

v9 explicitly represents *macro valuation drift* by evolving:
- NEP ($/NWAU) over time (index units by default), and
- an input-cost index over time.

The total "efficiency gap" used in funding-risk calculations is the sum of:
- a macro component driven by NEP-vs-cost drift, and
- a micro component driven by strategic behaviour ("games").

This is a mechanism model, not a forecasting model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

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


def clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))


@dataclass(frozen=True)
class Params:
    # --- Funding / bargaining ---
    nominal_cth_share_target: float = 0.45
    effective_cth_share_base: float = 0.41

    # --- Political / narrative ---
    political_salience: float = 0.30

    # --- Growth / caps / drift ---
    cap_growth: float = 0.065
    has_cumulative_cap: bool = True

    # --- System levers / externalities ---
    cost_shifting_intensity: float = 0.55
    fragmentation_index: float = 1.00
    avoidable_ed_share: float = 0.16
    admin_burden_weight: float = 1.00
    audit_pressure: float = 1.00
    discharge_delay_base: float = 1.05  # >1 indicates slower discharge

    # --- NEP / cost drift ---
    nep_per_nwau_start: float = 1.0
    nep_annual_growth: float = 0.03
    input_cost_index_start: float = 1.0
    input_cost_annual_growth: float = 0.04
    macro_drift_weight: float = 1.0  # 0 disables macro drift contribution

    # Baseline NEP-to-cost valuation ratios by rurality
    nep_to_cost_ratio_metro: float = 0.96
    nep_to_cost_ratio_regional: float = 0.90
    nep_to_cost_ratio_remote: float = 0.86
    rurality_weight: float = 0.32
    remote_weight: float = 0.06

    # --- Performance mapping ---
    offload_threshold_min: float = 25.0

    # --- Relative risk proxy parameters ---
    rr_beta_pressure: float = 0.55
    rr_beta_offload: float = 0.015
    rr_beta_effgap: float = 0.90
    rr_beta_discharge: float = 0.45
    rr_base: float = 1.0

    # --- Strategy selection & stochasticity ---
    equilibrium_selection_rule: str = "payoff_dominant"
    noise_sd: float = 0.02


@dataclass(frozen=True)
class State:
    year: int
    pressure: float
    occupancy: float
    offload_min: float
    within4: float
    effective_cth_share: float

    nep_per_nwau: float
    input_cost_index: float

    efficiency_gap_micro: float
    efficiency_gap: float  # total

    discharge_delay: float


def _base_ratio(p: Params) -> float:
    return (
        (1 - p.rurality_weight) * p.nep_to_cost_ratio_metro
        + (p.rurality_weight - p.remote_weight) * p.nep_to_cost_ratio_regional
        + p.remote_weight * p.nep_to_cost_ratio_remote
    )


def _macro_gap(nep: float, cost: float, p: Params) -> float:
    ratio = _base_ratio(p)
    g = (cost / max(1e-9, ratio * nep) - 1.0) * float(p.macro_drift_weight)
    return float(max(0.0, g))


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    p = Params() if p is None else p
    nep = float(p.nep_per_nwau_start)
    cost = float(p.input_cost_index_start)
    micro = 0.0
    macro = _macro_gap(nep, cost, p)
    total = clamp(macro + micro, 0.0, 0.80)
    return State(
        year=int(start_year),
        pressure=1.0,
        occupancy=0.92,
        offload_min=22.0,
        within4=0.53,
        effective_cth_share=float(p.effective_cth_share_base),
        nep_per_nwau=nep,
        input_cost_index=cost,
        efficiency_gap_micro=micro,
        efficiency_gap=total,
        discharge_delay=float(p.discharge_delay_base),
    )


def relative_risk(
    offload_min: float, pressure: float, efficiency_gap: float, discharge_delay: float, p: Params
) -> float:
    """A stylised multiplicative risk proxy (RR), anchored at p.rr_base."""
    lin = (
        p.rr_beta_pressure * (pressure - 1.0)
        + p.rr_beta_offload * max(0.0, offload_min - p.offload_threshold_min)
        + p.rr_beta_effgap * efficiency_gap
        + p.rr_beta_discharge * max(0.0, discharge_delay - 1.0)
    )
    return float(p.rr_base * np.exp(lin))


def decide_strategies(s: State, p: Params, rng: np.random.Generator) -> dict[str, str]:
    """Select a strategy profile via stage-game equilibrium selection."""
    gp = GameParams(
        pressure=float(s.pressure),
        efficiency_gap=float(s.efficiency_gap),
        discharge_delay=float(s.discharge_delay),
        political_salience=float(p.political_salience),
        audit_pressure=float(p.audit_pressure),
    )

    def _pick(game) -> str:
        eqs = all_nash(game)
        sel = select_equilibrium(
            eqs, rule=p.equilibrium_selection_rule, u_row=game.u_row, u_col=game.u_col
        )
        # tie-break with small noise so the process is not perfectly deterministic
        row = np.asarray(sel.row) + rng.normal(0.0, 1e-6, size=len(sel.row))
        a = game.row_actions[int(np.argmax(row))]
        return str(a)

    return {
        "DEF": _pick(definition_game(gp)),
        "BARG": _pick(bargaining_game(gp)),
        "SHIFT": _pick(cost_shifting_game(gp)),
        "DISC": _pick(discharge_coordination_game(gp)),
        "GOV": _pick(governance_integration_game(gp)),
        "COMP": _pick(compliance_game(gp)),
    }


def step(s: State, p: Params, strategies: dict[str, str], rng: np.random.Generator) -> State:
    """Advance the system by one year."""
    # --- macro drift ---
    nep = float(s.nep_per_nwau) * (1.0 + float(p.nep_annual_growth))
    extra_cost_drift = 0.01 * max(0.0, float(s.pressure) - 1.0)
    cost = float(s.input_cost_index) * (1.0 + float(p.input_cost_annual_growth) + extra_cost_drift)

    macro = _macro_gap(nep, cost, p)

    # --- micro gap (definition / coding incentives) ---
    micro = float(s.efficiency_gap_micro)
    micro *= 0.93 if strategies["DEF"] == "R" else 1.03
    micro = clamp(micro, 0.0, 0.50)

    eff_gap = clamp(macro + micro, 0.0, 0.80)

    # --- bargaining affects nominal share ---
    eff_share = float(s.effective_cth_share)
    target = float(p.nominal_cth_share_target)
    eff_share = eff_share + (0.25 if strategies["BARG"] == "A" else 0.05) * (target - eff_share)
    eff_share = clamp(eff_share, 0.30, 0.50)

    # --- discharge coordination affects discharge delay ---
    discharge = float(s.discharge_delay)
    discharge *= 0.90 if strategies["DISC"] == "C" else 1.02
    discharge = clamp(discharge, 0.75, 1.50)

    # --- governance integration affects fragmentation and avoidable demand ---
    fragmentation = float(p.fragmentation_index) * (0.8 if strategies["GOV"] == "I" else 1.05)
    avoidable = float(p.avoidable_ed_share) * (0.85 if strategies["GOV"] == "I" else 1.02)
    fragmentation = clamp(fragmentation, 0.6, 1.4)
    avoidable = clamp(avoidable, 0.08, 0.25)

    # --- cost shifting and compliance raise pressure ---
    pressure = float(s.pressure)
    pressure *= 1.0 + (0.06 if strategies["SHIFT"] == "S" else 0.02) * float(
        p.cost_shifting_intensity
    )

    admin = float(p.admin_burden_weight) * (1.10 if strategies["COMP"] == "H" else 0.98)
    admin = clamp(admin, 0.7, 1.4)
    pressure *= 1.0 + 0.02 * (admin - 1.0)

    # --- cap effect (stylised) ---
    demand_growth = (
        0.05
        + 0.03 * (pressure - 1.0)
        + 0.02 * (discharge - 1.0)
        + 0.02 * (avoidable - p.avoidable_ed_share)
    )
    if demand_growth > float(p.cap_growth):
        pressure *= (1.01 if p.has_cumulative_cap else 1.02) + (
            0.25 if p.has_cumulative_cap else 0.40
        ) * (demand_growth - p.cap_growth)

    # --- occupancy, offload, within-4 ---
    occupancy = float(s.occupancy)
    occupancy += 0.03 * (discharge - 1.0) + 0.02 * (pressure - 1.0)
    occupancy = clamp(occupancy, 0.82, 0.995)

    offload = float(s.offload_min)
    offload += 12.0 * (occupancy - 0.90) + 9.0 * (pressure - 1.0)
    offload = clamp(offload, 8.0, 120.0)

    within4 = float(s.within4)
    within4 -= 0.0025 * max(0.0, offload - float(p.offload_threshold_min))
    within4 -= 0.30 * max(0.0, occupancy - 0.92)
    within4 = clamp(within4, 0.15, 0.85)

    # small noise
    noise = float(rng.normal(0.0, float(p.noise_sd)))
    pressure = clamp(pressure * (1.0 + noise), 0.75, 1.80)
    within4 = clamp(within4 * (1.0 - 0.15 * noise), 0.15, 0.85)

    return State(
        year=int(s.year + 1),
        pressure=float(pressure),
        occupancy=float(occupancy),
        offload_min=float(offload),
        within4=float(within4),
        effective_cth_share=float(eff_share),
        nep_per_nwau=float(nep),
        input_cost_index=float(cost),
        efficiency_gap_micro=float(micro),
        efficiency_gap=float(eff_gap),
        discharge_delay=float(discharge),
    )


def run_hybrid(
    years: list[int], p: Params, seed: int = 0, n_mc: int = 500
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(int(seed))
    rows = []
    strat_rows = []

    for r in range(int(n_mc)):
        s = baseline_state(start_year=int(years[0]), p=p)
        for _y in years:
            # record current year state
            rr = relative_risk(s.offload_min, s.pressure, s.efficiency_gap, s.discharge_delay, p)
            rows.append(
                {
                    "rollout": r,
                    "year": s.year,
                    "pressure": s.pressure,
                    "occupancy": s.occupancy,
                    "offload_min": s.offload_min,
                    "within4": s.within4,
                    "nep_per_nwau": s.nep_per_nwau,
                    "input_cost_index": s.input_cost_index,
                    "efficiency_gap_micro": s.efficiency_gap_micro,
                    "efficiency_gap_macro": max(0.0, s.efficiency_gap - s.efficiency_gap_micro),
                    "cth_share_nominal": s.effective_cth_share,
                    "cth_share_effective": s.effective_cth_share / (1.0 + s.efficiency_gap),
                    "efficiency_gap": s.efficiency_gap,
                    "discharge_delay": s.discharge_delay,
                    "rr_proxy": rr,
                }
            )

            strategies = decide_strategies(s, p, rng)
            strat_rows.append({"rollout": r, "year": s.year, **strategies})
            s = step(s, p, strategies, rng)

    df = pd.DataFrame(rows)
    agg = (
        df.groupby("year")
        .agg(
            pressure_mean=("pressure", "mean"),
            occupancy_mean=("occupancy", "mean"),
            offload_mean=("offload_min", "mean"),
            within4_mean=("within4", "mean"),
            rr_mean=("rr_proxy", "mean"),
            cth_nominal_mean=("cth_share_nominal", "mean"),
            cth_effective_mean=("cth_share_effective", "mean"),
            effgap_mean=("efficiency_gap", "mean"),
            discharge_mean=("discharge_delay", "mean"),
            nep_mean=("nep_per_nwau", "mean"),
            cost_mean=("input_cost_index", "mean"),
            effgap_micro_mean=("efficiency_gap_micro", "mean"),
            effgap_macro_mean=("efficiency_gap_macro", "mean"),
        )
        .reset_index()
    )

    sf = pd.DataFrame(strat_rows)
    # frequency of each action per year and game
    freq = []
    for game in ["DEF", "BARG", "SHIFT", "DISC", "GOV", "COMP"]:
        f = sf.groupby(["year", game]).size().reset_index(name="n")
        tot = f.groupby("year")["n"].transform("sum")
        f["freq"] = f["n"] / tot
        f["game"] = game
        f = f.rename(columns={game: "action"})
        freq.append(f[["year", "game", "action", "freq"]])
    freq_df = pd.concat(freq, ignore_index=True)

    return agg, freq_df


def nep_cost_series(years: list[int], p: Params) -> pd.DataFrame:
    nep = float(p.nep_per_nwau_start)
    cost = float(p.input_cost_index_start)
    rows = []
    for i, y in enumerate(years):
        if i > 0:
            nep *= 1.0 + float(p.nep_annual_growth)
            cost *= 1.0 + float(p.input_cost_annual_growth)
        rows.append(
            {
                "year": int(y),
                "nep_per_nwau": float(nep),
                "input_cost_index": float(cost),
                "nep_to_cost_index": float(nep / max(1e-9, cost)),
            }
        )
    return pd.DataFrame(rows)


def apply_intervention(p: Params, name: str) -> Params:
    # Governance / integration
    if name in {"pooled_funding"}:
        return replace(
            p, cost_shifting_intensity=clamp(p.cost_shifting_intensity * 0.80, 0.05, 1.0)
        )
    if name in {"ucc_integration"}:
        return replace(
            p,
            fragmentation_index=clamp(p.fragmentation_index * 0.85, 0.6, 1.4),
            avoidable_ed_share=clamp(p.avoidable_ed_share * 0.90, 0.08, 0.25),
        )
    if name in {"aged_ndis_capacity"}:
        return replace(p, discharge_delay_base=clamp(p.discharge_delay_base * 0.93, 0.75, 1.50))
    if name in {"cumulative_cap"}:
        return replace(p, has_cumulative_cap=True)

    # Macro alignment
    if name in {"nep_realism"}:
        return replace(
            p,
            nep_to_cost_ratio_metro=clamp(p.nep_to_cost_ratio_metro + 0.01, 0.80, 1.05),
            nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.02, 0.75, 1.05),
            nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.03, 0.70, 1.05),
        )
    if name in {"nep_uplift", "nep_growth", "ihacpa_indexation"}:
        return replace(p, nep_annual_growth=clamp(p.nep_annual_growth + 0.01, 0.0, 0.08))
    if name in {"input_cost_containment", "wage_compact"}:
        return replace(
            p, input_cost_annual_growth=clamp(p.input_cost_annual_growth - 0.01, 0.0, 0.10)
        )

    raise ValueError(f"Unknown intervention: {name}")


def apply_intervention_partial(base: Params, name: str, strength: float = 0.5) -> Params:
    """Blend base parameters towards a fully-applied intervention."""
    full = apply_intervention(base, name)
    s = float(clamp(strength, 0.0, 1.0))
    return replace(
        base,
        cost_shifting_intensity=base.cost_shifting_intensity
        + s * (full.cost_shifting_intensity - base.cost_shifting_intensity),
        fragmentation_index=base.fragmentation_index
        + s * (full.fragmentation_index - base.fragmentation_index),
        avoidable_ed_share=base.avoidable_ed_share
        + s * (full.avoidable_ed_share - base.avoidable_ed_share),
        discharge_delay_base=base.discharge_delay_base
        + s * (full.discharge_delay_base - base.discharge_delay_base),
        has_cumulative_cap=full.has_cumulative_cap if s > 0 else base.has_cumulative_cap,
        nep_to_cost_ratio_metro=base.nep_to_cost_ratio_metro
        + s * (full.nep_to_cost_ratio_metro - base.nep_to_cost_ratio_metro),
        nep_to_cost_ratio_regional=base.nep_to_cost_ratio_regional
        + s * (full.nep_to_cost_ratio_regional - base.nep_to_cost_ratio_regional),
        nep_to_cost_ratio_remote=base.nep_to_cost_ratio_remote
        + s * (full.nep_to_cost_ratio_remote - base.nep_to_cost_ratio_remote),
        nep_annual_growth=base.nep_annual_growth
        + s * (full.nep_annual_growth - base.nep_annual_growth),
        input_cost_annual_growth=base.input_cost_annual_growth
        + s * (full.input_cost_annual_growth - base.input_cost_annual_growth),
    )
