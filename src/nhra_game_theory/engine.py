"""
NHRA stylised hybrid model (v26) — Cognitive Digital Twin Engine

This version implements monthly time-steps, explicit queuing dynamics,
hysteretic crisis states, and a modular agent-based decision layer.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from nhra_game_theory.agents.base import HeuristicAgent
from nhra_game_theory.rules import (
    HardCapRule,
    ProportionalAuditRule,
    SoftCapRule,
    ThresholdAuditRule,
)

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


def mm_s_queue_wait(arrival_rate: float, service_rate: float, servers: float) -> float:
    """Simplified approximation of M/M/s wait time.

    Calculates the expected wait time in minutes using a Kingman-like approximation
    for a multi-server queue.

    Args:
        arrival_rate: The rate of arrivals (e.g., patients per hour).
        service_rate: The service rate per server (e.g., patients per hour).
        servers: The number of available servers (effective capacity).

    Returns:
        The estimated wait time in minutes, clamped between 5 and 1440.
    """
    utilization = arrival_rate / max(1e-9, (service_rate * servers))
    if utilization >= 1.0:
        return 1440.0  # Cap at 24 hours
    wait = (utilization ** (math.sqrt(2 * (servers + 1)) - 1)) / (servers * (1 - utilization))
    return clamp(wait * 60.0, 5.0, 1440.0)


def within4_from_pressure(pidx: float) -> float:
    """Calibrate so pidx=1 -> ~0.53"""
    return clamp(0.80 - 0.45 * logistic((pidx - 1.0) / 0.20), 0.05, 0.85)


def nep_series(years: list[int], p: Params) -> pd.DataFrame:
    """Return an illustrative NEP series.

    Generates a time-series DataFrame of National Efficient Price (NEP) values
    based on the initial NEP and annual growth rate defined in the parameters.

    Args:
        years: A list of years to generate data for.
        p: The simulation parameters containing growth assumptions.

    Returns:
        A DataFrame with columns `year`, `nep_per_nwau`, `representative_nwau`,
        and `efficient_payment`.
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
    """Return an illustrative input-cost series (index units per NWAU)."""
    cost = float(p.input_cost_per_nwau_start)
    rows = []
    for i, y in enumerate(years):
        if i > 0:
            cost *= 1.0 + float(p.input_cost_annual_growth)
        rows.append({"year": int(y), "input_cost_per_nwau": float(cost)})
    return pd.DataFrame(rows)


def nep_vs_cost_series(years: list[int], p: Params) -> pd.DataFrame:
    """Combine NEP and input-cost indices."""
    nep_df = nep_series(years, p)[["year", "nep_per_nwau"]]
    cost_df = input_cost_series(years, p)
    out = nep_df.merge(cost_df, on="year", how="inner")
    out["nep_to_cost_ratio_index"] = out["nep_per_nwau"] / out["input_cost_per_nwau"]
    out["cost_over_nep_index"] = out["input_cost_per_nwau"] / out["nep_per_nwau"]
    return out


def pressure_index(occupancy: float, offload_min: float, discharge_delay: float) -> float:
    """Legacy pressure index for compatibility."""
    occ_term = logistic((occupancy - 0.88) / 0.03)
    off_term = logistic((offload_min - 20.0) / 8.0)
    return 0.8 + 0.8 * (0.55 * occ_term + 0.45 * off_term) * discharge_delay


# ----------------------------
# Parameters and state
# ----------------------------


