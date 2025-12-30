from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import config, lax
from jaxtyping import Array, Float

from nhra_gt.domain.state import JurisdictionState, LhnState, MetricsJax, ParamsJax, StateJax
from nhra_gt.rules import initialize_rules
from nhra_gt.subgames.queuing import PatientUtilityParams, solve_queuing_equilibrium_jax

config.update("jax_enable_x64", True)

# ----------------------------
# Utilities (JAX versions)
# ----------------------------


@beartype
def jax_logistic(x: Float[Array, "*"]) -> Float[Array, "*"]:
    return 1.0 / (1.0 + jnp.exp(-x))


@beartype
def jax_softmax(u: Float[Array, "n"], tau: float = 0.25) -> Float[Array, "n"]:
    u = u - jnp.max(u)
    z = jnp.exp(u / jnp.maximum(1e-9, tau))
    return z / jnp.sum(z)


@beartype
def mm_s_queue_wait_jax(
    arrival_rate: Float[Array, ""],
    service_rate: Float[Array, ""],
    servers: Float[Array, ""],
) -> Float[Array, ""]:
    utilization = arrival_rate / jnp.maximum(1e-9, (service_rate * servers))

    # Approximation for M/M/s wait time
    def at_capacity(_):
        return 1440.0

    def below_capacity(_):
        wait = (utilization ** (jnp.sqrt(2 * (servers + 1)) - 1)) / (servers * (1 - utilization))
        return jnp.clip(wait * 60.0, 5.0, 1440.0)

    return lax.cond(utilization >= 1.0, at_capacity, below_capacity, None)


@beartype
def within4_from_pressure_jax(pidx: Float[Array, ""]) -> Float[Array, ""]:
    return jnp.clip(0.80 - 0.45 * jax_logistic((pidx - 1.0) / 0.20), 0.05, 0.85)


@beartype
def update_lag_buffers(
    s: StateJax,
    p: ParamsJax,
    current_pressure: Float[Array, ""],
    current_occupancy: Float[Array, ""],
    current_within4: Float[Array, ""],
    current_nwau: Float[Array, ""],
    current_eff_gap: Float[Array, ""],
    current_coding: Float[Array, ""],
) -> tuple[
    jnp.ndarray,
    jnp.ndarray,
    jnp.ndarray,
    jnp.ndarray,
    jnp.ndarray,
    jnp.ndarray,
    Float[Array, ""],
    Float[Array, ""],
    Float[Array, ""],
    Float[Array, ""],
    Float[Array, ""],
    Float[Array, ""],
]:
    """Rolls the lag buffers and extracts reported values based on configured lags."""
    new_buf_p = jnp.roll(s.lag_buffer_pressure, -1).at[-1].set(current_pressure)
    new_buf_o = jnp.roll(s.lag_buffer_occupancy, -1).at[-1].set(current_occupancy)
    new_buf_w = jnp.roll(s.lag_buffer_within4, -1).at[-1].set(current_within4)
    new_buf_n = jnp.roll(s.lag_buffer_nwau, -1).at[-1].set(current_nwau)
    new_buf_e = jnp.roll(s.lag_buffer_efficiency_gap, -1).at[-1].set(current_eff_gap)
    new_buf_c = jnp.roll(s.lag_buffer_coding, -1).at[-1].set(current_coding)

    sig_idx = 11 - jnp.clip(p.signal_lag_months, 0, 11)
    claim_idx = 11 - jnp.clip(p.claims_lag_months, 0, 11)

    rep_p = new_buf_p[sig_idx]
    rep_o = new_buf_o[sig_idx]
    rep_w = new_buf_w[sig_idx]
    rep_n = new_buf_n[claim_idx]
    rep_e = new_buf_e[claim_idx]
    rep_c = new_buf_c[claim_idx]

    return (
        new_buf_p,
        new_buf_o,
        new_buf_w,
        new_buf_n,
        new_buf_e,
        new_buf_c,
        rep_p,
        rep_o,
        rep_w,
        rep_n,
        rep_e,
        rep_c,
    )


