from __future__ import annotations

import math
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from dataclasses import replace
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

from nhra_gt.agents.base import HeuristicAgent
from nhra_gt.rules import initialize_rules
from nhra_gt.subgames.queuing import PatientUtilityParams, solve_queuing_equilibrium_legacy

# ----------------------------
# Domain Models
# ----------------------------


class SystemMode(Enum):
    NORMAL = "normal"
    STRESS = "stress"
    CRISIS = "crisis"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class Params:
    """System-wide configuration parameters for the NHRA model."""

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
    expansion_lag: float = 0.10
    contraction_lag: float = 0.20
    adjustment_cost_beta: float = 5.0

    # Couplings
    cost_shifting_intensity: float = 0.35
    fragmentation_index: float = 1.00
    audit_pressure: float = 0.50
    admin_burden_weight: float = 0.25
    cannibalization_beta: float = 0.1

    # Boundary Shifting
    block_funding_base: float = 0.15
    shifting_friction: float = 0.05

    # Lags & Measurement
    signal_lag_months: int = 1
    claims_lag_months: int = 3

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

    # Patient choice / Queuing Game
    gp_out_of_pocket: float = 40.0
    gp_wait_time_min: float = 15.0
    patient_time_value_hour: float = 25.0

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

    # Modular Rules
    cap_rule: Any = dataclass_field(default_factory=lambda: None)
    audit_rule: Any = dataclass_field(default_factory=lambda: None)
    eligibility_rule: Any = dataclass_field(default_factory=lambda: None)
    reconciliation_rule: Any = dataclass_field(default_factory=lambda: None)

    # Data
    economic_spine: pd.DataFrame | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert params to a dictionary."""
        from dataclasses import asdict

        d = asdict(self)
        if self.economic_spine is not None:
            d["economic_spine"] = self.economic_spine.to_dict()
        else:
            d["economic_spine"] = None
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Params:
        """Create Params from a dictionary."""
        if d.get("economic_spine") is not None:
            d["economic_spine"] = pd.DataFrame(d["economic_spine"])
        return cls(**d)


@dataclass(frozen=True)
class LhnStateLegacy:
    """Granular state for a single LHN (Legacy)."""

    id: int
    pressure: float = 1.0
    occupancy: float = 0.88
    within4: float = 0.53
    offload_min: float = 18.0
    nwau_actual: float = 100.0
    nwau_reported: float = 100.0
    coding_intensity: float = 1.0
    target_capacity: float = 1.0
    current_capacity: float = 1.0
    discharge_delay: float = 1.0
    adjustment_costs: float = 0.0


@dataclass(frozen=True)
class JurisdictionStateLegacy:
    """Granular state for a single Jurisdiction (Legacy)."""

    id: int
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    political_capital: float = 1.0
    effective_cth_share: float = 0.38
    efficiency_gap: float = 0.10
    equity_index: float = 1.0
    total_block_revenue: float = 0.0
    lhns: list[LhnStateLegacy] = dataclass_field(default_factory=list)


@dataclass(frozen=True)
class State:
    year: int
    month: int
    pressure: float
    occupancy: float
    offload_min: float
    within4: float
    effective_cth_share: float = 0.38
    efficiency_gap: float = 0.10
    discharge_delay: float = 1.0
    political_capital: float = 1.0
    target_capacity: float = 1.0
    current_capacity: float = 1.0
    equity_index: float = 1.0
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    coding_intensity: float = 1.0
    reputation_score: float = 1.0
    system_mode: SystemMode = SystemMode.NORMAL
    workforce_pool: float = 1.0
    agreement_clock: int = 5

    # Hierarchical Entities
    jurisdictions: list[JurisdictionStateLegacy] = dataclass_field(default_factory=list)

    # Auditor Agent state
    auditor_suspicion: float = 0.0
    audit_pressure_active: float = 0.0
    adjustment_costs: float = 0.0

    # Lags & Measurement
    # Buffers store up to 12 months of history
    lag_buffer_pressure: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))
    lag_buffer_occupancy: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))
    lag_buffer_within4: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))
    lag_buffer_nwau: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))
    lag_buffer_efficiency_gap: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))
    lag_buffer_coding: np.ndarray = dataclass_field(default_factory=lambda: np.zeros(12))

    # Reported values (lagged) available to agents
    reported_pressure: float = 1.0
    reported_occupancy: float = 0.88
    reported_within4: float = 0.53
    reported_nwau: float = 0.0
    reported_efficiency_gap: float = 0.10
    reported_coding_intensity: float = 1.0

    # Stability Telemetry
    solver_n_equilibria: int = 1
    solver_residual: float = 0.0

    # Patient Choice
    prob_ed: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert state to a dictionary."""
        from dataclasses import asdict

        d = asdict(self)
        d["system_mode"] = self.system_mode.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> State:
        """Create State from a dictionary."""
        if "system_mode" in d and isinstance(d["system_mode"], str):
            d["system_mode"] = SystemMode(d["system_mode"])
        return cls(**d)


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    if p is None:
        p = Params()

    # Ensure rules are initialized
    p = initialize_rules(p)

    metro_ratio = p.nep_to_cost_ratio_metro
    reg_ratio = p.nep_to_cost_ratio_regional
    rem_ratio = p.nep_to_cost_ratio_remote
    ratio = (
        (1 - p.rurality_weight) * metro_ratio
        + (p.rurality_weight - p.remote_weight) * reg_ratio
        + p.remote_weight * rem_ratio
    )
    efficiency_gap = 1.0 / max(1e-9, ratio) - 1.0
    nominal_share = p.effective_cth_share_base * (1.0 + efficiency_gap)

    # Initialize Hierarchical Entities
    lhns = [LhnStateLegacy(id=i) for i in range(5)]
    jurisdictions = [
        JurisdictionStateLegacy(
            id=0,
            effective_cth_share=nominal_share,
            efficiency_gap=efficiency_gap,
            lhns=lhns,
        )
    ]

    return State(
        year=start_year,
        month=1,
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        effective_cth_share=nominal_share,
        efficiency_gap=efficiency_gap,
        discharge_delay=1.0,
        political_capital=jurisdictions[0].political_capital if jurisdictions else 1.0,
        target_capacity=1.0,
        current_capacity=1.0,
        equity_index=jurisdictions[0].equity_index if jurisdictions else 1.0,
        reconciliation_balance=jurisdictions[0].reconciliation_balance if jurisdictions else 0.0,
        bailout_expectation=jurisdictions[0].bailout_expectation if jurisdictions else 0.0,
        coding_intensity=1.0,
        reputation_score=1.0,
        system_mode=SystemMode.NORMAL,
        workforce_pool=1.0,
        agreement_clock=5,
        jurisdictions=jurisdictions,
        auditor_suspicion=0.0,
        audit_pressure_active=p.audit_pressure if p else 0.5,
        adjustment_costs=0.0,
        # Lags & Measurement
        lag_buffer_pressure=np.full(12, 1.0),
        lag_buffer_occupancy=np.full(12, p.occupancy_base if p else 0.88),
        lag_buffer_within4=np.full(12, p.within4_base if p else 0.53),
        lag_buffer_nwau=np.zeros(12),
        lag_buffer_efficiency_gap=np.full(12, efficiency_gap),
        lag_buffer_coding=np.full(12, 1.0),
        reported_pressure=1.0,
        reported_occupancy=p.occupancy_base if p else 0.88,
        reported_within4=p.within4_base if p else 0.53,
        reported_nwau=500.0,
        reported_efficiency_gap=efficiency_gap,
        reported_coding_intensity=1.0,
        solver_n_equilibria=1,
        solver_residual=0.0,
        prob_ed=0.5,
    )