class SystemMode(Enum):
    NORMAL = "normal"
    STRESS = "stress"
    CRISIS = "crisis"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class Params:
    # Funding / valuation
    nep_to_cost_ratio_metro: float = 0.90
    nep_to_cost_ratio_regional: float = 0.83
    nep_to_cost_ratio_remote: float = 0.75
    rurality_weight: float = 0.35
    remote_weight: float = 0.07
    nominal_cth_share_target: float = 0.45
    effective_cth_share_base: float = 0.38
    cap_growth: float = 0.065
    has_cumulative_cap: bool = False

    # Pricing & Costs
    nep_annual_growth: float = 0.03
    input_cost_annual_growth: float = 0.04
    nep_per_nwau_start: float = 1.0
    input_cost_per_nwau_start: float = 1.0
    representative_nwau: float = 1.0

    # System dynamics
    demand_base: float = 1.00
    avoidable_ed_share: float = 0.18
    discharge_delay_base: float = 1.00
    bed_capacity_index: float = 1.00
    capacity_lag: float = 0.15

    # Couplings
    cost_shifting_intensity: float = 0.35
    fragmentation_index: float = 1.00
    audit_pressure: float = 0.50
    admin_burden_weight: float = 0.25

    # Mapping
    occupancy_base: float = 0.88
    offload_base_min: float = 18.0
    within4_base: float = 0.53
    rr_beta_pressure: float = 0.35
    rr_beta_offload: float = 0.015
    offload_threshold_min: float = 20.0

    # Behavioural
    tau: float = 0.25
    bargaining_cost: float = 0.12
    political_salience: float = 0.30
    use_equilibrium_bargaining: bool = False
    use_quantal_response: bool = False
    qre_lambda: float = 4.0
    use_burden_feedback: bool = False
    burden_to_throughput_beta: float = 0.06
    noise_sd: float = 0.03

    # Orchestration & Logic
    orchestration_mode: str = "simultaneous"
    isolated_game: str | None = None
    cap_rule_type: str = "hard"
    audit_rule_type: str = "proportional"
    use_stage_game_equilibria: bool = True
    equilibrium_selection_rule: str = "payoff_dominant"

    # Data
    economic_spine: pd.DataFrame | None = None


@dataclass(frozen=True)
class State:
    year: int
    month: int
    pressure: float
    occupancy: float
    offload_min: float
    within4: float
    effective_cth_share: float
    efficiency_gap: float
    discharge_delay: float
    political_capital: float
    system_mode: SystemMode = SystemMode.NORMAL
    target_capacity: float = 1.0
    current_capacity: float = 1.0
    equity_index: float = 1.0
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    coding_intensity: float = 1.0


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    if p is None:
        p = Params()
    metro_ratio = p.nep_to_cost_ratio_metro
    reg_ratio = p.nep_to_cost_ratio_regional
    rem_ratio = p.nep_to_cost_ratio_remote
    ratio = (
        (1 - p.rurality_weight) * metro_ratio
        + (p.rurality_weight - p.remote_weight) * reg_ratio
        + p.remote_weight * rem_ratio
    )
    efficiency_gap = 1.0 / max(1e-9, ratio) - 1.0
    return State(
        year=start_year,
        month=1,
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        effective_cth_share=p.effective_cth_share_base * (1.0 + efficiency_gap),
        efficiency_gap=efficiency_gap,
        discharge_delay=p.discharge_delay_base,
        political_capital=1.0,
        system_mode=SystemMode.NORMAL,
        target_capacity=p.bed_capacity_index,
        current_capacity=p.bed_capacity_index,
        equity_index=1.0,
        reconciliation_balance=0.0,
        bailout_expectation=0.0,
        coding_intensity=1.0,
    )


# ----------------------------
# Transitions
# ----------------------------


def get_cap_rule(params: Params):
    return SoftCapRule() if params.cap_rule_type == "soft" else HardCapRule()


def get_audit_rule(params: Params):
    return (
        ThresholdAuditRule() if params.audit_rule_type == "threshold" else ProportionalAuditRule()
    )


def demand_step(s: State, p: Params, strategies: dict[str, Any], rng: np.random.Generator) -> float:
    demand = p.demand_base * (1.04 if strategies.get("SHIFT") == "S" else 0.96)
    demand += rng.normal(0, 0.02)
    return max(0.5, demand)


def policy_step(
    s: State, p: Params, strategies: dict[str, Any], month_growth_factor: float
) -> tuple[float, float, float]:
    if (
        p.economic_spine is not None
        and s.year in p.economic_spine["year"].values
        and (s.year + 1) in p.economic_spine["year"].values
    ):
        row_curr = p.economic_spine[p.economic_spine["year"] == s.year].iloc[0]
        row_next = p.economic_spine[p.economic_spine["year"] == (s.year + 1)].iloc[0]
        drift_factor = (
            1.0 + ((row_next["wpi_health_index"] / row_curr["wpi_health_index"]) - 1.0) / 12.0
        ) / (1.0 + ((row_next["nep_per_nwau"] / row_curr["nep_per_nwau"]) - 1.0) / 12.0)
    else:
        drift_factor = (1.0 + p.input_cost_annual_growth / 12.0) / (
            1.0 + p.nep_annual_growth / 12.0
        )

    eff_gap = clamp((1.0 + s.efficiency_gap) * drift_factor - 1.0, 0.05, 0.60)
    if strategies.get("DEF") == "R":
        eff_gap *= 0.93**month_growth_factor
    else:
        eff_gap *= 1.03**month_growth_factor

    eff_share = s.effective_cth_share
    target = p.nominal_cth_share_target
    if strategies.get("BARG") == "A":
        eff_share += 0.25 * (target - eff_share) * month_growth_factor
        bailout = s.bailout_expectation + (0.05 * month_growth_factor if s.pressure > 1.2 else 0.0)
    else:
        eff_share += 0.10 * (target - eff_share) * month_growth_factor
        bailout = max(0.0, s.bailout_expectation - 0.02 * month_growth_factor)

    if s.system_mode == SystemMode.CRISIS:
        eff_share = clamp(eff_share + 0.01, 0.30, 0.55)
    return eff_gap, eff_share, bailout


