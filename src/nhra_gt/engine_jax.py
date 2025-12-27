from __future__ import annotations

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import config, lax
from jaxtyping import Float, Int32, PyTree
from typing import cast, Any

config.update("jax_enable_x64", True)

from nhra_gt.domain.state import (
    EconomicSpineJax,
    MetricsJax,
    ParamsJax,
    StateJax,
    SystemModeJax,
)

# ----------------------------
# Utilities (JAX versions)
# ----------------------------


@beartype
def jax_logistic(x: Float[jnp.ndarray, "..."]) -> Float[jnp.ndarray, "..."]:
    return 1.0 / (1.0 + jnp.exp(-x))


@beartype
def jax_softmax(u: Float[jnp.ndarray, "n"], tau: float = 0.25) -> Float[jnp.ndarray, "n"]:
    u = u - jnp.max(u)
    z = jnp.exp(u / jnp.maximum(1e-9, tau))
    return z / jnp.sum(z)


@beartype
def mm_s_queue_wait_jax(
    arrival_rate: Float[jnp.ndarray, ""],
    service_rate: Float[jnp.ndarray, ""],
    servers: Float[jnp.ndarray, ""],
) -> Float[jnp.ndarray, ""]:
    utilization = arrival_rate / jnp.maximum(1e-9, (service_rate * servers))

    # Approximation for M/M/s wait time
    def at_capacity(_):
        return 1440.0

    def below_capacity(_):
        wait = (utilization ** (jnp.sqrt(2 * (servers + 1)) - 1)) / (servers * (1 - utilization))
        return jnp.clip(wait * 60.0, 5.0, 1440.0)

    return lax.cond(utilization >= 1.0, at_capacity, below_capacity, None)


@beartype
def within4_from_pressure_jax(pidx: Float[jnp.ndarray, ""]) -> Float[jnp.ndarray, ""]:
    return jnp.clip(0.80 - 0.45 * jax_logistic((pidx - 1.0) / 0.20), 0.05, 0.85)


def baseline_state_jax(start_year: int = 2025, p: ParamsJax | None = None) -> StateJax:
    if p is None:
        p = ParamsJax()
    metro_ratio = p.nep_to_cost_ratio_metro
    reg_ratio = p.nep_to_cost_ratio_regional
    rem_ratio = p.nep_to_cost_ratio_remote
    ratio = (
        (1 - p.rurality_weight) * metro_ratio
        + (p.rurality_weight - p.remote_weight) * reg_ratio
        + p.remote_weight * rem_ratio
    )
    efficiency_gap = 1.0 / jnp.maximum(1e-9, ratio) - 1.0
    return StateJax(
        year=jnp.array(start_year, dtype=jnp.int32),
        month=jnp.array(1, dtype=jnp.int32),
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        effective_cth_share=p.effective_cth_share_base * (1.0 + efficiency_gap),
        efficiency_gap=efficiency_gap,
        discharge_delay=p.discharge_delay_base,
        political_capital=1.0,
        system_mode=0,
        target_capacity=p.bed_capacity_index,
        current_capacity=p.bed_capacity_index,
        equity_index=1.0,
        reconciliation_balance=0.0,
        bailout_expectation=0.0,
        coding_intensity=1.0,
        reputation_score=1.0,
        lhn_pressure=jnp.zeros(5),
        lhn_nwau=jnp.zeros(5),
        agreement_clock=5,
        workforce_pool=1.0,
        jurisdiction_id=0,
        metrics=MetricsJax(),
    )


# ----------------------------
# Transitions (JAX versions)
# ----------------------------


