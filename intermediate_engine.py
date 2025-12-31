from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

try:
    import jax
    import jax.numpy as jnp
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "`intermediate_engine` is only used for JAX parity tests and requires `jax`."
    ) from exc


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
    demand_base: float = 0.85
    avoidable_ed_share: float = 0.18
    discharge_delay_base: float = 1.00
    bed_capacity_index: float = 1.00
    capacity_lag: float = 0.15

    # Couplings
    cost_shifting_intensity: float = 0.35
    fragmentation_index: float = 1.00
    audit_pressure: float = 0.50
    admin_burden_weight: float = 0.25

    # Boundary shifting
    block_funding_base: float = 0.15

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

    # Negotiation / solver toggles
    use_equilibrium_bargaining: bool = False
    use_quantal_response: bool = False
    qre_lambda: float = 4.0
    use_burden_feedback: bool = False
    burden_to_throughput_beta: float = 0.06
    noise_sd: float = 0.03

    # Rule types: keep legacy-friendly strings
    cap_rule_type: str = "hard"
    audit_rule_type: str = "proportional"

    # Rule objects (populated by nhra_gt.rules.initialize_rules)
    cap_rule: Any | None = None
    audit_rule: Any | None = None
    eligibility_rule: Any | None = None
    reconciliation_rule: Any | None = None

    # Optional “economic spine” used by some conversions/tests
    economic_spine: Any | None = None

    def replace(self, **updates: Any) -> Params:
        return replace(self, **updates)


@dataclass
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
    target_capacity: float
    current_capacity: float
    equity_index: float
    reconciliation_balance: float
    bailout_expectation: float
    coding_intensity: float
    reputation_score: float
    auditor_suspicion: float
    audit_pressure_active: float

    lag_buffer_pressure: np.ndarray
    lag_buffer_occupancy: np.ndarray
    lag_buffer_within4: np.ndarray
    lag_buffer_nwau: np.ndarray
    lag_buffer_efficiency_gap: np.ndarray
    lag_buffer_coding: np.ndarray

    reported_pressure: float
    reported_occupancy: float
    reported_within4: float
    reported_nwau: float
    reported_efficiency_gap: float
    reported_coding_intensity: float