def ops_step(
    s: State,
    p: Params,
    strategies: dict[str, Any],
    demand: float,
    month_growth_factor: float,
    rng: np.random.Generator,
) -> tuple[float, float, float, float, float, float, float]:
    """Execute the operational dynamics step.

    Updates operational metrics including discharge delay, capacity, occupancy,
    and pressure indices based on demand and strategic choices.

    Args:
        s: Current system state.
        p: System parameters.
        strategies: Dictionary of current agent strategies.
        demand: The realized demand for the current step.
        month_growth_factor: Scaling factor for monthly time-step (1/12).
        rng: Random number generator for stochasticity.

    Returns:
        A tuple containing:
        (discharge, capacity, wait_min, occ, off, pidx, w4)
    """
    discharge = s.discharge_delay
    aged_effect = 0.95 if strategies.get("AGED") == "C" else 1.02
    ndis_effect = 0.96 if strategies.get("NDIS") == "C" else 1.03
    discharge *= (aged_effect * ndis_effect) ** month_growth_factor
    if p.use_burden_feedback:
        discharge *= math.exp(
            p.burden_to_throughput_beta * max(0.0, s.pressure - 1.0) * month_growth_factor
        )
    discharge = clamp(discharge, 0.75, 1.50)

    capacity = s.current_capacity + p.capacity_lag * (s.target_capacity - s.current_capacity)
    wait_min = mm_s_queue_wait(demand, 1.0 / max(1e-9, discharge), capacity * 10.0)
    occ = clamp(s.occupancy + 0.015 * (demand - 1.0) + 0.035 * (discharge - 1.0), 0.78, 0.98)
    off = clamp(s.offload_min + 8.0 * (occ - 0.88) + rng.normal(0, 0.8), 5.0, 120.0)
    pidx = 0.8 + 0.2 * (wait_min / 60.0) + 0.5 * (occ - 0.8) / 0.1
    return discharge, capacity, wait_min, occ, off, pidx, within4_from_pressure(pidx)


def pay_step(
    s: State,
    p: Params,
    strategies: dict[str, Any],
    eff_share: float,
    month_growth_factor: float,
    rng: np.random.Generator,
) -> tuple[float, float, float, float]:
    coding = s.coding_intensity
    recon = s.reconciliation_balance
    pol_cap_hit = 0.0
    if strategies.get("CODING") == "U":
        coding += 0.02 * month_growth_factor
        if rng.random() < get_audit_rule(p).evaluate(s, p, coding):
            recon -= 0.05 * coding
            coding = 1.0
            pol_cap_hit = 0.1
    else:
        coding = max(1.0, coding - 0.01 * month_growth_factor)
    return clamp(eff_share * coding, 0.30, 0.60), coding, recon, pol_cap_hit


def update_system_mode(s: State, p: Params) -> SystemMode:
    if s.system_mode == SystemMode.NORMAL and s.pressure > 1.25:
        return SystemMode.STRESS
    if s.system_mode == SystemMode.STRESS:
        if s.pressure > 1.5:
            return SystemMode.CRISIS
        if s.pressure < 1.05:
            return SystemMode.NORMAL
    if s.system_mode == SystemMode.CRISIS and s.pressure < 1.3:
        return SystemMode.RECOVERY
    if s.system_mode == SystemMode.RECOVERY:
        if s.pressure < 1.1:
            return SystemMode.NORMAL
        if s.pressure > 1.4:
            return SystemMode.CRISIS
    return s.system_mode