# ----------------------------
# Transitions
# ----------------------------


def demand_step(
    s: State, p: Params, strategies: dict[str, Any], rng: np.random.Generator
) -> tuple[float, float]:
    demand_factor = (
        (1.04 * p.cost_shifting_intensity / 0.35) if strategies.get("SHIFT") == "S" else 0.96
    )

    # Use modular queuing equilibrium solver
    qp = PatientUtilityParams(
        gp_out_of_pocket=p.gp_out_of_pocket,
        gp_wait_time_min=p.gp_wait_time_min,
        patient_time_value_hour=p.patient_time_value_hour,
    )

    d_final, prob_ed = solve_queuing_equilibrium_legacy(
        total_base_demand=p.demand_base * demand_factor * 2.0,
        capacity=s.occupancy,  # Use current global occupancy as proxy for capacity constraint
        discharge_delay=1.0,
        params=qp,
    )

    demand = d_final + rng.normal(0, 0.02)
    return max(0.5, demand), prob_ed


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

    # Note: We take global reported eff_gap
    eff_gap = clamp((1.0 + s.reported_efficiency_gap) * drift_factor - 1.0, 0.05, 0.60)
    if strategies.get("DEF") == "R":
        eff_gap *= 0.93**month_growth_factor
    else:
        eff_gap *= 1.03**month_growth_factor

    # Nominal share drift
    eff_share = s.reported_efficiency_gap  # Proxy for current share drift base
    target = p.nominal_cth_share_target
    # Get bailout expectation from first jurisdiction (fallback to 0.0)
    current_bailout = s.jurisdictions[0].bailout_expectation if s.jurisdictions else 0.0
    if strategies.get("BARG") == "A":
        eff_share += 0.25 * (target - eff_share) * month_growth_factor
        # Guard for uninitialized reconciliation_rule
        if p.reconciliation_rule is not None:
            bailout = current_bailout + p.reconciliation_rule.calculate_bailout(
                s.pressure, month_growth_factor
            )
        else:
            # Fallback bailout calculation when rule not initialized
            bailout = current_bailout + (0.05 * month_growth_factor if s.pressure > 1.2 else 0.0)
    else:
        eff_share += 0.10 * (target - eff_share) * month_growth_factor
        bailout = max(0.0, current_bailout - 0.02 * month_growth_factor)

    if s.system_mode == SystemMode.CRISIS:
        eff_share = clamp(eff_share + 0.01, 0.30, 0.55)
    return eff_gap, eff_share, bailout