def baseline_state(start_year: int = 2025, p: Params | None = None) -> State:
    from nhra_gt.domain.state import ParamsJax
    from nhra_gt.engine import baseline_state as baseline_state_jax
    from nhra_gt.rules import initialize_rules

    p = initialize_rules(p or Params())  # type: ignore[arg-type]

    cap_rule_type = 1 if getattr(p, "cap_rule_type", "hard") == "soft" else 0
    audit_rule_type = 1 if getattr(p, "audit_rule_type", "proportional") == "threshold" else 0

    p_jax = ParamsJax(
        nep_to_cost_ratio_metro=p.nep_to_cost_ratio_metro,
        nep_to_cost_ratio_regional=p.nep_to_cost_ratio_regional,
        nep_to_cost_ratio_remote=p.nep_to_cost_ratio_remote,
        rurality_weight=p.rurality_weight,
        remote_weight=p.remote_weight,
        nominal_cth_share_target=p.nominal_cth_share_target,
        effective_cth_share_base=p.effective_cth_share_base,
        cap_growth=p.cap_growth,
        has_cumulative_cap=p.has_cumulative_cap,
        nep_annual_growth=p.nep_annual_growth,
        input_cost_annual_growth=p.input_cost_annual_growth,
        nep_per_nwau_start=p.nep_per_nwau_start,
        input_cost_per_nwau_start=p.input_cost_per_nwau_start,
        representative_nwau=p.representative_nwau,
        demand_base=p.demand_base,
        avoidable_ed_share=p.avoidable_ed_share,
        discharge_delay_base=p.discharge_delay_base,
        bed_capacity_index=p.bed_capacity_index,
        capacity_lag=p.capacity_lag,
        cost_shifting_intensity=p.cost_shifting_intensity,
        fragmentation_index=p.fragmentation_index,
        audit_pressure=p.audit_pressure,
        admin_burden_weight=p.admin_burden_weight,
        occupancy_base=p.occupancy_base,
        offload_base_min=p.offload_base_min,
        within4_base=p.within4_base,
        rr_beta_pressure=p.rr_beta_pressure,
        rr_beta_offload=p.rr_beta_offload,
        offload_threshold_min=p.offload_threshold_min,
        tau=p.tau,
        bargaining_cost=p.bargaining_cost,
        political_salience=p.political_salience,
        use_equilibrium_bargaining=p.use_equilibrium_bargaining,
        use_quantal_response=p.use_quantal_response,
        qre_lambda=p.qre_lambda,
        use_burden_feedback=p.use_burden_feedback,
        burden_to_throughput_beta=p.burden_to_throughput_beta,
        noise_sd=p.noise_sd,
        cap_rule_type=cap_rule_type,
        audit_rule_type=audit_rule_type,
        cap_rule=p.cap_rule,
        audit_rule=p.audit_rule,
        eligibility_rule=p.eligibility_rule,
        reconciliation_rule=p.reconciliation_rule,
    )

    s = baseline_state_jax(start_year=start_year, p=p_jax)
    return State(
        year=int(s.year),
        month=int(s.month),
        pressure=float(s.pressure),
        occupancy=float(s.occupancy),
        offload_min=float(s.offload_min),
        within4=float(s.within4),
        effective_cth_share=float(s.effective_cth_share),
        efficiency_gap=float(s.efficiency_gap),
        discharge_delay=float(s.discharge_delay),
        political_capital=float(s.political_capital),
        target_capacity=float(s.target_capacity),
        current_capacity=float(s.current_capacity),
        equity_index=float(s.equity_index),
        reconciliation_balance=float(s.reconciliation_balance),
        bailout_expectation=float(s.bailout_expectation),
        coding_intensity=float(s.coding_intensity),
        reputation_score=float(s.reputation_score),
        auditor_suspicion=float(s.auditor_suspicion),
        audit_pressure_active=float(s.audit_pressure_active),
        lag_buffer_pressure=np.asarray(s.lag_buffer_pressure, dtype=float),
        lag_buffer_occupancy=np.asarray(s.lag_buffer_occupancy, dtype=float),
        lag_buffer_within4=np.asarray(s.lag_buffer_within4, dtype=float),
        lag_buffer_nwau=np.asarray(s.lag_buffer_nwau, dtype=float),
        lag_buffer_efficiency_gap=np.asarray(s.lag_buffer_efficiency_gap, dtype=float),
        lag_buffer_coding=np.asarray(s.lag_buffer_coding, dtype=float),
        reported_pressure=float(s.reported_pressure),
        reported_occupancy=float(s.reported_occupancy),
        reported_within4=float(s.reported_within4),
        reported_nwau=float(s.reported_nwau),
        reported_efficiency_gap=float(s.reported_efficiency_gap),
        reported_coding_intensity=float(s.reported_coding_intensity),
    )


def _strategies_to_jax(strat: dict[str, Any]) -> jnp.ndarray:
    arr = jnp.zeros(13)
    arr = arr.at[0].set(1 if strat.get("SIGNAL") == "H" else 0)
    arr = arr.at[1].set(1 if strat.get("DEF") == "R" else 0)
    arr = arr.at[2].set(1 if strat.get("BARG") == "A" else 0)
    arr = arr.at[3].set(1 if strat.get("SHIFT") == "S" else 0)
    arr = arr.at[4].set(1 if strat.get("DISC") == "C" else 0)
    arr = arr.at[5].set(1 if strat.get("AGED") == "C" else 0)
    arr = arr.at[6].set(1 if strat.get("NDIS") == "C" else 0)
    arr = arr.at[7].set(1 if strat.get("CODING") == "U" else 0)
    arr = arr.at[8].set(1 if strat.get("COMP") == "H" or strat.get("WORKFORCE") == "H" else 0)
    arr = arr.at[9].set(float(strat.get("SIGNAL_QUALITY", 1.0)))
    arr = arr.at[10].set(1 if strat.get("VENUE_SHIFT") == "B" else 0)
    arr = arr.at[11].set(float(strat.get("CAPACITY_MOVE", 0.0)))
    arr = arr.at[12].set(1 if strat.get("COMPETITION") == "A" else 0)
    return arr