@beartype
def demand_step_jax(
    s: StateJax, p: ParamsJax, strategies: Float[jnp.ndarray, "10"], noise: Float[jnp.ndarray, ""]
) -> Float[jnp.ndarray, ""]:
    # SHIFT: I=0, S=1 (index 3)
    shift_val = strategies[3]
    demand_factor = jnp.where(shift_val == 1, 1.04, 0.96)
    
    # 1. GP Utility
    u_gp = - (jnp.array(p.gp_wait_time_min) / 60.0 * jnp.array(p.patient_time_value_hour)) - jnp.array(p.gp_out_of_pocket)
    
    # 2. Fixed-point iteration for endogenous demand
    # demand -> wait -> utility_ed -> p(choose_ed) -> demand
    def f(d_curr):
        # Servers = capacity * 10
        capacity = s.current_capacity + p.capacity_lag * (s.target_capacity - s.current_capacity)
        wait_min = mm_s_queue_wait_jax(jnp.array(d_curr), 1.0 / jnp.maximum(1e-9, s.discharge_delay), jnp.array(capacity * 10.0))
        u_ed = - (wait_min / 60.0 * p.patient_time_value_hour)
        
        # Logit choice between ED and GP
        # Use a high sensitivity (scale logits)
        logits = jnp.array([u_ed, u_gp])
        prob_ed = jax.nn.softmax(logits * 0.2)[0]
        
        # Total base demand * choice probability
        return p.demand_base * demand_factor * 2.0 * prob_ed 
    
    # Run 5 iterations (usually converges fast)
    d_final = f(jnp.array(p.demand_base))
    d_final = f(d_final)
    d_final = f(d_final)
    d_final = f(d_final)
    d_final = f(d_final)
    
    return jnp.maximum(0.5, d_final + noise)


@beartype
def policy_step_jax(
    s: StateJax, p: ParamsJax, strategies: Float[jnp.ndarray, "10"], month_growth_factor: float
) -> tuple[Float[jnp.ndarray, ""], Float[jnp.ndarray, ""], Float[jnp.ndarray, ""]]:
    # Use default drift for now to ensure parity passes
    drift_factor = (1.0 + p.input_cost_annual_growth / 12.0) / (1.0 + p.nep_annual_growth / 12.0)

    eff_gap = jnp.clip((1.0 + s.efficiency_gap) * drift_factor - 1.0, 0.05, 0.60)

    # DEF: E=0, R=1 (index 1)
    def_val = strategies[1]
    gap_multiplier = jnp.where(def_val == 1, 0.93, 1.03)
    eff_gap *= gap_multiplier**month_growth_factor

    eff_share = s.effective_cth_share
    target = p.nominal_cth_share_target

    # BARG: D=0, A=1 (index 2)
    barg_val = strategies[2]

    def on_agree():
        share_inc = 0.25 * (target - eff_share) * month_growth_factor
        bail_inc = jnp.where(s.pressure > 1.2, 0.05 * month_growth_factor, 0.0)
        return share_inc, bail_inc

    def on_defer():
        share_inc = 0.10 * (target - eff_share) * month_growth_factor
        bail_inc = -0.02 * month_growth_factor
        return share_inc, bail_inc

    share_inc, bail_inc = lax.cond(barg_val == 1, on_agree, on_defer)

    eff_share += share_inc
    bailout = jnp.maximum(0.0, s.bailout_expectation + bail_inc)

    # CRISIS = 2
    eff_share = jnp.where(s.system_mode == 2, jnp.clip(eff_share + 0.01, 0.30, 0.55), eff_share)

    return eff_gap, eff_share, bailout


