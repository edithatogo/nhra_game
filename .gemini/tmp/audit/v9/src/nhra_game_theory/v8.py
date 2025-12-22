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

from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Iterable, Optional
import math
import numpy as np
from numpy.typing import NDArray
from typing import Any, Mapping, cast

import pandas as pd


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
    remote_weight: float = 0.07    # subset weight in remote

    nominal_cth_share_target: float = 0.45
    effective_cth_share_base: float = 0.38

    cap_growth: float = 0.065  # "hard cap" annual
    has_cumulative_cap: bool = False

    # System dynamics
    demand_base: float = 1.00
    avoidable_ed_share: float = 0.18
    discharge_delay_base: float = 1.00  # multiplier
    bed_capacity_index: float = 1.00    # 1.0 baseline

    # Couplings
    cost_shifting_intensity: float = 0.35  # VFI spillover strength
    fragmentation_index: float = 1.00      # UCC/primary care integration etc
    audit_pressure: float = 0.50           # compliance scrutiny baseline
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

    # Randomness
    noise_sd: float = 0.03


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


def baseline_state(start_year: int = 2025, p: Params = Params()) -> State:
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

def decide_strategies(s: State, p: Params, rng: np.random.Generator) -> Dict[str, str]:
    """
    Returns a minimal strategy label for each game node.
    Labels are intentionally short to support diagrams.
    """
    noise = rng.normal(0, p.noise_sd)

    # Bargaining: offer basis (E=efficient-price basis, A=actual-cost recognition)
    # As pressure rises, incentive to concede increases, but political salience pushes to "E"
    u_E = +0.25 - 0.35 * (s.pressure - 1.0) + 0.20 * p.political_salience + noise
    u_A = -0.05 + 0.45 * (s.pressure - 1.0) - 0.10 * p.political_salience - noise
    prob = softmax(np.array([u_E, u_A]), tau=p.tau)
    barg = "E" if rng.random() < prob[0] else "A"

    # Definition: indexation realism (S=strict NEP, R=realistic indexation)
    u_S = +0.18 + 0.15 * p.audit_pressure - 0.20 * (s.pressure - 1.0) + noise
    u_R = -0.02 - 0.10 * p.audit_pressure + 0.25 * (s.pressure - 1.0) - noise
    prob = softmax(np.array([u_S, u_R]), tau=p.tau)
    defin = "S" if rng.random() < prob[0] else "R"

    # Cost shifting: upstream invest (I) vs hold (H) by Commonwealth; and State mitigations (M) vs accept (A)
    # We compress into one label driven by intensity & pressure.
    u_H = +0.12 + 0.15 * p.cost_shifting_intensity - 0.30 * (s.pressure - 1.0) + noise
    u_I = -0.05 - 0.15 * p.cost_shifting_intensity + 0.35 * (s.pressure - 1.0) - noise
    prob = softmax(np.array([u_H, u_I]), tau=p.tau)
    shift = "H" if rng.random() < prob[0] else "I"

    # Discharge: capacity add in aged/NDIS/community (C) vs status quo (Q)
    u_Q = +0.20 - 0.40 * (s.pressure - 1.0) + noise
    u_C = -0.05 + 0.50 * (s.pressure - 1.0) - noise
    prob = softmax(np.array([u_Q, u_C]), tau=p.tau)
    disc = "Q" if rng.random() < prob[0] else "C"

    # Integration: silo (S) vs integrate (I) (eg UCCs with LHN governance + digital handover)
    u_S = +0.15 + 0.25 * p.political_salience - 0.25 * (s.pressure - 1.0) + noise
    u_I = -0.02 - 0.15 * p.political_salience + 0.30 * (s.pressure - 1.0) - noise
    prob = softmax(np.array([u_S, u_I]), tau=p.tau)
    gov = "S" if rng.random() < prob[0] else "I"

    # Compliance: tighten (T) vs lighten (L) audit posture
    u_T = +0.20 + 0.30 * (s.pressure - 1.0) + 0.10 * p.audit_pressure + noise
    u_L = -0.05 - 0.25 * (s.pressure - 1.0) - 0.05 * p.audit_pressure - noise
    prob = softmax(np.array([u_T, u_L]), tau=p.tau)
    comp = "T" if rng.random() < prob[0] else "L"

    # Signalling: hard (H) vs cooperative (C)
    u_H = +0.22 + 0.30 * (s.pressure - 1.0) + 0.20 * p.political_salience + noise
    u_C = -0.05 - 0.20 * (s.pressure - 1.0) - 0.10 * p.political_salience - noise
    prob = softmax(np.array([u_H, u_C]), tau=p.tau)
    sig = "H" if rng.random() < prob[0] else "C"

    return {"BARG": barg, "DEF": defin, "SHIFT": shift, "DISC": disc, "GOV": gov, "COMP": comp, "SIGNAL": sig}


# ----------------------------
# System update
# ----------------------------

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


def step(s: State, p: Params, strategies: Dict[str, str], rng: np.random.Generator) -> State:
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


def run_hybrid(
    years: List[int],
    p: Params,
    seed: int = 123,
    n_mc: int = 300
) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
        rows.append({k: getattr(p, k) for k in Params().__dict__.keys()})
        rows[-1]["sample_id"] = i
    return pd.DataFrame(rows)


def summarise_outcome(agg: pd.DataFrame) -> Dict[str, float]:
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