def _state_to_jax(s: State):
    from nhra_gt.domain.state import JurisdictionState, LhnState, StateJax

    n_lhns = 5
    lhns = jax.vmap(lambda i: LhnState(id=i))(jnp.arange(n_lhns))
    jurisdiction = JurisdictionState(id=0, lhn_states=lhns)
    jurisdictions = jax.tree_util.tree_map(lambda x: jnp.expand_dims(x, 0), jurisdiction)

    return StateJax(
        year=jnp.array(s.year, dtype=jnp.int32),
        month=jnp.array(s.month, dtype=jnp.int32),
        pressure=jnp.array(s.pressure),
        occupancy=jnp.array(s.occupancy),
        offload_min=jnp.array(s.offload_min),
        within4=jnp.array(s.within4),
        effective_cth_share=jnp.array(s.effective_cth_share),
        efficiency_gap=jnp.array(s.efficiency_gap),
        discharge_delay=jnp.array(s.discharge_delay),
        political_capital=jnp.array(s.political_capital),
        system_mode=jnp.array(0, dtype=jnp.int32),
        lhn_pressure=jnp.full(n_lhns, s.pressure),
        lhn_nwau=jnp.full(n_lhns, 100.0),
        agreement_clock=jnp.array(5, dtype=jnp.int32),
        workforce_pool=jnp.array(1.0),
        target_capacity=jnp.array(s.target_capacity),
        current_capacity=jnp.array(s.current_capacity),
        equity_index=jnp.array(s.equity_index),
        reconciliation_balance=jnp.array(s.reconciliation_balance),
        bailout_expectation=jnp.array(s.bailout_expectation),
        coding_intensity=jnp.array(s.coding_intensity),
        reputation_score=jnp.array(s.reputation_score),
        auditor_suspicion=jnp.array(s.auditor_suspicion),
        audit_pressure_active=jnp.array(s.audit_pressure_active),
        jurisdictions=jurisdictions,
        lag_buffer_pressure=jnp.array(s.lag_buffer_pressure),
        lag_buffer_occupancy=jnp.array(s.lag_buffer_occupancy),
        lag_buffer_within4=jnp.array(s.lag_buffer_within4),
        lag_buffer_nwau=jnp.array(s.lag_buffer_nwau),
        lag_buffer_efficiency_gap=jnp.array(s.lag_buffer_efficiency_gap),
        lag_buffer_coding=jnp.array(s.lag_buffer_coding),
        reported_pressure=float(s.reported_pressure),
        reported_occupancy=float(s.reported_occupancy),
        reported_within4=float(s.reported_within4),
        reported_nwau=float(s.reported_nwau),
        reported_efficiency_gap=float(s.reported_efficiency_gap),
        reported_coding_intensity=float(s.reported_coding_intensity),
    )


def _jax_to_state(s) -> State:
    return State(
        year=int(s.year),
        month=int(s.month),
        pressure=float(s.pressure),
        occupancy=float(s.occupancy),
        offload_min=float(s.offload_min),
        within4=float(s.within4),
        effective_cth_share=float(s.effective_cth_share),
        efficiency_gap=float(s.efficiency_gap),
        discharge_delay=float(s.discharge_delay),
        political_capital=float(s.political_capital),
        target_capacity=float(s.target_capacity),
        current_capacity=float(s.current_capacity),
        equity_index=float(s.equity_index),
        reconciliation_balance=float(s.reconciliation_balance),
        bailout_expectation=float(s.bailout_expectation),
        coding_intensity=float(s.coding_intensity),
        reputation_score=float(s.reputation_score),
        auditor_suspicion=float(s.auditor_suspicion),
        audit_pressure_active=float(s.audit_pressure_active),
        lag_buffer_pressure=np.asarray(s.lag_buffer_pressure, dtype=float),
        lag_buffer_occupancy=np.asarray(s.lag_buffer_occupancy, dtype=float),
        lag_buffer_within4=np.asarray(s.lag_buffer_within4, dtype=float),
        lag_buffer_nwau=np.asarray(s.lag_buffer_nwau, dtype=float),
        lag_buffer_efficiency_gap=np.asarray(s.lag_buffer_efficiency_gap, dtype=float),
        lag_buffer_coding=np.asarray(s.lag_buffer_coding, dtype=float),
        reported_pressure=float(s.reported_pressure),
        reported_occupancy=float(s.reported_occupancy),
        reported_within4=float(s.reported_within4),
        reported_nwau=float(s.reported_nwau),
        reported_efficiency_gap=float(s.reported_efficiency_gap),
        reported_coding_intensity=float(s.reported_coding_intensity),
    )


