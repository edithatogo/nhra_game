from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import Any

import jax.numpy as jnp
from flax import struct

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]


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

    # Leakage Metrics
    cumulative_indexation_loss: float = 0.0
    cumulative_cap_loss: float = 0.0
    cumulative_audit_loss: float = 0.0
    cumulative_adjustment_costs: float = 0.0

    # Stability Metrics
    max_solver_n_equilibria: int = 0
    mean_solver_residual: float = 0.0

    def replace(self, **kwargs: Any) -> MetricsJax:
        return self.replace(**kwargs)


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
    demand_base: float = 0.85
    avoidable_ed_share: float = 0.18
    discharge_delay_base: float = 1.00
    bed_capacity_index: float = 1.00
    capacity_lag: float = 0.15
    expansion_lag: float = 0.10  # Harder to hire
    contraction_lag: float = 0.20  # Easier to reduce (simplified)
    adjustment_cost_beta: float = 5.0  # Sensitivity of fiscal cost to Delta Capacity

    # Couplings
    cost_shifting_intensity: float = 0.35
    fragmentation_index: float = 1.00
    audit_pressure: float = 0.50
    admin_burden_weight: float = 0.25
    cannibalization_beta: float = 0.1  # Drain factor for workforce/volume competition

    # Boundary Shifting
    block_funding_base: float = 0.15  # 15% of activity typically block funded
    shifting_friction: float = 0.05  # Cost of moving activity between streams

    # Lags & Measurement
    signal_lag_months: int = 1  # Lag for public indicators (pressure, occupancy)
    claims_lag_months: int = 3  # Lag for financial data (NWAU, coding)

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

    # Orchestration & Logic (mapped to ints/floats for JAX)
    # cap_rule_type: 0 for hard, 1 for soft
    cap_rule_type: int = 0
    # audit_rule_type: 0 for proportional, 1 for threshold
    audit_rule_type: int = 0
    orchestration_mode: int = 0
    equilibrium_selection_rule: str = "nash"
    isolated_game: str | None = None
    use_stage_game_equilibria: bool = True

    # Modular Rules (JAX-compatible PyTrees)
    cap_rule: Any = struct.field(default_factory=lambda: None)
    audit_rule: Any = struct.field(default_factory=lambda: None)
    eligibility_rule: Any = struct.field(default_factory=lambda: None)
    reconciliation_rule: Any = struct.field(default_factory=lambda: None)

    # Economic Spine (optional JAX arrays)
    spine: EconomicSpineJax | None = None
    economic_spine: str | None = None  # Registry alias/path placeholder

    def replace(self, **kwargs: Any) -> ParamsJax:
        return self.replace(**kwargs)

    @classmethod
    def from_yaml(cls, path: Path | str) -> ParamsJax:
        """Loads parameters from a YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        # Flatten the nested YAML groups
        flat_data = {}
        for group in data.values():
            if isinstance(group, dict):
                flat_data.update(group)

        # Filter only fields that exist in the dataclass
        # We handle default type conversion if needed (e.g. bools to ints for JAX)
        return cls(**{k: v for k, v in flat_data.items() if k in cls.__dataclass_fields__})


# Backwards-compatible alias (many callers/tests still import `Params` from this module).
Params = ParamsJax


class BaselineProvider:
    """Manages loading of the automated data spine and baseline parameters."""

    @staticmethod
    def load_spine(
        path: Path | str = "data/calibration/historical_normalized.csv",
    ) -> EconomicSpineJax:
        if pl is None:
            import pandas as pd

            df_pd = pd.read_csv(path)
            return EconomicSpineJax(
                years=jnp.array(df_pd["year"].to_numpy().astype(jnp.int32)),
                nep_per_nwau=jnp.array(
                    df_pd["within4"].to_numpy()
                ),  # Placeholder for actual NEP if not in spine
                wpi_health_index=jnp.array(df_pd["occupancy"].to_numpy()),  # Placeholder
            )

        df = pl.read_csv(path)
        return EconomicSpineJax(
            years=jnp.array(df["year"].to_numpy().astype(jnp.int32)),
            nep_per_nwau=jnp.array(
                df["within4"].to_numpy()
            ),  # Placeholder for actual NEP if not in spine
            wpi_health_index=jnp.array(df["occupancy"].to_numpy()),  # Placeholder
        )

    @classmethod
    def get_baseline(cls, config_path: str = "configs/defaults.yaml") -> tuple[ParamsJax, StateJax]:
        from nhra_gt.engine_jax import baseline_state_jax

        params = ParamsJax.from_yaml(config_path)
        # Check if spine exists
        spine_path = Path("data/calibration/historical_normalized.csv")
        if spine_path.exists():
            spine = cls.load_spine(spine_path)
            params = params.replace(spine=spine)

        state = baseline_state_jax(2025, params)
        return params, state


@struct.dataclass
class LhnState:
    """Granular state for a single Local Hospital Network (LHN)."""

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

    def replace(self, **kwargs: Any) -> LhnState:
        return self.replace(**kwargs)


@struct.dataclass
class JurisdictionState:
    """Granular state for a single Jurisdiction (State/Territory)."""

    id: int
    reconciliation_balance: float = 0.0
    bailout_expectation: float = 0.0
    political_capital: float = 1.0
    effective_cth_share: float = 0.38
    efficiency_gap: float = 0.10
    equity_index: float = 1.0
    total_block_revenue: float = 0.0
    lhn_states: LhnState = struct.field(
        default_factory=lambda: LhnState(0)
    )  # Vectorized in practice

    def replace(self, **kwargs: Any) -> JurisdictionState:
        return self.replace(**kwargs)


@struct.dataclass
class StateJax:
    """JAX-compatible simulation state (Global Orchestrator)."""

    year: Any
    month: Any
    pressure: Any
    occupancy: Any
    offload_min: Any
    within4: Any

    # Fiscal / bargaining state
    effective_cth_share: Any = 0.38
    efficiency_gap: Any = 0.10
    discharge_delay: Any = 1.0
    political_capital: Any = 1.0
    equity_index: Any = 1.0
    reconciliation_balance: Any = 0.0
    bailout_expectation: Any = 0.0
    total_block_revenue: Any = 0.0

    # Orchestrator state
    system_mode: Any = 0  # Mapped from SystemModeJax
    agreement_clock: Any = 5
    workforce_pool: Any = 1.0
    target_capacity: Any = 1.0
    current_capacity: Any = 1.0
    coding_intensity: Any = 1.0
    reputation_score: Any = 1.0
    jurisdiction_id: Any = 0

    # Per-LHN (flat) state used by tests + simple vmaps
    lhn_pressure: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(5))
    lhn_nwau: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(5))

    # Hierarchical Entities (optional richer representation)
    jurisdictions: JurisdictionState | None = None

    # Auditor Agent state
    auditor_suspicion: float = 0.0
    audit_pressure_active: float = 0.0
    adjustment_costs: float = 0.0

    # Lags & Measurement
    # Buffers store up to 12 months of history
    lag_buffer_pressure: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_occupancy: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_within4: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_nwau: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_efficiency_gap: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))
    lag_buffer_coding: jnp.ndarray = struct.field(default_factory=lambda: jnp.zeros(12))

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

    metrics: MetricsJax = MetricsJax()

    def replace(self, **kwargs: Any) -> StateJax:
        return self.replace(**kwargs)