def lhn_step(
    lhn: LhnStateLegacy,
    p: Params,
    strategies: dict[str, Any],
    demand: float,
    mgf: float,
    rng: np.random.Generator,
    discharge_target: float,
    wf_availability: float,
) -> LhnStateLegacy:
    """Operational step for a single LHN (Legacy)."""
    # Workforce drain
    wf_drain = (
        0.2 if strategies.get("COMP") == "H" or strategies.get("WORKFORCE") == "H" else 0.1
    ) * mgf
    if strategies.get("COMPETITION") == "A":
        wf_drain += 0.1 * mgf

    wf_impact = math.exp(0.5 * max(0.0, 1.0 - wf_availability))

    aged_effect = 0.95 if strategies.get("AGED") == "C" else (1.02 * p.fragmentation_index)
    ndis_effect = 0.96 if strategies.get("NDIS") == "C" else (1.03 * p.fragmentation_index)
    disc_effect = 0.98 if strategies.get("DISC") == "C" else 1.01

    discharge = lhn.discharge_delay * ((aged_effect * ndis_effect * disc_effect) ** mgf) * wf_impact
    discharge = clamp(discharge + 0.1 * (discharge_target - discharge), 0.75, 1.50)

    is_expanding = lhn.target_capacity > lhn.current_capacity
    active_lag = p.expansion_lag if is_expanding else p.contraction_lag
    capacity = lhn.current_capacity + active_lag * (lhn.target_capacity - lhn.current_capacity)

    wait_min = mm_s_queue_wait(demand, 1.0 / max(1e-9, discharge), capacity * 10.0)
    occ = clamp(lhn.occupancy + 0.015 * (demand - 1.0) + 0.035 * (discharge - 1.0), 0.78, 0.98)
    off = clamp(lhn.offload_min + 8.0 * (occ - 0.88) + rng.normal(0, 0.8), 5.0, 120.0)
    pidx = 0.8 + 0.2 * (wait_min / 60.0) + 0.5 * (occ - 0.8) / 0.1

    return LhnStateLegacy(
        id=lhn.id,
        pressure=pidx,
        occupancy=occ,
        offload_min=off,
        within4=within4_from_pressure(pidx),
        discharge_delay=discharge,
        current_capacity=capacity,
        nwau_actual=occ * 100.0,
        adjustment_costs=p.adjustment_cost_beta * ((capacity - lhn.current_capacity) ** 2),
    )


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


def renegotiation_step(s: State, p: Params) -> tuple[float, int]:
    """Execute the strategic Hold-Up game at agreement expiry."""
    from nhra_gt.subgames.games import GameParams, renegotiation_game
    from nhra_gt.subgames.nash import all_nash, select_equilibrium

    gp = GameParams(
        pressure=s.pressure,
        efficiency_gap=s.reported_efficiency_gap,
        discharge_delay=(
            s.jurisdictions[0].lhns[0].discharge_delay
            if s.jurisdictions and s.jurisdictions[0].lhns
            else 1.0
        ),
        political_salience=p.political_salience,
        audit_pressure=p.audit_pressure,
        cost_shifting_intensity=p.cost_shifting_intensity,
        political_capital=1.0,  # Average across jurisdictions
    )

    game = renegotiation_game(gp, s.agreement_clock)
    eqs = all_nash(game)
    sel, _ = select_equilibrium(eqs, rule="payoff_dominant", u_row=game.u_row, u_col=game.u_col)

    cth_action = game.row_actions[int(np.argmax(sel.row))]
    state_action = game.col_actions[int(np.argmax(sel.col))]

    increase = 0.0
    if cth_action == "C" and state_action == "H":
        increase = 0.06
    elif cth_action == "C" or state_action == "H":
        increase = 0.03

    new_share = clamp(p.nominal_cth_share_target + increase, 0.40, 0.70)
    return new_share, 4


