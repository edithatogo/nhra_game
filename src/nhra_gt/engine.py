from __future__ import annotations

import math
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from beartype import beartype
from jax import config, lax
from jaxtyping import Array, Float

from nhra_gt.agents.jax import HeuristicAgentJax
from nhra_gt.domain.state import JurisdictionState, LhnState, MetricsJax, ParamsJax, StateJax
from nhra_gt.rules import initialize_rules
from nhra_gt.subgames.queuing import PatientUtilityParams, solve_queuing_equilibrium_jax

config.update("jax_enable_x64", True)

# Aliases for compatibility
Params = ParamsJax
State = StateJax

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


def baseline_state(start_year: int = 2025, p: ParamsJax | None = None) -> StateJax:
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

    if s.jurisdictions is None:
        return s.replace(year=s.year + 1)

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
        from nhra_gt.solvers_jax import discrete_nash_jax
        from nhra_gt.subgames.games_jax import GameParamsJax, renegotiation_game_jax

        # Aggregate params for game
        gp = GameParamsJax(
            pressure=avg_pidx,
            efficiency_gap=jnp.mean(jurs.efficiency_gap),
            discharge_delay=jnp.mean(jurs.lhn_states.discharge_delay),
            political_salience=p.political_salience,
            audit_pressure=p.audit_pressure,
            cost_shifting_intensity=p.cost_shifting_intensity,
            political_capital=jnp.mean(jurs.political_capital),
        )

        u_row, u_col = renegotiation_game_jax(gp)
        p_row, q_col = discrete_nash_jax(u_row, u_col)

        cth_concede = p_row[0] > 0.5
        state_hold_up = q_col[1] > 0.5

        increase = jnp.where(
            cth_concede & state_hold_up, 0.06, jnp.where(cth_concede | state_hold_up, 0.03, 0.0)
        )

        next_share = jnp.clip(p.nominal_cth_share_target + increase, 0.40, 0.70)
        next_share_batched = jnp.full_like(jurs.effective_cth_share, next_share)
        return jurs.replace(effective_cth_share=next_share_batched)

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


def apply_intervention(p: ParamsJax, name: str) -> ParamsJax:
    key = name.lower().strip().replace(" ", "_")

    def clamp(val, low, high):
        return jnp.clip(val, low, high)

    if key in {"pooled_funding", "pooled"}:
        return p.replace(
            cost_shifting_intensity=float(clamp(p.cost_shifting_intensity * 0.75, 0.05, 0.60))
        )

    if key in {"ucc_integration", "integration"}:
        return p.replace(fragmentation_index=float(clamp(p.fragmentation_index * 0.80, 0.60, 1.50)))

    if key in {"nep_realism", "indexation"}:
        return p.replace(
            nep_to_cost_ratio_metro=float(clamp(p.nep_to_cost_ratio_metro + 0.03, 0.6, 1.0)),
            nep_to_cost_ratio_regional=float(clamp(p.nep_to_cost_ratio_regional + 0.04, 0.6, 1.0)),
            nep_to_cost_ratio_remote=float(clamp(p.nep_to_cost_ratio_remote + 0.05, 0.6, 1.0)),
        )

    if key in {"aged_ndis_capacity", "discharge"}:
        return p.replace(discharge_delay_base=float(clamp(p.discharge_delay_base * 0.90, 0.6, 1.4)))

    if key in {"middle_tier", "workforce"}:
        return p.replace(
            nep_to_cost_ratio_regional=float(clamp(p.nep_to_cost_ratio_regional + 0.03, 0.6, 1.0)),
            nep_to_cost_ratio_remote=float(clamp(p.nep_to_cost_ratio_remote + 0.04, 0.6, 1.0)),
        )

    if key in {"cumulative_cap", "cap"}:
        return p.replace(has_cumulative_cap=True, cap_growth=0.070)

    if key in {"audit_relief"}:
        return p.replace(
            audit_pressure=float(clamp(p.audit_pressure * 0.70, 0.05, 1.0)),
            admin_burden_weight=float(clamp(p.admin_burden_weight * 0.8, 0.05, 0.6)),
        )

    return p