def step(s: State, p: Params, strategies: dict[str, Any], rng: np.random.Generator) -> State:
    """Advance the simulation by one month.

    Integrates demand, policy, operational, and payment dynamics to produce the
    next system state. Also updates political capital and equity indices.

    Args:
        s: Current state.
        p: System parameters.
        strategies: Dictionary of chosen strategies for this step.
        rng: Random number generator.

    Returns:
        The new `State` object for the simulation.
    """
    mgf = 1.0 / 12.0
    demand = demand_step(s, p, strategies, rng)
    eff_gap, eff_share, bailout = policy_step(s, p, strategies, mgf)
    discharge, capacity, wait_min, occ, off, pidx, w4 = ops_step(s, p, strategies, demand, mgf, rng)
    final_share, coding, recon, pol_cap_hit = pay_step(s, p, strategies, eff_share, mgf, rng)

    sig_quality = strategies.get("SIGNAL_QUALITY", 1.0)
    pol_cap = clamp(
        s.political_capital
        - pol_cap_hit
        - (1.0 - sig_quality) * 0.2 * mgf
        + (0.05 if strategies.get("BARG") == "A" else -0.10) * mgf
        - (0.05 * (wait_min / 240.0) if wait_min > 240 else 0.0),
        0.0,
        2.0,
    )

    equity = clamp(
        s.equity_index
        - (0.01 if strategies.get("DEF") == "E" else 0.0) * mgf
        - (0.02 if s.system_mode == SystemMode.CRISIS else 0.0) * mgf,
        0.5,
        1.5,
    )

    next_m, next_y = (s.month + 1, s.year) if s.month < 12 else (1, s.year + 1)
    return State(
        year=next_y,
        month=next_m,
        pressure=pidx,
        occupancy=occ,
        offload_min=off,
        within4=w4,
        effective_cth_share=final_share,
        efficiency_gap=eff_gap,
        discharge_delay=discharge,
        political_capital=pol_cap,
        system_mode=update_system_mode(s, p),
        target_capacity=s.target_capacity,
        current_capacity=capacity,
        equity_index=equity,
        reconciliation_balance=recon,
        bailout_expectation=bailout,
        coding_intensity=coding,
    )


# ----------------------------
# Legacy & Simulation
# ----------------------------


def decide_strategies(s: State, p: Params, rng: np.random.Generator) -> dict[str, Any]:
    return HeuristicAgent().decide(s, p, rng)


def relative_risk(pidx: float, offload_min: float, p: Params) -> float:
    return math.exp(p.rr_beta_pressure * max(0.0, pidx - 1.0)) * math.exp(
        p.rr_beta_offload * max(0.0, offload_min - p.offload_threshold_min)
    )