def step(
    s: State,
    p: Params,
    strategies: dict[str, Any],
    rng: np.random.Generator,
    subgame_metadata: dict[str, Any] | None = None,
) -> State:
    """Advance the simulation by one month (Hierarchical Refactor)."""
    if subgame_metadata is None:
        subgame_metadata = {}
    mgf = 1.0 / 12.0

    demand, prob_ed = demand_step(s, p, strategies, rng)
    eff_gap, eff_share, bailout = policy_step(s, p, strategies, mgf)

    # Workforce Update (Shared across all)
    new_wf_pool = clamp(s.workforce_pool - 0.02 + 0.1 * mgf, 0.5, 1.5)

    # Process Jurisdictions
    new_jurisdictions = []
    for jur in s.jurisdictions:
        # State-level target
        discharge_target = 0.9 if jur.political_capital < 0.8 else 1.0

        new_lhns = []
        for lhn in jur.lhns:
            lhn = replace(
                lhn,
                target_capacity=s.target_capacity,
                current_capacity=s.current_capacity,
                discharge_delay=s.discharge_delay,
                coding_intensity=s.coding_intensity,
            )
            new_lhns.append(
                lhn_step(lhn, p, strategies, demand, mgf, rng, discharge_target, s.workforce_pool)
            )

        adjustment_costs = float(sum(lhn.adjustment_costs for lhn in new_lhns))
        reconciliation_balance = jur.reconciliation_balance - adjustment_costs

        new_jurisdictions.append(
            JurisdictionStateLegacy(
                id=jur.id,
                reconciliation_balance=reconciliation_balance,
                bailout_expectation=bailout,
                political_capital=jur.political_capital,
                effective_cth_share=eff_share,
                efficiency_gap=eff_gap,
                lhns=new_lhns,
            )
        )

    # Global Aggregation
    all_lhns = [lhn for jur in new_jurisdictions for lhn in jur.lhns]
    avg_pidx = np.mean([lhn.pressure for lhn in all_lhns])
    avg_occ = np.mean([lhn.occupancy for lhn in all_lhns])
    avg_w4 = np.mean([lhn.within4 for lhn in all_lhns])
    avg_discharge = float(np.mean([lhn.discharge_delay for lhn in all_lhns]))
    avg_target_capacity = float(np.mean([lhn.target_capacity for lhn in all_lhns]))
    avg_current_capacity = float(np.mean([lhn.current_capacity for lhn in all_lhns]))
    total_adjustment_costs = float(sum(lhn.adjustment_costs for lhn in all_lhns))
    total_nwau = sum([lhn.nwau_actual for lhn in all_lhns])

    # Auditor move
    coding_signal = max(0.0, 1.0 - 1.0)  # Placeholder
    new_suspicion = 0.8 * s.auditor_suspicion + 0.2 * coding_signal
    new_pressure = max(0.05, min(1.0, p.audit_pressure))

    # Renegotiation
    final_eff_share = eff_share
    next_clock = s.agreement_clock
    if s.month == 12:
        if s.agreement_clock == 0:
            final_eff_share, next_clock = renegotiation_step(s, p)
        else:
            next_clock -= 1

    # Lags
    new_buf_p = np.roll(s.lag_buffer_pressure, -1)
    new_buf_p[-1] = avg_pidx
    sig_idx = 11 - clamp(p.signal_lag_months, 0, 11)
    rep_p = new_buf_p[int(sig_idx)]

    return State(
        year=(s.year + 1 if s.month == 12 else s.year),
        month=(1 if s.month == 12 else s.month + 1),
        pressure=avg_pidx,
        occupancy=avg_occ,
        offload_min=np.mean([lhn.offload_min for lhn in all_lhns]),
        within4=avg_w4,
        effective_cth_share=final_eff_share,
        efficiency_gap=eff_gap,
        discharge_delay=avg_discharge,
        political_capital=float(
            np.mean([jur.political_capital for jur in new_jurisdictions])
            if new_jurisdictions
            else 1.0
        ),
        target_capacity=avg_target_capacity,
        current_capacity=avg_current_capacity,
        equity_index=float(
            np.mean([jur.equity_index for jur in new_jurisdictions]) if new_jurisdictions else 1.0
        ),
        reconciliation_balance=float(
            np.mean([jur.reconciliation_balance for jur in new_jurisdictions])
            if new_jurisdictions
            else 0.0
        ),
        bailout_expectation=float(
            np.mean([jur.bailout_expectation for jur in new_jurisdictions])
            if new_jurisdictions
            else 0.0
        ),
        coding_intensity=s.coding_intensity,
        reputation_score=s.reputation_score,
        system_mode=update_system_mode(s, p),
        workforce_pool=new_wf_pool,
        agreement_clock=next_clock,
        jurisdictions=new_jurisdictions,
        auditor_suspicion=new_suspicion,
        audit_pressure_active=new_pressure,
        adjustment_costs=total_adjustment_costs,
        reported_pressure=rep_p,
        reported_occupancy=avg_occ,  # Simplified
        reported_within4=avg_w4,
        reported_nwau=total_nwau,
        reported_efficiency_gap=eff_gap,
        reported_coding_intensity=1.0,
        solver_n_equilibria=subgame_metadata.get("n_equilibria", 1),
        prob_ed=prob_ed,
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
    """Execute a hybrid simulation experiment with multiple Monte Carlo rollouts."""
    rng = np.random.default_rng(seed)
    start_year, end_year = years[0], years[-1]
    rows, strat_rows = [], []
    agent = HeuristicAgent()

    for r in range(n_mc):
        sub = np.random.default_rng(int(rng.integers(0, 2**31)))
        s = baseline_state(start_year, p)
        cum_press = 0.0
        while s.year <= end_year:
            rr = relative_risk(s.pressure, s.offload_min, p)
            cum_press += s.pressure / 12.0
            rows.append(
                {
                    "rollout": r,
                    "year": s.year,
                    "month": s.month,
                    "pressure": s.pressure,
                    "occupancy": s.occupancy,
                    "within4": s.within4,
                    "offload_min": s.offload_min,
                    "cth_share_nominal": s.effective_cth_share
                    if hasattr(s, "effective_cth_share")
                    else 0.38,
                    "efficiency_gap": s.reported_efficiency_gap,
                    "rr_proxy": rr,
                    "workforce": s.workforce_pool,
                    "prob_ed": s.prob_ed,
                    "agreement_clock": s.agreement_clock,
                }
            )

            strategies = agent.decide(s, p, sub)
            if overrides:
                strategies.update(overrides)

            # Record strategies
            rat = strategies.get("RATIONALE", "")
            for g, lab in strategies.items():
                if g not in {"RATIONALE", "n_equilibria"}:
                    strat_rows.append(
                        {
                            "rollout": r,
                            "year": s.year,
                            "month": s.month,
                            "game": g,
                            "strategy": str(lab),
                            "rationale": rat,
                        }
                    )

            meta = {"n_equilibria": strategies.get("n_equilibria", 1)}
            s = step(s, p, strategies, sub, subgame_metadata=meta)
            if s.year > end_year:
                break

    df, strat = pd.DataFrame(rows), pd.DataFrame(strat_rows)
    agg = (
        df.groupby("year")
        .agg(
            pressure_mean=("pressure", "mean"),
            pressure_std=("pressure", "std"),
            occupancy_mean=("occupancy", "mean"),
            occupancy_std=("occupancy", "std"),
            within4_mean=("within4", "mean"),
            within4_std=("within4", "std"),
            offload_mean=("offload_min", "mean"),
            rr_mean=("rr_proxy", "mean"),
            rr_std=("rr_proxy", "std"),
            workforce_mean=("workforce", "mean"),
            prob_ed_mean=("prob_ed", "mean"),
            agreement_clock_mean=("agreement_clock", "mean"),
            cth_nominal_mean=("cth_share_nominal", "mean"),
            effgap_mean=("efficiency_gap", "mean"),
        )
        .reset_index()
    )

    # Calculate SEM
    for m in ["pressure", "occupancy", "within4", "rr"]:
        agg[f"{m}_sem"] = agg[f"{m}_std"] / math.sqrt(n_mc)

    if not strat.empty:
        freq = strat.groupby(["year", "game", "strategy"]).size().reset_index(name="n")
        freq["share"] = freq["n"] / freq.groupby(["year", "game"])["n"].transform("sum")
    else:
        freq = pd.DataFrame(columns=["year", "game", "strategy", "n", "share"])

    return agg, freq


def mm_s_queue_wait(arrival_rate: float, service_rate: float, servers: float) -> float:
    utilization = arrival_rate / max(1e-9, (service_rate * servers))
    if utilization >= 1.0:
        return 1440.0
    wait = (utilization ** (math.sqrt(2 * (servers + 1)) - 1)) / (servers * (1 - utilization))
    return max(5.0, min(1440.0, wait * 60.0))


def within4_from_pressure(pidx: float) -> float:
    return max(0.05, min(0.85, 0.80 - 0.45 * (1.0 / (1.0 + math.exp(-(pidx - 1.0) / 0.20)))))


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


def apply_intervention(p: Params, name: str) -> Params:
    key = name.lower().strip().replace(" ", "_")

    if key in {"pooled_funding", "pooled"}:
        return replace(
            p, cost_shifting_intensity=clamp(p.cost_shifting_intensity * 0.75, 0.05, 0.60)
        )

    if key in {"ucc_integration", "integration"}:
        return replace(p, fragmentation_index=clamp(p.fragmentation_index * 0.80, 0.60, 1.50))

    if key in {"nep_realism", "indexation"}:
        return replace(
            p,
            nep_to_cost_ratio_metro=clamp(p.nep_to_cost_ratio_metro + 0.03, 0.6, 1.0),
            nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.04, 0.6, 1.0),
            nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.05, 0.6, 1.0),
        )

    if key in {"aged_ndis_capacity", "discharge"}:
        return replace(p, discharge_delay_base=clamp(p.discharge_delay_base * 0.90, 0.6, 1.4))

    if key in {"middle_tier", "workforce"}:
        return replace(
            p,
            nep_to_cost_ratio_regional=clamp(p.nep_to_cost_ratio_regional + 0.03, 0.6, 1.0),
            nep_to_cost_ratio_remote=clamp(p.nep_to_cost_ratio_remote + 0.04, 0.6, 1.0),
        )

    if key in {"cumulative_cap", "cap"}:
        return replace(p, has_cumulative_cap=True, cap_growth=0.070)

    if key in {"audit_relief"}:
        return replace(
            p,
            audit_pressure=clamp(p.audit_pressure * 0.70, 0.05, 1.0),
            admin_burden_weight=clamp(p.admin_burden_weight * 0.8, 0.05, 0.6),
        )

    return p


