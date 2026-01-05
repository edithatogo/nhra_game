"""
JAX-compatible state definitions for the NHRA simulation.

This module defines the data structures used to represent the state of the system
at various levels of granularity (LHN, Jurisdiction, Global). It uses
`flax.struct.dataclass` to ensure compatibility with JAX transformations
like `jit`, `vmap`, and `grad`.
"""

from __future__ import annotations

import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

import jax.numpy as jnp
from flax import struct

from .params_generated import ParamsGenerated

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class SystemModeJax(IntEnum):
    """Enumeration of system-wide operational modes."""

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
        return struct.replace(self, **kwargs)


@struct.dataclass
class OperationalParamsJax:
    """Hidden coefficients for system dynamics (JAX version)."""

    wf_drain_max: float = 0.2
    wf_drain_min: float = 0.1
    wf_comp_drain: float = 0.1
    wf_impact_weight: float = 0.5
    aged_coord_effect: float = 0.95
    aged_frag_effect: float = 1.02
    ndis_coord_effect: float = 0.96
    ndis_frag_effect: float = 1.03
    disc_coord_effect: float = 0.98
    disc_frag_effect: float = 1.01
    discharge_update_speed: float = 0.1
    eff_gap_decay: float = 0.93
    occ_demand_slope: float = 0.015
    occ_discharge_slope: float = 0.035
    offload_occ_slope: float = 8.0
    offload_occ_base: float = 0.88
    pressure_base: float = 0.8
    pressure_wait_weight: float = 0.2
    pressure_occ_weight: float = 0.5
    pressure_occ_base: float = 0.8
    pressure_occ_scale: float = 0.1
    within4_intercept: float = 1.02
    within4_slope: float = 0.45
    within4_scale: float = 0.20
    within4_min: float = 0.05
    within4_max: float = 0.85
    wf_drain_base: float = 0.02
    wf_drain_intensity: float = 0.06
    wf_recovery_rate: float = 0.1
    wf_pool_min: float = 0.5
    wf_pool_max: float = 1.5
    reneg_occ_threshold: float = 0.95
    reneg_share_inc_high: float = 0.06
    reneg_share_inc_low: float = 0.03
    init_n_lhns: int = 5
    init_efficiency_gap: float = 0.10
    init_agreement_clock: int = 5
    init_lhn_nwau_base: float = 100.0
    jurisdiction_pressure_threshold: float = 1.1
    jurisdiction_discharge_target: float = 0.9
    jurisdiction_noise_scale: float = 0.8
    jurisdiction_noise_base: float = 0.03
    decision_threshold: float = 0.5
    venue_shift_revenue_scale: float = 100.0
    reneg_share_clip_min: float = 0.40
    reneg_share_clip_max: float = 0.70
    minutes_per_hour: float = 60.0
    hours_per_day: float = 24.0
    discharge_clip_min: float = 0.75
    discharge_clip_max: float = 1.50
    occ_clip_min: float = 0.78
    occ_clip_max: float = 0.98
    offload_clip_min: float = 5.0
    offload_clip_max: float = 120.0
    capacity_scalar: float = 10.0
    auditor_suspicion_increment: float = 0.03
    auditor_suspicion_decay: float = 0.95
    auditor_pressure_base: float = 0.25
    mode_stress_threshold: float = 1.25
    mode_crisis_threshold: float = 1.5
    mode_normal_recovery_threshold: float = 1.05
    mode_recovery_trigger_threshold: float = 1.3
    mode_normal_final_threshold: float = 1.1
    mode_crisis_relapse_threshold: float = 1.4
    queuing_outside_utility: float = -100.0
    queuing_init_prob: float = 0.5
    demand_shift_slope: float = 1.04
    demand_shift_base: float = 0.35
    demand_invest_base: float = 0.96
    demand_scale: float = 2.0
    wait_time_cap: float = 1440.0
    wait_time_min: float = 5.0