def run_hybrid(
    years: list[int],
    p: Params,
    seed: int = 123,
    n_mc: int = 300,
    recorder: Any | None = None,
    overrides: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute a hybrid simulation experiment with multiple Monte Carlo rollouts.

    Runs the simulation over the specified years, aggregating results across `n_mc`
    independent trajectories. Calculates standard deviations and percentiles for
    key metrics.

    Args:
        years: List of integer years to simulate (e.g., `[2025, 2026, ...]`).
        p: Base simulation parameters.
        seed: Random seed for reproducibility.
        n_mc: Number of Monte Carlo rollouts (iterations).
        recorder: Optional instrumentation object for tracking experiments.
        overrides: Optional dictionary of strategy overrides (e.g., forced "COOP").

    Returns:
        A tuple of two DataFrames:
        1. `agg`: Aggregated metrics per year (mean, std, p10, p90).
        2. `freq`: Frequency of strategy choices per game per year.
    """
    if recorder:
        recorder.start_experiment(
            experiment_name=f"hybrid_sim_{years[0]}_{years[-1]}",
            seed=seed,
            n_mc=n_mc,
            params=str(p),
        )
    rows, strat_rows, agent = [], [], HeuristicAgent()
    for r in range(n_mc):
        s, sub, end_year = (
            baseline_state(start_year=years[0], p=p),
            np.random.default_rng(np.random.default_rng(seed).integers(1, 2**32 - 1)),
            years[-1],
        )
        while s.year <= end_year:
            rr = relative_risk(s.pressure, s.offload_min, p)
            rows.append(
                {
                    "rollout": r,
                    "year": s.year,
                    "month": s.month,
                    "pressure": s.pressure,
                    "occupancy": s.occupancy,
                    "offload_min": s.offload_min,
                    "within4": s.within4,
                    "cth_share_nominal": s.effective_cth_share,
                    "cth_share_effective": s.effective_cth_share / (1.0 + s.efficiency_gap),
                    "efficiency_gap": s.efficiency_gap,
                    "discharge_delay": s.discharge_delay,
                    "political_capital": s.political_capital,
                    "system_mode": s.system_mode.value,
                    "equity_index": s.equity_index,
                    "rr_proxy": rr,
                }
            )

            strategies = agent.decide(s, p, sub)
            # Apply manual overrides if present
            if overrides:
                strategies.update(overrides)

            rat = strategies.get("RATIONALE", "")
            for g, lab in strategies.items():
                if g != "RATIONALE":
                    strat_rows.append(
                        {
                            "rollout": r,
                            "year": s.year,
                            "month": s.month,
                            "game": g,
                            "strategy": lab,
                            "rationale": rat,
                        }
                    )
            s = step(s, p, strategies, sub)
            wf = calculate_vfi_waterfall(s, p)
            rows[-1].update(
                {
                    "index_gap": wf["indexation_gap"],
                    "cap_gap": wf["cap_limit_gap"],
                    "audit_gap": wf["audit_clawback"],
                }
            )
            if s.year > end_year:
                break
    df, strat = pd.DataFrame(rows), pd.DataFrame(strat_rows)
    agg = (
        df.groupby("year")
        .agg(
            pressure_mean=("pressure", "mean"),
            pressure_std=("pressure", "std"),
            pressure_p10=("pressure", lambda x: x.quantile(0.10)),
            pressure_p90=("pressure", lambda x: x.quantile(0.90)),
            occupancy_mean=("occupancy", "mean"),
            occupancy_std=("occupancy", "std"),
            occupancy_p10=("occupancy", lambda x: x.quantile(0.10)),
            occupancy_p90=("occupancy", lambda x: x.quantile(0.90)),
            offload_mean=("offload_min", "mean"),
            offload_std=("offload_min", "std"),
            offload_p10=("offload_min", lambda x: x.quantile(0.10)),
            offload_p90=("offload_min", lambda x: x.quantile(0.90)),
            within4_mean=("within4", "mean"),
            within4_std=("within4", "std"),
            within4_p10=("within4", lambda x: x.quantile(0.10)),
            within4_p90=("within4", lambda x: x.quantile(0.90)),
            rr_mean=("rr_proxy", "mean"),
            rr_std=("rr_proxy", "std"),
            rr_p10=("rr_proxy", lambda x: x.quantile(0.10)),
            rr_p90=("rr_proxy", lambda x: x.quantile(0.90)),
            cth_nominal_mean=("cth_share_nominal", "mean"),
            cth_effective_mean=("cth_share_effective", "mean"),
            effgap_mean=("efficiency_gap", "mean"),
            discharge_mean=("discharge_delay", "mean"),
            polcap_mean=("political_capital", "mean"),
            equity_mean=("equity_index", "mean"),
            index_gap_mean=("index_gap", "mean"),
            cap_gap_mean=("cap_gap", "mean"),
            audit_gap_mean=("audit_gap", "mean"),
        )
        .reset_index()
    )

    # Calculate SEM (Standard Error of Mean) = std / sqrt(n)
    for m in ["pressure", "occupancy", "offload", "within4", "rr"]:
        agg[f"{m}_sem"] = agg[f"{m}_std"] / math.sqrt(n_mc)
    if not strat.empty:
        freq = strat.groupby(["year", "game", "strategy"]).size().reset_index(name="n")
        freq["share"] = freq["n"] / freq.groupby(["year", "game"])["n"].transform("sum")
    else:
        freq = pd.DataFrame(columns=["year", "game", "strategy", "n", "share"])
    if recorder:
        recorder.end_experiment()
    return agg, freq


def calculate_vfi_waterfall(s: State, p: Params) -> dict[str, float]:
    nominal = p.nominal_cth_share_target
    return {
        "nominal_share": nominal,
        "indexation_gap": s.efficiency_gap * nominal,
        "cap_limit_gap": max(0.0, (s.pressure - 1.1) * 0.05) * nominal,
        "audit_clawback": abs(s.reconciliation_balance) if s.reconciliation_balance < 0 else 0.0,
        "effective_share": nominal
        - (s.efficiency_gap * nominal)
        - (max(0.0, (s.pressure - 1.1) * 0.05) * nominal)
        - (abs(s.reconciliation_balance) if s.reconciliation_balance < 0 else 0.0),
    }


def apply_intervention(p: Params, name: str) -> Params:
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


def summarise_outcome(agg: pd.DataFrame) -> dict[str, float]:
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