def step(s: State, p: Params, strategies: dict[str, Any], rng: np.random.Generator) -> State:
    from nhra_gt.domain.state import ParamsJax
    from nhra_gt.engine import step_jax
    from nhra_gt.rules import initialize_rules

    p = initialize_rules(p)  # type: ignore[arg-type]

    cap_rule_type = 1 if getattr(p, "cap_rule_type", "hard") == "soft" else 0
    audit_rule_type = 1 if getattr(p, "audit_rule_type", "proportional") == "threshold" else 0

    p_jax = ParamsJax(
        nep_to_cost_ratio_metro=p.nep_to_cost_ratio_metro,
        nep_to_cost_ratio_regional=p.nep_to_cost_ratio_regional,
        nep_to_cost_ratio_remote=p.nep_to_cost_ratio_remote,
        rurality_weight=p.rurality_weight,
        remote_weight=p.remote_weight,
        nominal_cth_share_target=p.nominal_cth_share_target,
        effective_cth_share_base=p.effective_cth_share_base,
        cap_growth=p.cap_growth,
        has_cumulative_cap=p.has_cumulative_cap,
        nep_annual_growth=p.nep_annual_growth,
        input_cost_annual_growth=p.input_cost_annual_growth,
        nep_per_nwau_start=p.nep_per_nwau_start,
        input_cost_per_nwau_start=p.input_cost_per_nwau_start,
        representative_nwau=p.representative_nwau,
        demand_base=p.demand_base,
        avoidable_ed_share=p.avoidable_ed_share,
        discharge_delay_base=p.discharge_delay_base,
        bed_capacity_index=p.bed_capacity_index,
        capacity_lag=p.capacity_lag,
        cost_shifting_intensity=p.cost_shifting_intensity,
        fragmentation_index=p.fragmentation_index,
        audit_pressure=p.audit_pressure,
        admin_burden_weight=p.admin_burden_weight,
        occupancy_base=p.occupancy_base,
        offload_base_min=p.offload_base_min,
        within4_base=p.within4_base,
        rr_beta_pressure=p.rr_beta_pressure,
        rr_beta_offload=p.rr_beta_offload,
        offload_threshold_min=p.offload_threshold_min,
        tau=p.tau,
        bargaining_cost=p.bargaining_cost,
        political_salience=p.political_salience,
        use_equilibrium_bargaining=p.use_equilibrium_bargaining,
        use_quantal_response=p.use_quantal_response,
        qre_lambda=p.qre_lambda,
        use_burden_feedback=p.use_burden_feedback,
        burden_to_throughput_beta=p.burden_to_throughput_beta,
        noise_sd=p.noise_sd,
        cap_rule_type=cap_rule_type,
        audit_rule_type=audit_rule_type,
        cap_rule=p.cap_rule,
        audit_rule=p.audit_rule,
        eligibility_rule=p.eligibility_rule,
        reconciliation_rule=p.reconciliation_rule,
    )

    str_j = _strategies_to_jax(strategies)
    sj = _state_to_jax(s)
    if hasattr(rng, "integers"):
        seed = int(rng.integers(0, 2**31 - 1))  # type: ignore[call-arg]
    else:
        seed = int(float(rng.random()) * (2**31 - 1))  # type: ignore[call-arg]
    key = jax.random.PRNGKey(seed)
    next_sj = step_jax(sj, p_jax, str_j, key)
    return _jax_to_state(next_sj)


__all__ = ["Params", "State", "baseline_state", "step"]