@struct.dataclass
class BehavioralParamsJax:
    """Hidden coefficients for subgame payoffs (JAX version)."""

    # Definition Game
    def_realism_benefit_base: float = 0.5
    def_realism_eg_weight: float = 0.8
    def_realism_pr_weight: float = 0.4
    def_realism_cost_base: float = 0.25
    def_realism_ps_weight: float = 0.35
    def_strict_benefit_base: float = 0.35
    def_strict_ps_weight: float = 0.45
    def_strict_cost_base: float = 0.30
    def_strict_pr_weight: float = 0.50

    # Bargaining Game
    barg_converge_gain_base: float = 0.45
    barg_converge_pr_weight: float = 0.25
    barg_converge_pc_weight: float = 0.20
    barg_conflict_cost_base: float = 0.55
    barg_conflict_pr_weight: float = 0.90
    barg_narrative_gain_base: float = 0.25
    barg_narrative_ps_weight: float = 0.50

    # Cost Shifting Game
    shift_coop_gain_base: float = 0.55
    shift_coop_eg_weight: float = 0.45
    shift_gain_base: float = 0.35
    shift_eg_weight: float = 0.75
    shift_csi_weight: float = 1.0
    shift_pr_cost_weight: float = 0.65

    # Renegotiation Game
    reneg_cth_fallout_weight: float = 0.8
    reneg_state_failure_weight: float = 0.6
    reneg_concede_agree_cost: float = 0.1
    reneg_concede_holdup_cost: float = 0.3
    reneg_concede_agree_gain: float = 0.2
    reneg_concede_holdup_gain: float = 0.5
    def_row_realism_offset: float = 0.15
    def_row_strict_offset: float = 0.45
    def_col_realism_offset: float = 0.15
    def_col_realism_cost: float = 0.20
    def_col_strict_cost_1: float = 0.35
    def_col_strict_cost_2: float = 0.55
    barg_row_converge_ps_penalty: float = 0.10
    barg_row_converge_base_penalty: float = 0.25
    barg_row_converge_pr_penalty: float = 0.15
    barg_row_narrative_pr_penalty: float = 0.10
    barg_col_converge_ps_penalty: float = 0.05
    barg_col_converge_base_penalty: float = 0.30
    barg_col_converge_pr_penalty: float = 0.20
    barg_col_narrative_penalty: float = 0.20
    shift_row_coop_penalty: float = 0.25
    shift_row_shift_pr_penalty: float = 0.35
    shift_row_shift_base_penalty: float = 0.60
    shift_row_shift_pr_heavy_penalty: float = 1.00
    disc_benefit_base: float = 0.70
    disc_benefit_slope: float = 0.80
    disc_cost_base: float = 0.30
    disc_cost_slope: float = 0.10
    disc_pr_penalty_weight: float = 0.45
    disc_row_coop_penalty: float = 0.40
    disc_row_frag_base_penalty: float = 0.25
    disc_row_frag_heavy_penalty: float = 0.70
    disc_row_frag_pr_penalty: float = 1.10
    disc_col_coop_penalty: float = 0.35
    disc_col_frag_base_penalty: float = 0.25
    disc_col_frag_heavy_penalty: float = 0.70
    disc_col_frag_pr_penalty: float = 1.00
    gov_safety_gain_base: float = 0.55
    gov_safety_gain_slope: float = 0.35
    gov_int_cost_base: float = 0.20
    gov_int_cost_slope: float = 0.35
    gov_frag_risk_base: float = 0.40
    gov_frag_risk_slope: float = 0.60
    gov_row_safety_penalty: float = 0.25
    gov_row_frag_bonus: float = 0.10
    gov_row_frag_penalty: float = 0.45
    gov_col_safety_penalty_1: float = 0.10
    gov_col_safety_penalty_2: float = 0.20
    gov_col_frag_penalty_1: float = 0.35
    gov_col_frag_penalty_2: float = 0.55
    aged_coord_benefit_base: float = 0.6
    aged_coord_benefit_slope: float = 0.4
    aged_frag_cost_weight: float = 0.5
    ndis_coord_benefit_base: float = 0.5
    ndis_coord_benefit_slope: float = 0.5
    ndis_frag_cost_weight: float = 0.6
    coding_upcode_gain_base: float = 0.3
    coding_upcode_gain_slope: float = 0.7
    coding_penalty_weight: float = 0.8
    coding_audit_cost: float = 0.2
    coding_recovery_weight: float = 0.4
    comp_leakage_base: float = 0.40
    comp_leakage_slope: float = 0.70
    comp_admin_base: float = 0.18
    comp_admin_slope: float = 0.45
    comp_row_tight_bonus: float = 0.15
    comp_row_light_penalty: float = 0.80
    comp_col_tight_penalty: float = 0.10
    comp_col_tight_ai_penalty: float = 0.35
    comp_col_light_base_bonus: float = 0.20
    venue_shift_gain_base: float = 0.25
    venue_shift_gain_eg_weight: float = 0.5
    venue_shift_gain_pr_weight: float = 0.3
    venue_strict_penalty: float = 0.45
    venue_enforce_cost: float = 0.15
    venue_col_strict_penalty_weight: float = 0.15
    venue_col_strict_base_bonus: float = 0.10
    comp_capture_base: float = 0.4
    comp_capture_slope: float = 0.6
    comp_cost_base: float = 0.3
    comp_cost_slope: float = 0.2