def baseline_state_jax(start_year: int = 2025, p: ParamsJax | None = None) -> StateJax:
    if p is None:
        p = ParamsJax()
    p = initialize_rules(p)

    efficiency_gap = 0.10
    n_jurisdictions = 1
    n_lhns = 5

    def init_lhn(i):
        return LhnState(id=i)

    def init_jurisdiction(i):
        lhns = jax.vmap(init_lhn)(jnp.arange(n_lhns))
        return JurisdictionState(id=i, lhn_states=lhns)

    jurisdictions = jax.vmap(init_jurisdiction)(jnp.arange(n_jurisdictions))

    return StateJax(
        year=jnp.array(start_year, dtype=jnp.int32),
        month=jnp.array(1, dtype=jnp.int32),
        pressure=1.0,
        occupancy=p.occupancy_base,
        offload_min=p.offload_base_min,
        within4=p.within4_base,
        system_mode=0,
        workforce_pool=1.0,
        agreement_clock=5,
        jurisdictions=jurisdictions,
        lag_buffer_pressure=jnp.full(12, 1.0),
        lag_buffer_occupancy=jnp.full(12, p.occupancy_base),
        lag_buffer_within4=jnp.full(12, p.within4_base),
        lag_buffer_nwau=jnp.zeros(12),
        lag_buffer_efficiency_gap=jnp.full(12, efficiency_gap),
        lag_buffer_coding=jnp.full(12, 1.0),
        reported_pressure=1.0,
        reported_occupancy=p.occupancy_base,
        reported_within4=p.within4_base,
        reported_nwau=500.0,
        reported_efficiency_gap=efficiency_gap,
        reported_coding_intensity=1.0,
        prob_ed=0.5,
        metrics=MetricsJax(),
    )


@beartype
def lhn_step_jax(
    lhn: LhnState,
    p: ParamsJax,
    strategies: Float[Array, "13"],
    demand: Float[Array, ""],
    month_growth_factor: float,
    offload_noise: Float[Array, ""],
    discharge_delay_target: Float[Array, ""],
    workforce_availability: Float[Array, ""],
) -> LhnState:
    """Operational step for a single LHN agent."""
    wf_intensity = strategies[8]
    wf_drain = (wf_intensity * 0.2 + (1.0 - wf_intensity) * 0.1) * month_growth_factor
    wf_drain += strategies[12] * 0.1 * month_growth_factor

    wf_impact = jnp.exp(0.5 * jnp.maximum(0.0, 1.0 - workforce_availability))

    aged_val, ndis_val, disc_val = strategies[5], strategies[6], strategies[4]
    aged_effect = aged_val * 0.95 + (1.0 - aged_val) * (1.02 * p.fragmentation_index)
    ndis_effect = ndis_val * 0.96 + (1.0 - ndis_val) * (1.03 * p.fragmentation_index)
    disc_effect = disc_val * 0.98 + (1.0 - disc_val) * 1.01

    discharge = (
        lhn.discharge_delay
        * ((aged_effect * ndis_effect * disc_effect) ** month_growth_factor)
        * wf_impact
    )
    discharge = jnp.clip(discharge + 0.1 * (discharge_delay_target - discharge), 0.75, 1.50)

    is_expanding = lhn.target_capacity > lhn.current_capacity
    active_lag = jnp.where(is_expanding, p.expansion_lag, p.contraction_lag)
    capacity = lhn.current_capacity + active_lag * (lhn.target_capacity - lhn.current_capacity)

    wait_min = mm_s_queue_wait_jax(
        demand, 1.0 / jnp.maximum(1e-9, discharge), jnp.array(capacity * 10.0)
    )
    occ = jnp.clip(lhn.occupancy + 0.015 * (demand - 1.0) + 0.035 * (discharge - 1.0), 0.78, 0.98)
    off = jnp.clip(lhn.offload_min + 8.0 * (occ - 0.88) + offload_noise, 5.0, 120.0)
    pidx = 0.8 + 0.2 * (wait_min / 60.0) + 0.5 * (occ - 0.8) / 0.1

    return lhn.replace(
        pressure=pidx,
        occupancy=occ,
        offload_min=off,
        within4=within4_from_pressure_jax(pidx),
        discharge_delay=discharge,
        current_capacity=capacity,
        nwau_actual=occ * 100.0,
        adjustment_costs=p.adjustment_cost_beta * jnp.square(capacity - lhn.current_capacity),
    )


@beartype
def jurisdiction_step_jax(
    js: JurisdictionState,
    p: ParamsJax,
    strategies: Float[Array, "13"],
    demand_macro: Float[Array, ""],
    mgf: float,
    prng_key: Any,
    wf_pool: Float[Array, ""],
) -> JurisdictionState:
    """Step for a single jurisdiction and its batch of LHNs."""
    k_ops, k_pay = jax.random.split(prng_key)
    n_lhns = js.lhn_states.id.shape[0]

    # State-level target
    discharge_target = jnp.where(jnp.mean(js.lhn_states.pressure) > 1.1, 0.9, 1.0)

    # Vectorized LHN steps
    keys = jax.random.split(k_ops, n_lhns)
    new_lhns = jax.vmap(
        lambda l, k: lhn_step_jax(
            l,
            p,
            strategies,
            demand_macro,
            mgf,
            jax.random.normal(k) * 0.8,
            discharge_target,
            wf_pool,
        )
    )(js.lhn_states, keys)

    return js.replace(lhn_states=new_lhns)


