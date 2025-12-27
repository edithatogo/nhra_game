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
    demand = p.demand_base * demand_factor
    demand += noise
    return jnp.maximum(0.5, demand)


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
def ops_step_jax(
    s: StateJax,
    p: ParamsJax,
    strategies: Float[jnp.ndarray, "10"],
    demand: Float[jnp.ndarray, ""],
    month_growth_factor: float,
    offload_noise: Float[jnp.ndarray, ""],
) -> tuple[
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
    Float[jnp.ndarray, ""],
]:
    # AGED: F=0, C=1 (index 5)
    # NDIS: F=0, C=1 (index 6)
    # DISC: F=0, C=1 (index 4)
    aged_effect = jnp.where(strategies[5] == 1, 0.95, 1.02)
    ndis_effect = jnp.where(strategies[6] == 1, 0.96, 1.03)
    disc_effect = jnp.where(strategies[4] == 1, 0.98, 1.01)

    discharge = s.discharge_delay
    discharge *= (aged_effect * ndis_effect * disc_effect) ** month_growth_factor

    feedback_factor = jnp.exp(
        p.burden_to_throughput_beta * jnp.maximum(0.0, s.pressure - 1.0) * month_growth_factor
    )
    discharge = jnp.where(p.use_burden_feedback, discharge * feedback_factor, discharge)
    discharge = jnp.clip(discharge, 0.75, 1.50)

    capacity = s.current_capacity + p.capacity_lag * (s.target_capacity - s.current_capacity)
    wait_min = mm_s_queue_wait_jax(
        jnp.array(demand), 1.0 / jnp.maximum(1e-9, jnp.array(discharge)), jnp.array(capacity * 10.0)
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

    # Split keys for stochasticity
    k1, k2, k3 = jax.random.split(prng_key, 3)
    demand_noise = jax.random.normal(k1) * 0.02
    offload_noise = jax.random.normal(k2) * 0.8
    audit_random = jax.random.uniform(k3)

    demand = demand_step_jax(s, p, strategies, demand_noise)
    eff_gap, eff_share, bailout = policy_step_jax(s, p, strategies, mgf)
    discharge, capacity, wait_min, occ, off, pidx, w4 = ops_step_jax(
        s, p, strategies, demand, mgf, offload_noise
    )
    final_share, coding, recon, pol_cap_hit = pay_step_jax(
        s, p, strategies, eff_share, mgf, audit_random
    )

    # SIGNAL_QUALITY is index 9
    sig_quality = strategies[9]
    # BARG is index 2
    barg_agree = strategies[2]

    pol_cap_change = (
        -pol_cap_hit
        - (1.0 - sig_quality) * 0.2 * mgf
        + jnp.where(barg_agree == 1, 0.05, -0.10) * mgf
        - jnp.where(wait_min > 240, 0.05 * (wait_min / 240.0), 0.0)
    )
    pol_cap = jnp.clip(s.political_capital + pol_cap_change, 0.0, 2.0)

    # DEF is index 1
    equity_change = -(jnp.where(strategies[1] == 0, 0.01, 0.0)) * mgf  # DEF="E" is 0
    equity_change -= jnp.where(s.system_mode == 2, 0.02 * mgf, 0.0)
    equity = jnp.clip(s.equity_index + equity_change, 0.5, 1.5)

    # Update accumulated metrics
    new_metrics = MetricsJax(
        cumulative_pressure=s.metrics.cumulative_pressure + pidx * mgf,
        cumulative_budget_variance=s.metrics.cumulative_budget_variance
        + jnp.abs(final_share - p.nominal_cth_share_target) * mgf,
        max_occupancy=jnp.maximum(s.metrics.max_occupancy, occ),
        min_within4=jnp.minimum(s.metrics.min_within4, w4),
    )

    # Handle time rollover
    def rollover():
        return 1, s.year + 1

    def no_rollover():
        return s.month + 1, s.year

    next_m, next_y = lax.cond(s.month < 12, no_rollover, rollover)

    return StateJax(
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
        system_mode=update_system_mode_jax(s, p, pidx),
        target_capacity=s.target_capacity,
        current_capacity=capacity,
        equity_index=equity,
        reconciliation_balance=recon,
        bailout_expectation=bailout,
        coding_intensity=coding,
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