@struct.dataclass
class PolicyParamsJax:
    """Hidden coefficients for rule logic (JAX version)."""

    cap_soft_multiplier: float = 0.5
    audit_prop_multiplier: float = 2.0
    audit_threshold_penalty_high: float = 3.0
    audit_threshold_penalty_low: float = 0.1
    eligibility_venue_shift_impact: float = 0.10
    eligibility_abf_share_min: float = 0.5
    recon_bailout_increment: float = 0.05
    recon_safety_net_generosity: float = 1.5
    iv_pooled_csi_mult: float = 0.75
    iv_pooled_csi_min: float = 0.05
    iv_pooled_csi_max: float = 0.60
    iv_ucc_frag_mult: float = 0.80
    iv_ucc_frag_min: float = 0.60
    iv_ucc_frag_max: float = 1.50
    iv_nep_realism_inc: float = 0.03
    iv_nep_realism_regional_inc: float = 0.04
    iv_nep_realism_remote_inc: float = 0.05
    iv_nep_realism_min: float = 0.6
    iv_nep_realism_max: float = 1.0
    iv_aged_ndis_delay_mult: float = 0.90
    iv_aged_ndis_delay_min: float = 0.6
    iv_aged_ndis_delay_max: float = 1.4
    iv_cap_cumulative_growth: float = 0.070
    iv_audit_relief_audit_mult: float = 0.70
    iv_audit_relief_audit_min: float = 0.05
    iv_audit_relief_audit_max: float = 1.0
    iv_audit_relief_burden_mult: float = 0.8
    iv_audit_relief_burden_min: float = 0.05
    iv_audit_relief_burden_max: float = 0.6


@struct.dataclass
class ParamsJax(ParamsGenerated):
    """JAX-compatible simulation parameters.

    This class extends the auto-generated scalar parameters with runtime
    objects and JAX-native rules.
    """

    # Grouped coefficients
    ops: OperationalParamsJax = struct.field(default_factory=OperationalParamsJax)
    behavior: BehavioralParamsJax = struct.field(default_factory=BehavioralParamsJax)
    policy: PolicyParamsJax = struct.field(default_factory=PolicyParamsJax)

    # Modular Rules (JAX-compatible PyTrees)
    cap_rule: Any = struct.field(default_factory=lambda: None)
    audit_rule: Any = struct.field(default_factory=lambda: None)
    eligibility_rule: Any = struct.field(default_factory=lambda: None)
    reconciliation_rule: Any = struct.field(default_factory=lambda: None)

    # Economic Spine (optional JAX arrays)
    spine: EconomicSpineJax | None = None
    economic_spine: str | None = struct.field(default=None, pytree_node=False)  # alias/placeholder

    def replace(self, **kwargs: Any) -> ParamsJax:
        """Flax-compatible field replacement."""
        return struct.replace(self, **kwargs)

    @classmethod
    def from_yaml(cls, path: Path | str) -> ParamsJax:
        """Loads parameters from a YAML file via Pydantic for validation."""
        import yaml

        from .params import Params

        with open(path) as f:
            data = yaml.safe_load(f)

        # 1. Flatten the legacy groups if they exist
        flat_data = {}
        for k, v in data.items():
            if isinstance(v, dict) and k not in {"ops", "behavior", "policy"}:
                flat_data.update(v)
            else:
                flat_data[k] = v

        # 2. Use Pydantic to validate and handle nesting
        p_pydantic = Params(**flat_data)
        return p_pydantic.to_params_jax()


