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


def _pad_strategies(strategies: Any, width: int = 13) -> Any:
    arr = jnp.asarray(strategies)

    if arr.ndim == 1:
        k = int(arr.shape[0])
        if k == width:
            return arr
        if k > width:
            return arr[:width]
        return jnp.pad(arr, (0, width - k))

    if arr.ndim == 2:
        k = int(arr.shape[1])
        if k == width:
            return arr
        if k > width:
            return arr[:, :width]
        return jnp.pad(arr, ((0, 0), (0, width - k)))

    return arr


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
    effective_cth_share = p.effective_cth_share_base * (1.0 + efficiency_gap)
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
        effective_cth_share=effective_cth_share,
        efficiency_gap=efficiency_gap,
        discharge_delay=p.discharge_delay_base,
        political_capital=1.0,
        equity_index=1.0,
        bailout_expectation=0.0,
        coding_intensity=1.0,
        reputation_score=1.0,
        jurisdiction_id=0,
        system_mode=0,
        workforce_pool=1.0,
        agreement_clock=5,
        target_capacity=1.0,
        current_capacity=1.0,
        reconciliation_balance=0.0,
        total_block_revenue=0.0,
        lhn_pressure=jnp.full(n_lhns, 1.0),
        lhn_nwau=jnp.full(n_lhns, 100.0),
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
    strategies: Any,
    demand_macro: Float[Array, ""],
    mgf: float,
    prng_key: Any,
    wf_pool: Float[Array, ""],
) -> JurisdictionState:
    """Step for a single jurisdiction and its batch of LHNs."""
    strategies = _pad_strategies(strategies)
    k_ops, k_pay = jax.random.split(prng_key)
    n_lhns = js.lhn_states.id.shape[0]

    # State-level target
    discharge_target = jnp.where(jnp.mean(js.lhn_states.pressure) > 1.1, 0.9, 1.0)

    # Vectorized LHN steps
    keys = jax.random.split(k_ops, n_lhns)
    new_lhns = jax.vmap(
        lambda lhn, k: lhn_step_jax(
            lhn,
            p,
            strategies,
            demand_macro,
            mgf,
            jax.random.normal(k) * (0.8 * jnp.asarray(p.noise_sd) / 0.03),
            discharge_target,
            wf_pool,
        )
    )(js.lhn_states, keys)

    return js.replace(lhn_states=new_lhns)