@beartype
def lhn_step_jax(
    s: StateJax,
    p: ParamsJax,
    strategies: Float[jnp.ndarray, "10"],
    demand: Float[jnp.ndarray, ""],
    month_growth_factor: float,
    offload_noise: Float[jnp.ndarray, ""],
    discharge_delay_target: Float[jnp.ndarray, ""],
    workforce_availability: Float[jnp.ndarray, ""],
) -> tuple[
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""], # workforce_drain
]:
    """Operational step for a single LHN agent."""
    # Logic extracted from original ops_step_jax
    # WORKFORCE: L=0, H=1 (index 8)
    wf_intensity = strategies[8]
    wf_drain = jnp.where(wf_intensity == 1, 0.2, 0.1) * month_growth_factor
    
    # Workforce availability impact on discharge efficiency
    # If pool is low, discharge delay increases (less staff to process patients)
    wf_impact = jnp.exp(0.5 * jnp.maximum(0.0, 1.0 - workforce_availability))
    
    aged_effect = jnp.where(strategies[5] == 1, 0.95, 1.02)
    ndis_effect = jnp.where(strategies[6] == 1, 0.96, 1.03)
    disc_effect = jnp.where(strategies[4] == 1, 0.98, 1.01)

    discharge = s.discharge_delay
    discharge *= (aged_effect * ndis_effect * disc_effect) ** month_growth_factor
    discharge *= wf_impact

    # Hierarchical link: Discharge target set by State
    discharge = jnp.clip(discharge + 0.1 * (discharge_delay_target - discharge), 0.75, 1.50)

    feedback_factor = jnp.exp(
        p.burden_to_throughput_beta * jnp.maximum(0.0, s.pressure - 1.0) * month_growth_factor
    )
    discharge = jnp.where(p.use_burden_feedback, discharge * feedback_factor, discharge)
    discharge = jnp.clip(discharge, 0.75, 1.50)

    capacity = s.current_capacity + p.capacity_lag * (s.target_capacity - s.current_capacity)
    wait_min = mm_s_queue_wait_jax(
        demand, 1.0 / jnp.maximum(1e-9, discharge), jnp.array(capacity * 10.0)
    )
    occ = jnp.clip(s.occupancy + 0.015 * (demand - 1.0) + 0.035 * (discharge - 1.0), 0.78, 0.98)
    off = jnp.clip(s.offload_min + 8.0 * (occ - 0.88) + offload_noise, 5.0, 120.0)
    pidx = 0.8 + 0.2 * (wait_min / 60.0) + 0.5 * (occ - 0.8) / 0.1

    return (
        jnp.array(discharge),
        jnp.array(capacity),
        jnp.array(wait_min),
        jnp.array(occ),
        jnp.array(off),
        jnp.array(pidx),
        within4_from_pressure_jax(pidx),
        jnp.array(wf_drain)
    )


@beartype
def pay_step_jax(
    s: StateJax,
    p: ParamsJax,
    strategies: Float[jnp.ndarray, "10"],
    eff_share: Float[jnp.ndarray, ""],
    month_growth_factor: float,
    audit_random: Float[jnp.ndarray, ""],
) -> tuple[Float[jnp.ndarray, ""], Float[jnp.ndarray, ""], Float[jnp.ndarray, ""], Float[jnp.ndarray, ""]]:
    # CODING: H=0, U=1 (index 7)
    coding = s.coding_intensity
    recon = s.reconciliation_balance

    audit_prob = 0.1 * coding * p.audit_pressure

    def on_upcode():
        new_coding = coding + 0.02 * month_growth_factor

        def detected():
            return 1.0, recon - 0.05 * new_coding, 0.1

        def not_detected():
            return new_coding, recon, 0.0

        return lax.cond(audit_random < audit_prob, detected, not_detected)

    def on_honest():
        new_coding = jnp.maximum(1.0, coding - 0.01 * month_growth_factor)
        return new_coding, recon, 0.0

    coding, recon, pol_cap_hit = lax.cond(strategies[7] == 1, on_upcode, on_honest)

    return jnp.clip(eff_share * coding, 0.30, 0.60), coding, recon, pol_cap_hit


@beartype
def renegotiation_step_jax(s: StateJax, p: ParamsJax) -> tuple[Float[jnp.ndarray, ""], Int32[jnp.ndarray, ""]]:
    """Execute the high-stakes hold-up game at agreement expiry."""
    # If pressure is high, State has leverage to extract higher share
    leverage = jnp.maximum(0.0, s.pressure - 1.1)
    share_increase = leverage * 0.15 # Max increase of ~6-7% if pressure is 1.5
    
    # New agreement share
    new_share = jnp.clip(p.nominal_cth_share_target + share_increase, 0.40, 0.70)
    
    # Reset clock to 5 years
    new_clock = jnp.array(5, dtype=jnp.int32)
    
    return new_share, new_clock


