"""
Domain model for Simulation Parameters (Pydantic).

This module defines the validation schema for simulation parameters using Pydantic,
serving as the user-facing API for configuration and tooling. It includes logic
to convert these validated parameters into JAX-compatible structures.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from nhra_gt.domain.state import ParamsJax


class OperationalParams(BaseModel):
    """Hidden coefficients for system dynamics."""

    # Workforce
    wf_drain_max: float = Field(default=0.2, description="Max workforce drain per month")
    wf_drain_min: float = Field(default=0.1, description="Min workforce drain per month")
    wf_comp_drain: float = Field(default=0.1, description="Workforce drain from competition")
    wf_impact_weight: float = Field(
        default=0.5, description="Sensitivity of discharge to workforce"
    )

    # Interface effects
    aged_coord_effect: float = 0.95
    aged_frag_effect: float = 1.02
    ndis_coord_effect: float = 0.96
    ndis_frag_effect: float = 1.03
    disc_coord_effect: float = 0.98
    disc_frag_effect: float = 1.01

    # Transitions
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

    # Workforce
    wf_drain_base: float = 0.02
    wf_drain_intensity: float = 0.06
    wf_recovery_rate: float = 0.1
    wf_pool_min: float = 0.5
    wf_pool_max: float = 1.5

    # Renegotiation (Operational side)
    reneg_occ_threshold: float = 0.95
    reneg_share_inc_high: float = 0.06
    reneg_share_inc_low: float = 0.03

    # Initial Conditions
    init_n_lhns: int = 5
    init_efficiency_gap: float = 0.10
    init_agreement_clock: int = 5
    init_lhn_nwau_base: float = 100.0

    # Jurisdiction Step
    jurisdiction_pressure_threshold: float = 1.1
    jurisdiction_discharge_target: float = 0.9
    jurisdiction_noise_scale: float = 0.8
    jurisdiction_noise_base: float = 0.03
    decision_threshold: float = 0.5

    # Step JAX
    venue_shift_revenue_scale: float = 100.0
    reneg_share_clip_min: float = 0.40
    reneg_share_clip_max: float = 0.70

    # Time
    minutes_per_hour: float = 60.0
    hours_per_day: float = 24.0

    # Clipping Bounds
    discharge_clip_min: float = 0.75
    discharge_clip_max: float = 1.50
    occ_clip_min: float = 0.78
    occ_clip_max: float = 0.98
    offload_clip_min: float = 5.0
    offload_clip_max: float = 120.0
    capacity_scalar: float = 10.0

    # Auditor
    auditor_suspicion_increment: float = 0.03
    auditor_suspicion_decay: float = 0.95
    auditor_pressure_base: float = 0.25

    # Mode Thresholds
    mode_stress_threshold: float = 1.25
    mode_crisis_threshold: float = 1.5
    mode_normal_recovery_threshold: float = 1.05
    mode_recovery_trigger_threshold: float = 1.3
    mode_normal_final_threshold: float = 1.1
    mode_crisis_relapse_threshold: float = 1.4

    # Queuing
    queuing_outside_utility: float = -100.0
    queuing_init_prob: float = 0.5
    demand_shift_slope: float = 1.04
    demand_shift_base: float = 0.35
    demand_invest_base: float = 0.96
    demand_scale: float = 2.0
    wait_time_cap: float = 1440.0
    wait_time_min: float = 5.0


class BehavioralParams(BaseModel):
    """Hidden coefficients for subgame payoffs."""

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

    # Definition Matrix Offsets
    def_row_realism_offset: float = 0.15
    def_row_strict_offset: float = 0.45
    def_col_realism_offset: float = 0.15
    def_col_realism_cost: float = 0.20
    def_col_strict_cost_1: float = 0.35
    def_col_strict_cost_2: float = 0.55

    # Bargaining Matrix Offsets
    barg_row_converge_ps_penalty: float = 0.10
    barg_row_converge_base_penalty: float = 0.25
    barg_row_converge_pr_penalty: float = 0.15
    barg_row_narrative_pr_penalty: float = 0.10
    barg_col_converge_ps_penalty: float = 0.05
    barg_col_converge_base_penalty: float = 0.30
    barg_col_converge_pr_penalty: float = 0.20
    barg_col_narrative_penalty: float = 0.20

    # Cost Shifting Matrix Offsets
    shift_row_coop_penalty: float = 0.25
    shift_row_shift_pr_penalty: float = 0.35
    shift_row_shift_base_penalty: float = 0.60
    shift_row_shift_pr_heavy_penalty: float = 1.00

    # Discharge Coordination
    disc_benefit_base: float = 0.70
    disc_benefit_slope: float = 0.80
    disc_cost_base: float = 0.30
    disc_cost_slope: float = 0.10
    disc_pr_penalty_weight: float = 0.45
    # Discharge Matrix Offsets
    disc_row_coop_penalty: float = 0.40
    disc_row_frag_base_penalty: float = 0.25
    disc_row_frag_heavy_penalty: float = 0.70
    disc_row_frag_pr_penalty: float = 1.10
    disc_col_coop_penalty: float = 0.35
    disc_col_frag_base_penalty: float = 0.25
    disc_col_frag_heavy_penalty: float = 0.70
    disc_col_frag_pr_penalty: float = 1.00

    # Governance Integration
    gov_safety_gain_base: float = 0.55
    gov_safety_gain_slope: float = 0.35
    gov_int_cost_base: float = 0.20
    gov_int_cost_slope: float = 0.35
    gov_frag_risk_base: float = 0.40
    gov_frag_risk_slope: float = 0.60
    # Governance Matrix Offsets
    gov_row_safety_penalty: float = 0.25
    gov_row_frag_bonus: float = 0.10
    gov_row_frag_penalty: float = 0.45
    gov_col_safety_penalty_1: float = 0.10
    gov_col_safety_penalty_2: float = 0.20
    gov_col_frag_penalty_1: float = 0.35
    gov_col_frag_penalty_2: float = 0.55

    # Aged Care & NDIS
    aged_coord_benefit_base: float = 0.6
    aged_coord_benefit_slope: float = 0.4
    aged_frag_cost_weight: float = 0.5
    ndis_coord_benefit_base: float = 0.5
    ndis_coord_benefit_slope: float = 0.5
    ndis_frag_cost_weight: float = 0.6

    # Coding Audit
    coding_upcode_gain_base: float = 0.3
    coding_upcode_gain_slope: float = 0.7
    coding_penalty_weight: float = 0.8
    coding_audit_cost: float = 0.2
    coding_recovery_weight: float = 0.4

    # Compliance
    comp_leakage_base: float = 0.40
    comp_leakage_slope: float = 0.70
    comp_admin_base: float = 0.18
    comp_admin_slope: float = 0.45
    # Compliance Matrix Offsets
    comp_row_tight_bonus: float = 0.15
    comp_row_light_penalty: float = 0.80
    comp_col_tight_penalty: float = 0.10
    comp_col_tight_ai_penalty: float = 0.35
    comp_col_light_base_bonus: float = 0.20

    # Venue Shifting
    venue_shift_gain_base: float = 0.25
    venue_shift_gain_eg_weight: float = 0.5
    venue_shift_gain_pr_weight: float = 0.3
    venue_strict_penalty: float = 0.45
    venue_enforce_cost: float = 0.15
    venue_col_strict_penalty_weight: float = 0.15
    venue_col_strict_base_bonus: float = 0.10

    # Competition
    comp_capture_base: float = 0.4
    comp_capture_slope: float = 0.6
    comp_cost_base: float = 0.3
    comp_cost_slope: float = 0.2


class PolicyParams(BaseModel):
    """Hidden coefficients for rule logic."""

    cap_soft_multiplier: float = 0.5
    audit_prop_multiplier: float = 2.0
    audit_threshold_penalty_high: float = 3.0
    audit_threshold_penalty_low: float = 0.1
    eligibility_venue_shift_impact: float = 0.10
    eligibility_abf_share_min: float = 0.5
    recon_bailout_increment: float = 0.05
    recon_safety_net_generosity: float = 1.5

    # Intervention Multipliers
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


class Params(BaseModel):
    """Pydantic Params wrapper for validation and tooling."""

    # Operational, Behavioral & Policy Groupings
    ops: OperationalParams = Field(default_factory=OperationalParams)
    behavior: BehavioralParams = Field(default_factory=BehavioralParams)
    policy: PolicyParams = Field(default_factory=PolicyParams)

    rurality_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    remote_weight: float = Field(default=0.07, ge=0.0, le=1.0)
    nominal_cth_share_target: float = Field(default=0.45, ge=0.0, le=1.0)
    effective_cth_share_base: float = Field(default=0.38, ge=0.0, le=1.0)

    nep_annual_growth: float = Field(default=0.03, ge=-1.0, le=1.0)
    input_cost_annual_growth: float = Field(default=0.04, ge=-1.0, le=1.0)
    demand_base: float = Field(default=0.85, ge=0.0, le=10.0)
    avoidable_ed_share: float = Field(default=0.18, ge=0.0, le=1.0)

    discharge_delay_base: float = Field(default=1.0, ge=0.0, le=10.0)
    bed_capacity_index: float = Field(default=1.0, ge=0.0, le=10.0)
    capacity_lag: float = Field(default=0.15, ge=0.0, le=10.0)
    expansion_lag: float = Field(default=0.10, ge=0.0, le=10.0)
    contraction_lag: float = Field(default=0.20, ge=0.0, le=10.0)
    adjustment_cost_beta: float = Field(default=5.0, ge=0.0, le=1e6)

    cost_shifting_intensity: float = Field(default=0.35, ge=0.0, le=10.0)
    fragmentation_index: float = Field(default=1.0, ge=0.0, le=10.0)
    audit_pressure: float = Field(default=0.50, ge=0.0, le=10.0)
    admin_burden_weight: float = Field(default=0.25, ge=0.0, le=10.0)
    cannibalization_beta: float = Field(default=0.10, ge=0.0, le=10.0)

    block_funding_base: float = Field(default=0.15, ge=0.0, le=1.0)
    shifting_friction: float = Field(default=0.05, ge=0.0, le=10.0)

    signal_lag_months: int = Field(default=1, ge=0, le=24)
    claims_lag_months: int = Field(default=3, ge=0, le=24)

    occupancy_base: float = Field(default=0.88, ge=0.0, le=10.0)
    offload_base_min: float = Field(default=18.0, ge=0.0, le=1e6)
    within4_base: float = Field(default=0.53, ge=0.0, le=1.0)

    rr_beta_pressure: float = Field(default=0.35, ge=0.0, le=10.0)
    rr_beta_offload: float = Field(default=0.015, ge=0.0, le=10.0)
    offload_threshold_min: float = Field(default=20.0, ge=0.0, le=1e6)

    tau: float = Field(default=0.25, ge=0.0, le=10.0)
    bargaining_cost: float = Field(default=0.12, ge=0.0, le=10.0)
    political_salience: float = Field(default=0.30, ge=0.0, le=10.0)

    gp_out_of_pocket: float = Field(default=40.0, ge=0.0, le=1e6)
    gp_wait_time_min: float = Field(default=15.0, ge=0.0, le=1e6)
    patient_time_value_hour: float = Field(default=25.0, ge=0.0, le=1e6)

    cap_growth: float = Field(default=0.065, ge=0.0, le=10.0)
    has_cumulative_cap: bool = False

    cap_rule_type: int = Field(default=0, ge=0, le=1)
    audit_rule_type: int = Field(default=0, ge=0, le=1)
    orchestration_mode: int = Field(default=0, ge=0, le=10)
    equilibrium_selection_rule: str = "nash"
    isolated_game: str | None = None
    use_stage_game_equilibria: bool = True

    use_equilibrium_bargaining: bool = False
    use_quantal_response: bool = False
    qre_lambda: float = Field(default=4.0, ge=0.0, le=1e6)
    use_burden_feedback: bool = False
    burden_to_throughput_beta: float = Field(default=0.06, ge=0.0, le=10.0)
    noise_sd: float = Field(default=0.03, ge=0.0, le=10.0)

    model_config = ConfigDict(validate_assignment=True)

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> Params:
        """Creates a Params object from a potentially flat dictionary."""
        ops_fields = OperationalParams.model_fields.keys()
        behavior_fields = BehavioralParams.model_fields.keys()
        policy_fields = PolicyParams.model_fields.keys()

        # Extract nested structures if present as flat keys
        ops_data = {k: data.pop(k) for k in list(data.keys()) if k in ops_fields}
        behavior_data = {k: data.pop(k) for k in list(data.keys()) if k in behavior_fields}
        policy_data = {k: data.pop(k) for k in list(data.keys()) if k in policy_fields}

        # If data already had them as dicts, update with the popped values
        if "ops" in data and isinstance(data["ops"], dict):
            data["ops"].update(ops_data)
        elif ops_data:
            data["ops"] = ops_data

        if "behavior" in data and isinstance(data["behavior"], dict):
            data["behavior"].update(behavior_data)
        elif behavior_data:
            data["behavior"] = behavior_data

        if "policy" in data and isinstance(data["policy"], dict):
            data["policy"].update(policy_data)
        elif policy_data:
            data["policy"] = policy_data

        return cls(**data)

    def flatten(self) -> dict[str, Any]:
        """Returns a flat dictionary representation of all parameters."""
        data = self.model_dump()
        ops = data.pop("ops", {})
        behavior = data.pop("behavior", {})
        policy = data.pop("policy", {})
        return {**data, **ops, **behavior, **policy}

    def to_params_jax(self) -> ParamsJax:
        """Converts Pydantic Params to JAX-native ParamsJax."""
        from .state import BehavioralParamsJax, OperationalParamsJax, PolicyParamsJax

        data = self.model_dump()
        # Handle nested groups
        ops_data = data.pop("ops", {})
        behavior_data = data.pop("behavior", {})
        policy_data = data.pop("policy", {})

        return ParamsJax(
            ops=OperationalParamsJax(**ops_data),
            behavior=BehavioralParamsJax(**behavior_data),
            policy=PolicyParamsJax(**policy_data),
            **data,
        )

    def replace(self, **kwargs: Any) -> Params:
        """Pydantic-compatible field replacement."""
        return self.model_copy(update=kwargs)