def run_hybrid(
    years: list[int],
    p: ParamsJax,
    seed: int = 123,
    n_mc: int = 300,
    recorder: Any | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    start_year = years[0]
    end_year = years[-1]
    num_years = end_year - start_year + 1
    num_months = num_years * 12

    agent = HeuristicAgentJax()

    def step_with_agent(state, key):
        strat = agent.decide(state, p)
        if overrides:
            for k, v in overrides.items():
                mapping = {
                    "COMP": 0,
                    "DEF": 1,
                    "BARG": 2,
                    "SHIFT": 3,
                    "DISC": 4,
                    "AGED": 5,
                    "NDIS": 6,
                    "CODING": 7,
                    "WORKFORCE": 8,
                    "SIGNAL": 9,
                    "VENUE_SHIFT": 10,
                    "CAP": 11,
                    "COMPETITION": 12,
                }
                idx = mapping.get(k, k)
                if isinstance(idx, int):
                    val = v
                    if v == "T":
                        val = 1.0
                    if v == "L":
                        val = 0.0
                    if v == "R":
                        val = 1.0
                    if v == "E":
                        val = 0.0
                    if v == "A":
                        val = 1.0
                    if v == "D":
                        val = 0.0
                    if v == "I":
                        val = 1.0
                    if v == "S":
                        val = 0.0
                    if v == "C":
                        val = 1.0
                    if v == "F":
                        val = 0.0
                    if v == "U":
                        val = 1.0
                    if v == "H":
                        val = 0.0
                    if v == "B":
                        val = 1.0
                    if v == "M":
                        val = 0.0
                    strat = strat.at[idx].set(val)

        next_s = step_jax(state, p, strat, key)
        return next_s, next_s

    @jax.jit
    def multi_rollout(keys):
        def single_rollout(key):
            init_s = baseline_state(start_year, p)
            months_keys = jax.random.split(key, num_months)
            _, trajectory = jax.lax.scan(step_with_agent, init_s, months_keys)
            return trajectory

        return jax.vmap(single_rollout)(keys)

    rng_key = jax.random.PRNGKey(seed)
    mc_keys = jax.random.split(rng_key, n_mc)

    all_trajectories = multi_rollout(mc_keys)

    def agg_metric(arr):
        return {
            "mean": np.mean(arr, axis=0),
            "std": np.std(arr, axis=0),
            "p10": np.percentile(arr, 10, axis=0),
            "p90": np.percentile(arr, 90, axis=0),
        }

    years_arr = np.array(all_trajectories.year[0])
    months_arr = np.array(all_trajectories.month[0])

    results = {
        "year": years_arr,
        "month": months_arr,
    }

    metrics_to_agg = [
        "pressure",
        "occupancy",
        "within4",
        "offload_min",
        "effective_cth_share",
        "efficiency_gap",
        "workforce_pool",
    ]

    for m in metrics_to_agg:
        data = np.array(getattr(all_trajectories, m))
        stats = agg_metric(data)
        results[f"{m}_mean"] = stats["mean"]
        results[f"{m}_std"] = stats["std"]
        results[f"{m}_p10"] = stats["p10"]
        results[f"{m}_p90"] = stats["p90"]
        results[f"{m}_sem"] = stats["std"] / math.sqrt(n_mc)

    results["effective_cth_share_mean"] = results["effective_cth_share_mean"]
    results["cth_nominal_mean"] = results["effective_cth_share_mean"]
    results["cth_effective_mean"] = results["effective_cth_share_mean"]
    results["rr_mean"] = results["pressure_mean"]
    results["rr_p10"] = results["pressure_p10"]
    results["rr_p90"] = results["pressure_p90"]
    results["efficiency_gap_mean"] = results["efficiency_gap_mean"]
    results["effgap_mean"] = results["efficiency_gap_mean"]

    results["polcap_mean"] = np.ones_like(years_arr)
    results["polcap_std"] = np.zeros_like(years_arr)
    results["polcap_sem"] = np.zeros_like(years_arr)
    results["equity_mean"] = np.ones_like(years_arr)
    results["equity_std"] = np.zeros_like(years_arr)
    results["equity_sem"] = np.zeros_like(years_arr)
    results["prob_ed_mean"] = np.array(all_trajectories.prob_ed[0])
    results["agreement_clock_mean"] = np.array(all_trajectories.agreement_clock[0])

    df = pd.DataFrame(results)
    df = df[df["year"] <= end_year]
    agg_yearly = df.groupby("year").mean().reset_index()

    strat_freq = pd.DataFrame(columns=["year", "game", "strategy", "n", "share"])
    return agg_yearly, strat_freq


baseline_state_jax = baseline_state


def mm_s_queue_wait(arrival_rate: float, service_rate: float, servers: float) -> float:
    utilization = arrival_rate / max(1e-9, (service_rate * servers))
    if utilization >= 1.0:
        return 1440.0
    wait = (utilization ** (math.sqrt(2 * (servers + 1)) - 1)) / (servers * (1 - utilization))
    return max(5.0, min(1440.0, wait * 60.0))


def summarise_outcome(agg: pd.DataFrame) -> dict[str, float]:
    from nhra_gt.domain.stability import calculate_hysteresis_area

    last = agg.sort_values("year").iloc[-1]
    summary: dict[str, float] = {
        "pressure_2030": float(last["pressure_mean"]),
        "within4_2030": float(last["within4_mean"]),
        "offload_2030": float(last.get("offload_mean", 18.0)),
        "rr_2030": float(last["rr_mean"]),
        "effshare_nominal_2030": float(last["cth_nominal_mean"]),
        "effshare_effective_2030": float(last.get("cth_effective_mean", last["cth_nominal_mean"])),
        "effgap_2030": float(last.get("effgap_mean", 0.0)),
    }
    if {"pressure_mean", "occupancy_mean"}.issubset(agg.columns):
        summary["hysteresis_area"] = float(
            calculate_hysteresis_area(
                agg["pressure_mean"].to_numpy(), agg["occupancy_mean"].to_numpy()
            )
        )
    else:
        summary["hysteresis_area"] = 0.0
    summary["recovery_time"] = 0.0
    summary["resilience_index"] = 1.0
    return summary