def summarise_outcome(agg: pd.DataFrame) -> dict[str, float]:
    last = agg.sort_values("year").iloc[-1]
    return {
        "pressure_2030": float(last["pressure_mean"]),
        "within4_2030": float(last["within4_mean"]),
        "offload_2030": float(last.get("offload_mean", 18.0)),
        "rr_2030": float(last["rr_mean"]),
        "effshare_nominal_2030": float(last["cth_nominal_mean"]),
        "effshare_effective_2030": float(last["cth_nominal_mean"]),
        "effgap_2030": float(last["effgap_mean"]),
    }


def nep_series(years: list[int], p: Params) -> pd.DataFrame:
    """Return an illustrative NEP series.

    NEP is represented as an index by default (`nep_per_nwau_start=1.0`), but can be set to
    an actual IHACPA $/NWAU level if desired.

    Columns:
      - year
      - nep_per_nwau
      - representative_nwau
      - efficient_payment
    """

    nep = float(p.nep_per_nwau_start)
    rows: list[dict[str, float | int]] = []
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


def nep_vs_cost_series(years: list[int], p: Params) -> pd.DataFrame:
    """Return NEP and input-cost indices over time."""

    nep = float(p.nep_per_nwau_start)
    cost = float(p.input_cost_per_nwau_start)
    rows: list[dict[str, float | int]] = []
    for i, y in enumerate(years):
        if i > 0:
            nep *= 1.0 + float(p.nep_annual_growth)
            cost *= 1.0 + float(p.input_cost_annual_growth)
        rows.append(
            {
                "year": int(y),
                "nep_per_nwau": float(nep),
                "input_cost_per_nwau": float(cost),
                "nep_to_cost_ratio": float(nep / max(1e-9, cost)),
            }
        )
    return pd.DataFrame(rows)