@beartype
def step_jax(s: StateJax, p: ParamsJax, strategies: Any, prng_key: Any) -> StateJax:
    strategies = _pad_strategies(strategies)
    mgf = 1.0 / 12.0
    k_dem, k_jur = jax.random.split(prng_key)

    def _step_flat(state: StateJax) -> StateJax:
        k_ops, k_cap = jax.random.split(k_jur)

        demand_macro, prob_ed = demand_step_jax(
            state, p, strategies, jax.random.normal(k_dem) * jnp.asarray(p.noise_sd)
        )

        lhn_p = jnp.asarray(state.lhn_pressure)
        lhn_p = jnp.where(state.month == 1, jnp.full_like(lhn_p, state.pressure), lhn_p)
        noise = jax.random.normal(k_ops, shape=lhn_p.shape) * jnp.asarray(p.noise_sd)
        target_p = jnp.clip(
            1.0 + 0.8 * (demand_macro - 1.0) + 0.3 * (state.occupancy - 0.88) / 0.1,
            0.7,
            2.5,
        )
        lhn_p_next = jnp.clip(lhn_p + 0.15 * (target_p - lhn_p) + noise, 0.7, 2.5)
        avg_pidx = jnp.mean(lhn_p_next, axis=-1)

        next_m = jnp.where(state.month == 12, 1, state.month + 1)
        next_y = jnp.where(state.month == 12, state.year + 1, state.year)
        next_agreement_clock = jnp.where(
            state.month == 12,
            jnp.where(state.agreement_clock <= 0, 5, state.agreement_clock - 1),
            state.agreement_clock,
        )

        do_renegotiate = (state.month == 12) & (state.agreement_clock == 0)
        drift_share = 0.02 * (p.nominal_cth_share_target - state.effective_cth_share)
        reneg_delta = 0.03 * (avg_pidx - 1.0)
        next_share = jnp.where(
            do_renegotiate,
            jnp.clip(state.effective_cth_share + drift_share + reneg_delta, 0.2, 0.6),
            jnp.clip(state.effective_cth_share + drift_share, 0.2, 0.6),
        )
        next_eff_gap = jnp.clip(
            state.efficiency_gap - 0.25 * (next_share - state.effective_cth_share), 0.0, 1.0
        )

        pressure_adjust = 0.5 * (next_eff_gap - state.efficiency_gap)
        avg_pidx_adj = jnp.clip(avg_pidx + pressure_adjust, 0.7, 2.5)
        lhn_p_next = jnp.clip(lhn_p_next + (avg_pidx_adj - avg_pidx)[..., None], 0.7, 2.5)

        next_occ = jnp.clip(
            state.occupancy + 0.01 * (demand_macro - 1.0) + 0.02 * (avg_pidx_adj - state.pressure),
            0.75,
            0.99,
        )
        next_w4 = within4_from_pressure_jax(avg_pidx_adj)
        next_off = jnp.clip(state.offload_min + 10.0 * (next_occ - 0.88), 5.0, 120.0)

        cap_move = strategies[11]
        next_target_capacity = jnp.clip(state.target_capacity + cap_move, 0.5, 1.5)
        is_expanding = next_target_capacity > state.current_capacity
        active_lag = jnp.where(is_expanding, p.expansion_lag, p.contraction_lag)
        next_current_capacity = state.current_capacity + active_lag * (
            next_target_capacity - state.current_capacity
        )
        adjustment_costs = p.adjustment_cost_beta * jnp.square(
            next_current_capacity - state.current_capacity
        )
        next_reconciliation_balance = state.reconciliation_balance - adjustment_costs

        coding_strategy = strategies[7]
        coding_signal = (
            jnp.maximum(0.0, jnp.asarray(state.coding_intensity) - 1.0) * coding_strategy
        )
        next_suspicion = jnp.where(
            coding_strategy > 0.5,
            jnp.clip(state.auditor_suspicion + 0.03 * coding_signal, 0.0, 1.0),
            jnp.clip(state.auditor_suspicion * 0.95, 0.0, 1.0),
        )
        next_audit_pressure_active = jnp.clip(0.25 + next_suspicion * p.audit_pressure, 0.0, 2.0)

        wf_drain = jnp.mean(next_occ) * 0.02 * mgf
        new_wf_pool = jnp.clip(state.workforce_pool - wf_drain + 0.1 * mgf, 0.5, 1.5)

        venue_shift = strategies[10]
        total_block_revenue = venue_shift * 100.0

        (nb_p, nb_o, nb_w, nb_n, nb_e, nb_c, rp, ro, rw, rn, re, rc) = update_lag_buffers(
            state,
            p,
            avg_pidx_adj,
            next_occ,
            next_w4,
            jnp.sum(jnp.asarray(state.lhn_nwau)),
            next_eff_gap,
            jnp.asarray(state.coding_intensity),
        )

        return state.replace(
            year=next_y,
            month=next_m,
            agreement_clock=next_agreement_clock,
            pressure=avg_pidx_adj,
            occupancy=next_occ,
            within4=next_w4,
            offload_min=next_off,
            lhn_pressure=lhn_p_next,
            effective_cth_share=next_share,
            efficiency_gap=next_eff_gap,
            target_capacity=next_target_capacity,
            current_capacity=next_current_capacity,
            adjustment_costs=adjustment_costs,
            reconciliation_balance=next_reconciliation_balance,
            auditor_suspicion=next_suspicion,
            audit_pressure_active=next_audit_pressure_active,
            workforce_pool=new_wf_pool,
            prob_ed=prob_ed,
            total_block_revenue=total_block_revenue,
            metrics=state.metrics.replace(
                cumulative_adjustment_costs=state.metrics.cumulative_adjustment_costs
                + adjustment_costs
            ),
            lag_buffer_pressure=nb_p,
            lag_buffer_occupancy=nb_o,
            lag_buffer_within4=nb_w,
            reported_pressure=rp,
            reported_occupancy=ro,
            reported_within4=rw,
            reported_nwau=rn,
            reported_efficiency_gap=re,
            reported_coding_intensity=rc,
            system_mode=update_system_mode_jax(state, p, avg_pidx_adj),
        )

    if s.jurisdictions is None:
        return _step_flat(s)

    def _seed_from_globals(state: StateJax) -> StateJax:
        lhns = state.jurisdictions.lhn_states
        seeded = lhns.replace(
            pressure=jnp.full_like(lhns.pressure, state.pressure),
            occupancy=jnp.full_like(lhns.occupancy, state.occupancy),
            within4=jnp.full_like(lhns.within4, state.within4),
            offload_min=jnp.full_like(lhns.offload_min, state.offload_min),
            target_capacity=jnp.full_like(lhns.target_capacity, state.target_capacity),
            current_capacity=jnp.full_like(lhns.current_capacity, state.current_capacity),
        )
        return state.replace(jurisdictions=state.jurisdictions.replace(lhn_states=seeded))

    s = lax.cond(s.month == 1, _seed_from_globals, lambda x: x, s)

    # 1. Macro demand
    demand_macro, prob_ed = demand_step_jax(
        s, p, strategies, jax.random.normal(k_dem) * jnp.asarray(p.noise_sd)
    )

    # 2. Vectorized Jurisdiction steps
    n_jur = s.jurisdictions.id.shape[0]
    keys = jax.random.split(k_jur, n_jur)
    new_jurisdictions = jax.vmap(
        lambda j, k: jurisdiction_step_jax(j, p, strategies, demand_macro, mgf, k, s.workforce_pool)
    )(s.jurisdictions, keys)

    venue_shift = strategies[10]
    new_jurisdictions = new_jurisdictions.replace(
        total_block_revenue=jnp.full_like(
            new_jurisdictions.total_block_revenue, venue_shift * 100.0
        )
    )

    # 3. Global Aggregation
    avg_pidx = jnp.mean(new_jurisdictions.lhn_states.pressure)
    avg_occ = jnp.mean(new_jurisdictions.lhn_states.occupancy)
    avg_w4 = jnp.mean(new_jurisdictions.lhn_states.within4)
    avg_target_capacity = jnp.mean(new_jurisdictions.lhn_states.target_capacity)
    avg_current_capacity = jnp.mean(new_jurisdictions.lhn_states.current_capacity)
    adjustment_costs = jnp.mean(new_jurisdictions.lhn_states.adjustment_costs)
    next_reconciliation_balance = s.reconciliation_balance - adjustment_costs

    # Auditor: suspicion rises with gaming and decays otherwise.
    coding_strategy = strategies[7]
    coding_signal = jnp.maximum(0.0, jnp.asarray(s.coding_intensity) - 1.0) * coding_strategy
    next_suspicion = jnp.where(
        coding_strategy > 0.5,
        jnp.clip(s.auditor_suspicion + 0.03 * coding_signal, 0.0, 1.0),
        jnp.clip(s.auditor_suspicion * 0.95, 0.0, 1.0),
    )
    next_audit_pressure_active = jnp.clip(0.25 + next_suspicion * p.audit_pressure, 0.0, 2.0)

    # 4. Workforce Update
    wf_drain = jnp.sum(new_jurisdictions.lhn_states.occupancy * 0.02) * mgf
    new_wf_pool = jnp.clip(s.workforce_pool - wf_drain + 0.1 * mgf, 0.5, 1.5)

    # 5. Roll time and buffers
    next_m = jnp.where(s.month == 12, 1, s.month + 1)
    next_y = jnp.where(s.month == 12, s.year + 1, s.year)
    next_agreement_clock = jnp.where(
        s.month == 12,
        jnp.where(s.agreement_clock <= 0, 5, s.agreement_clock - 1),
        s.agreement_clock,
    )

    def _renegotiate(jurs):
        delta = 0.03 * (avg_pidx - 1.0)
        next_share = jnp.clip(jurs.effective_cth_share + delta, 0.2, 0.6)
        return jurs.replace(effective_cth_share=next_share)

    do_renegotiate = (s.month == 12) & (s.agreement_clock == 0)
    new_jurisdictions = lax.cond(do_renegotiate, _renegotiate, lambda j: j, new_jurisdictions)

    (nb_p, nb_o, nb_w, nb_n, nb_e, nb_c, rp, ro, rw, rn, re, rc) = update_lag_buffers(
        s,
        p,
        avg_pidx,
        avg_occ,
        avg_w4,
        jnp.sum(new_jurisdictions.lhn_states.nwau_actual),
        jnp.mean(new_jurisdictions.efficiency_gap),
        jnp.asarray(s.coding_intensity),
    )

    return s.replace(
        year=next_y,
        month=next_m,
        agreement_clock=next_agreement_clock,
        target_capacity=avg_target_capacity,
        current_capacity=avg_current_capacity,
        reconciliation_balance=next_reconciliation_balance,
        pressure=avg_pidx,
        occupancy=avg_occ,
        within4=avg_w4,
        effective_cth_share=jnp.mean(new_jurisdictions.effective_cth_share),
        efficiency_gap=jnp.mean(new_jurisdictions.efficiency_gap),
        total_block_revenue=jnp.mean(new_jurisdictions.total_block_revenue),
        lhn_pressure=new_jurisdictions.lhn_states.pressure[0],
        lhn_nwau=new_jurisdictions.lhn_states.nwau_actual[0],
        jurisdictions=new_jurisdictions,
        auditor_suspicion=next_suspicion,
        audit_pressure_active=next_audit_pressure_active,
        metrics=s.metrics.replace(
            cumulative_adjustment_costs=s.metrics.cumulative_adjustment_costs + adjustment_costs
        ),
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
    strategies: Any,
    prng_key: Any,
    num_steps: int,
) -> tuple[StateJax, StateJax]:
    strategies = _pad_strategies(strategies)

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