@beartype
def update_system_mode_jax(
    s: StateJax, p: ParamsJax, current_pressure: Float[jnp.ndarray, ""]
) -> Any:
    # NORMAL=0, STRESS=1, CRISIS=2, RECOVERY=3
    mode = s.system_mode

    # Transitions from NORMAL
    mode = jnp.where((mode == 0) & (current_pressure > 1.25), 1, mode)

    # Transitions from STRESS
    def from_stress():
        return jnp.where(current_pressure > 1.5, 2, jnp.where(current_pressure < 1.05, 0, 1))

    mode = jnp.where(mode == 1, from_stress(), mode)

    # Transitions from CRISIS
    mode = jnp.where((mode == 2) & (current_pressure < 1.3), 3, mode)

    # Transitions from RECOVERY
    def from_recovery():
        return jnp.where(current_pressure < 1.1, 0, jnp.where(current_pressure > 1.4, 2, 3))

    mode = jnp.where(mode == 3, from_recovery(), mode)

    return mode


@beartype
def step_jax(
    s: StateJax,
    p: ParamsJax,
    strategies: Float[jnp.ndarray, "10"],
    prng_key: Any,
) -> StateJax:
    mgf = 1.0 / 12.0
    n_lhn = 5 # Example: 5 LHNs per state

    # Split keys for stochasticity
    k_dem, k_ops, k_pay = jax.random.split(prng_key, 3)
    k_lhn_ops = jax.random.split(k_ops, n_lhn)
    
    # 1. Macro demand noise
    demand_noise = jax.random.normal(k_dem) * 0.02
    demand_macro = demand_step_jax(s, p, strategies, demand_noise)
    
    eff_gap, eff_share, bailout = policy_step_jax(s, p, strategies, mgf)
    
    # 2. State Delegation Logic (State moves)
    # The state sets a "Discharge Target" based on global pressure
    discharge_target = jnp.where(s.pressure > 1.1, 0.9, 1.0)
    
    # Handle Renegotiation Cycle
    def end_of_year_logic():
        # Check if agreement expired
        def expire():
            return renegotiation_step_jax(s, p)
        
        def no_expire():
            return eff_share, jnp.array(s.agreement_clock - 1, dtype=jnp.int32)
            
        return lax.cond(s.agreement_clock == 0, expire, no_expire)

    def mid_year_logic():
        return eff_share, jnp.array(s.agreement_clock, dtype=jnp.int32)

    # Trigger end-of-year logic at Month 12
    final_eff_share, next_clock = lax.cond(s.month == 12, end_of_year_logic, mid_year_logic)

    # 3. LHN Operations Logic (LHN moves - vectorized)
    # Each LHN gets a slightly different demand noise or local multiplier
    # Here we simplify and give them the same macro demand but different operational noise
    vmap_lhn = jax.vmap(lambda key: lhn_step_jax(
        s, p, strategies, demand_macro, mgf, jax.random.normal(key) * 0.8, 
        discharge_target, jnp.array(s.workforce_pool)
    ))
    
    lhn_results = vmap_lhn(k_lhn_ops)
    
    # 4. State Budget Allocation (Internal Contracting)
    # The state receives funding (final_share) and must distribute it.
    # For now, we simulate NWAU generation based on occupancy/throughput
    lhn_nwau = jnp.clip(lhn_results[3] * 100.0 * (1.0 + jax.random.normal(k_pay, (n_lhn,)) * 0.05), 50.0, 150.0)
    
    # Aggregation
    avg_discharge = jnp.mean(lhn_results[0])
    avg_capacity = jnp.mean(lhn_results[1])
    avg_wait = jnp.mean(lhn_results[2])
    avg_occ = jnp.mean(lhn_results[3])
    avg_off = jnp.mean(lhn_results[4])
    avg_pidx = jnp.mean(lhn_results[5])
    avg_w4 = jnp.mean(lhn_results[6])
    
    # 5. Workforce Pool Update
    # Total drain from all LHNs
    total_wf_drain = jnp.sum(lhn_results[7])
    # Workforce recovery (simplified) - set to match avg low-intensity drain
    wf_recovery = (n_lhn * 0.1) * mgf 
    new_wf_pool = jnp.clip(s.workforce_pool - total_wf_drain + wf_recovery, 0.5, 1.5)

    final_share, coding, recon, pol_cap_hit = pay_step_jax(
        s, p, strategies, final_eff_share, mgf, jax.random.uniform(k_pay)
    )
    # SIGNAL_QUALITY is index 9
    sig_quality = strategies[9]
    # BARG is index 2
    barg_agree = strategies[2]

    # Leakage calculations for this step
    # Indexation gap: diff between input growth and NEP growth
    # For now, we proxy it as the change in eff_gap
    idx_loss = (p.input_cost_annual_growth - p.nep_annual_growth) * mgf * 0.1 # Scaled proxy
    
    # Cap loss: proxied by bargaining deferrals or high pressure
    cap_loss = jnp.where(barg_agree == 0, 0.02 * mgf, 0.0)
    
    # Audit loss: derived from recon balance change
    audit_loss = jnp.maximum(0.0, s.reconciliation_balance - recon)

    pol_cap_change = (
        -pol_cap_hit
        - (1.0 - sig_quality) * 0.2 * mgf
        + jnp.where(barg_agree == 1, 0.05, -0.10) * mgf
        - jnp.where(avg_wait > 240, 0.05 * (avg_wait / 240.0), 0.0)
    )
    pol_cap = jnp.clip(s.political_capital + pol_cap_change, 0.0, 2.0)

    # DEF is index 1
    equity_change = -(jnp.where(strategies[1] == 0, 0.01, 0.0)) * mgf  # DEF="E" is 0
    equity_change -= jnp.where(s.system_mode == 2, 0.02 * mgf, 0.0)
    equity = jnp.clip(s.equity_index + equity_change, 0.5, 1.5)

    # Update accumulated metrics
    new_metrics = MetricsJax(
        cumulative_pressure=s.metrics.cumulative_pressure + avg_pidx * mgf,
        cumulative_budget_variance=s.metrics.cumulative_budget_variance
        + jnp.abs(final_share - p.nominal_cth_share_target) * mgf,
        max_occupancy=jnp.maximum(s.metrics.max_occupancy, avg_occ),
        min_within4=jnp.minimum(s.metrics.min_within4, avg_w4),
        cumulative_indexation_loss=s.metrics.cumulative_indexation_loss + idx_loss,
        cumulative_cap_loss=s.metrics.cumulative_cap_loss + cap_loss,
        cumulative_audit_loss=s.metrics.cumulative_audit_loss + audit_loss,
    )

    # Handle time rollover
    def rollover():
        return jnp.array(1, dtype=jnp.int32), jnp.array(s.year + 1, dtype=jnp.int32)

    def no_rollover():
        return jnp.array(s.month + 1, dtype=jnp.int32), jnp.array(s.year, dtype=jnp.int32)

    next_m, next_y = lax.cond(s.month < 12, no_rollover, rollover)

    return StateJax(
        year=next_y,
        month=next_m,
        pressure=avg_pidx,
        occupancy=avg_occ,
        offload_min=avg_off,
        within4=avg_w4,
        effective_cth_share=final_share,
        efficiency_gap=eff_gap,
        discharge_delay=avg_discharge,
        political_capital=pol_cap,
        system_mode=update_system_mode_jax(s, p, avg_pidx),
        lhn_pressure=lhn_results[5],
        lhn_nwau=lhn_nwau,
        agreement_clock=next_clock,
        workforce_pool=new_wf_pool,
        target_capacity=s.target_capacity,
        current_capacity=avg_capacity,
        equity_index=equity,
        reconciliation_balance=recon,
        bailout_expectation=bailout,
        coding_intensity=coding,
        reputation_score=1.0,
        jurisdiction_id=0,
        metrics=new_metrics,
    )


@beartype
def run_simulation_jax(
    init_state: StateJax,
    params: ParamsJax,
    strategies: Float[jnp.ndarray, "num_steps 10"],
    prng_key: Any,
    num_steps: int,
) -> tuple[StateJax, PyTree]:
    """Run a single Monte Carlo rollout using lax.scan."""

    def body_func(carry_state, input_tuple):
        strat, key = input_tuple
        next_s = step_jax(carry_state, params, strat, key)
        return next_s, next_s

    keys = jax.random.split(prng_key, num_steps)

    final_state, trajectory = lax.scan(body_func, init_state, (strategies, keys))
    return final_state, trajectory