@beartype
def step_jax(s: StateJax, p: ParamsJax, strategies: Float[Array, "13"], prng_key: Any) -> StateJax:
    mgf = 1.0 / 12.0
    k_dem, k_jur = jax.random.split(prng_key)

    # 1. Macro demand
    demand_macro, prob_ed = demand_step_jax(s, p, strategies, jax.random.normal(k_dem) * 0.02)

    # 2. Vectorized Jurisdiction steps
    n_jur = s.jurisdictions.id.shape[0]
    keys = jax.random.split(k_jur, n_jur)
    new_jurisdictions = jax.vmap(
        lambda j, k: jurisdiction_step_jax(j, p, strategies, demand_macro, mgf, k, s.workforce_pool)
    )(s.jurisdictions, keys)

    # 3. Global Aggregation
    avg_pidx = jnp.mean(new_jurisdictions.lhn_states.pressure)
    avg_occ = jnp.mean(new_jurisdictions.lhn_states.occupancy)
    avg_w4 = jnp.mean(new_jurisdictions.lhn_states.within4)

    # 4. Workforce Update
    wf_drain = jnp.sum(new_jurisdictions.lhn_states.occupancy * 0.02) * mgf
    new_wf_pool = jnp.clip(s.workforce_pool - wf_drain + 0.1 * mgf, 0.5, 1.5)

    # 5. Roll time and buffers
    next_m = jnp.where(s.month == 12, 1, s.month + 1)
    next_y = jnp.where(s.month == 12, s.year + 1, s.year)

    (nb_p, nb_o, nb_w, nb_n, nb_e, nb_c, rp, ro, rw, rn, re, rc) = update_lag_buffers(
        s, p, avg_pidx, avg_occ, avg_w4, jnp.sum(new_jurisdictions.lhn_states.nwau_actual), 0.1, 1.0
    )

    return s.replace(
        year=next_y,
        month=next_m,
        pressure=avg_pidx,
        occupancy=avg_occ,
        within4=avg_w4,
        jurisdictions=new_jurisdictions,
        workforce_pool=new_wf_pool,
        prob_ed=prob_ed,
        lag_buffer_pressure=nb_p,
        lag_buffer_occupancy=nb_o,
        lag_buffer_within4=nb_w,
        reported_pressure=rp,
        reported_occupancy=ro,
        reported_within4=rw,
        system_mode=update_system_mode_jax(s, p, avg_pidx),
    )


@beartype
def run_simulation_jax(
    init_state: StateJax,
    params: ParamsJax,
    strategies: Float[Array, "num_steps 13"],
    prng_key: Any,
    num_steps: int,
) -> tuple[StateJax, StateJax]:
    def body_func(carry, input_tuple):
        strat, key = input_tuple
        next_s = step_jax(carry, params, strat, key)
        return next_s, next_s

    keys = jax.random.split(prng_key, num_steps)
    return lax.scan(body_func, init_state, (strategies, keys))


@beartype
def update_system_mode_jax(s: StateJax, p: ParamsJax, current_pressure: Float[Array, ""]) -> Any:
    mode = s.system_mode
    mode = jnp.where((mode == 0) & (current_pressure > 1.25), 1, mode)

    def from_stress():
        return jnp.where(current_pressure > 1.5, 2, jnp.where(current_pressure < 1.05, 0, 1))

    mode = jnp.where(mode == 1, from_stress(), mode)
    mode = jnp.where((mode == 2) & (current_pressure < 1.3), 3, mode)

    def from_recovery():
        return jnp.where(current_pressure < 1.1, 0, jnp.where(current_pressure > 1.4, 2, 3))

    mode = jnp.where(mode == 3, from_recovery(), mode)
    return mode


@beartype
def demand_step_jax(
    s: StateJax, p: ParamsJax, strategies: Float[Array, "13"], noise: Float[Array, ""]
) -> tuple[Float[Array, ""], Float[Array, ""]]:
    shift_val = strategies[3]
    demand_factor = shift_val * (1.04 * p.cost_shifting_intensity / 0.35) + (1.0 - shift_val) * 0.96
    qp = PatientUtilityParams(
        gp_out_of_pocket=p.gp_out_of_pocket,
        gp_wait_time_min=p.gp_wait_time_min,
        patient_time_value_hour=p.patient_time_value_hour,
    )
    d_final, prob_ed = solve_queuing_equilibrium_jax(
        total_base_demand=p.demand_base * demand_factor * 2.0,
        capacity=s.occupancy,
        discharge_delay=1.0,
        params=qp,
    )
    return jnp.maximum(0.5, d_final + noise), prob_ed