# Backwards-compatible alias (many callers/tests still import `Params` from this module).
Params = ParamsJax


class BaselineProvider:
    """
    Manages loading of the automated data spine and baseline parameters.

    Provides a centralized interface for synchronizing empirical data into
    the JAX simulation environment.
    """

    @staticmethod
    def load_spine(
        path: Path | str = "data/calibration/historical_normalized.csv",
    ) -> EconomicSpineJax:
        """
        Loads the economic spine (NEP, WPI) from a CSV file.

        Uses Polars if available, otherwise falls back to Pandas.
        """
        required = {"year", "nep_per_nwau", "wpi_health_index"}
        if pl is None:
            import pandas as pd

            df_pd = pd.read_csv(path)
            missing = required - set(df_pd.columns)
            if missing:
                raise ValueError(f"Spine missing required columns: {sorted(missing)}")
            return EconomicSpineJax(
                years=jnp.array(df_pd["year"].to_numpy().astype(jnp.int32)),
                nep_per_nwau=jnp.array(df_pd["nep_per_nwau"].to_numpy()),
                wpi_health_index=jnp.array(df_pd["wpi_health_index"].to_numpy()),
            )

        df = pl.read_csv(path)
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Spine missing required columns: {sorted(missing)}")
        return EconomicSpineJax(
            years=jnp.array(df["year"].to_numpy().astype(jnp.int32)),
            nep_per_nwau=jnp.array(df["nep_per_nwau"].to_numpy()),
            wpi_health_index=jnp.array(df["wpi_health_index"].to_numpy()),
        )

    @classmethod
    def get_baseline(cls, config_path: str = "configs/defaults.yaml") -> tuple[ParamsJax, StateJax]:
        """
        Retrieves baseline parameters and state for a new simulation run.
        """
        from nhra_gt.engine_jax import baseline_state_jax

        params = ParamsJax.from_yaml(config_path)
        # Check if spine exists
        spine_path = Path("data/calibration/historical_normalized.csv")
        if spine_path.exists():
            try:
                spine = cls.load_spine(spine_path)
            except ValueError as exc:
                logger.warning("Skipping spine load: %s", exc)
            else:
                params = params.replace(spine=spine)

        state = baseline_state_jax(2025, params)
        return params, state


@struct.dataclass
class LhnState:
    """
    Granular state for a single Local Hospital Network (LHN).

    Represents the operational and strategic status of a hospital cluster,
    including its pressure, occupancy, and internal choices.
    """

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
        """Flax-compatible field replacement."""
        return struct.replace(self, **kwargs)


@struct.dataclass
class JurisdictionState:
    """
    Granular state for a single Jurisdiction (State/Territory).

    Aggregates LHNs and manages jurisdictional-level fiscal and political state.
    """

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
        """Flax-compatible field replacement."""
        return struct.replace(self, **kwargs)


@struct.dataclass
class JurisdictionStateJax:
    """JAX-native jurisdiction state."""

    id: Any
    reconciliation_balance: Any = 0.0
    bailout_expectation: Any = 0.0
    political_capital: Any = 1.0
    effective_cth_share: Any = 0.38
    efficiency_gap: Any = 0.10
    equity_index: Any = 1.0
    total_block_revenue: Any = 0.0
    lhn_states: Any = None  # Vectorized


@struct.dataclass
class StateJax:
    """
    JAX-compatible simulation state (Global Orchestrator).

    The root PyTree for the entire simulation state. It contains both global
    aggregates and hierarchical jurisdictional/LHN states.
    """

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

    # ... (other orchestrator state)
    metrics: MetricsJax = struct.field(default_factory=MetricsJax)

    def replace(self, **kwargs: Any) -> StateJax:
        """Flax-compatible field replacement."""
        return struct.replace(self, **kwargs)


# Aliases for hierarchical modeling
State = StateJax
ConstitutionalStateJax = StateJax
JurisdictionState = JurisdictionStateJax
LhnStateJax = LhnState
