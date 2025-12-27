from __future__ import annotations

from enum import IntEnum
from typing import Any

import jax.numpy as jnp
from flax import struct


class SystemModeJax(IntEnum):
    NORMAL = 0
    STRESS = 1
    CRISIS = 2
    RECOVERY = 3


@struct.dataclass
class EconomicSpineJax:
    """JAX-compatible container for economic indices."""

    years: jnp.ndarray  # int32[N]
    nep_per_nwau: jnp.ndarray  # float64[N]
    wpi_health_index: jnp.ndarray  # float64[N]


@struct.dataclass
class MetricsJax:
    """Accumulated metrics for policy optimization and objective functions."""

    cumulative_pressure: float = 0.0
    cumulative_budget_variance: float = 0.0
    max_occupancy: float = 0.0
    min_within4: float = 1.0


@struct.dataclass
class ParamsJax:
    """JAX-compatible simulation parameters."""

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

    # Orchestration & Logic (mapped to ints/floats for JAX)
    # cap_rule_type: 0 for hard, 1 for soft
    cap_rule_type: int = 0
    # audit_rule_type: 0 for proportional, 1 for threshold
    audit_rule_type: int = 0

    # Economic Spine (optional JAX arrays)
    spine: EconomicSpineJax | None = None


@struct.dataclass
class StateJax:
    """JAX-compatible simulation state."""

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
    system_mode: int  # Mapped from SystemModeJax
    target_capacity: float = 1.0
    current_capacity: float = 1.0
    equity_index: float = 1.0
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    coding_intensity: float = 1.0
    reputation_score: float = 1.0
    jurisdiction_id: int = 0

    metrics: MetricsJax = MetricsJax()
