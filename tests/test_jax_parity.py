from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.engine import Params, State, baseline_state, step
from nhra_gt.engine_jax import run_simulation_jax, step_jax
from nhra_gt.rules import initialize_rules


def params_to_jax(p: Params) -> ParamsJax:
    from nhra_gt.domain.state import EconomicSpineJax

    p = initialize_rules(p)
    spine_jax = None
    if p.economic_spine is not None:
        spine_jax = EconomicSpineJax(
            years=jnp.array(p.economic_spine["year"].values, dtype=jnp.int32),
            nep_per_nwau=jnp.array(p.economic_spine["nep_per_nwau"].values, dtype=jnp.float64),
            wpi_health_index=jnp.array(
                p.economic_spine["wpi_health_index"].values, dtype=jnp.float64
            ),
        )

    return ParamsJax(
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
        cap_rule_type=1 if p.cap_rule_type == "soft" else 0,
        audit_rule_type=1 if p.audit_rule_type == "threshold" else 0,
        cap_rule=p.cap_rule,
        audit_rule=p.audit_rule,
        eligibility_rule=p.eligibility_rule,
        reconciliation_rule=p.reconciliation_rule,
        spine=spine_jax,
    )


def state_to_jax(s: State) -> StateJax:
    return StateJax(
        year=s.year,
        month=s.month,
        pressure=s.pressure,
        occupancy=s.occupancy,
        offload_min=s.offload_min,
        within4=s.within4,
        effective_cth_share=s.effective_cth_share,
        efficiency_gap=s.efficiency_gap,
        discharge_delay=s.discharge_delay,
        political_capital=s.political_capital,
        system_mode=int(s.system_mode.value) if isinstance(s.system_mode.value, int | float) else 0,
        lhn_pressure=jnp.zeros(5),
        lhn_nwau=jnp.full(5, 100.0),
        agreement_clock=5,
        workforce_pool=1.0,
        target_capacity=s.target_capacity,
        current_capacity=s.current_capacity,
        equity_index=s.equity_index,
        reconciliation_balance=s.reconciliation_balance,
        bailout_expectation=s.bailout_expectation,
        coding_intensity=s.coding_intensity,
        reputation_score=s.reputation_score,
        auditor_suspicion=s.auditor_suspicion,
        audit_pressure_active=s.audit_pressure_active,
        # Lags
        lag_buffer_pressure=jnp.array(s.lag_buffer_pressure),
        lag_buffer_occupancy=jnp.array(s.lag_buffer_occupancy),
        lag_buffer_within4=jnp.array(s.lag_buffer_within4),
        lag_buffer_nwau=jnp.array(s.lag_buffer_nwau),
        lag_buffer_efficiency_gap=jnp.array(s.lag_buffer_efficiency_gap),
        lag_buffer_coding=jnp.array(s.lag_buffer_coding),
        reported_pressure=s.reported_pressure,
        reported_occupancy=s.reported_occupancy,
        reported_within4=s.reported_within4,
        reported_nwau=s.reported_nwau,
        reported_efficiency_gap=s.reported_efficiency_gap,
        reported_coding_intensity=s.reported_coding_intensity,
    )


def strategies_to_jax(strat: dict[str, Any]) -> jnp.ndarray:
    # 0: SIGNAL, 1: DEF, 2: BARG, 3: SHIFT, 4: DISC, 5: AGED, 6: NDIS, 7: CODING, 8: COMP, 9: SIGNAL_QUALITY, 10: VENUE_SHIFT, 11: CAPACITY, 12: COMPETITION
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


def test_step_parity():
    p = Params()
    p = initialize_rules(p)
    s = baseline_state(start_year=2025, p=p)

    strategies = {
        "SIGNAL": "L",
        "DEF": "E",
        "BARG": "D",
        "SHIFT": "I",
        "DISC": "F",
        "AGED": "F",
        "NDIS": "F",
        "CODING": "H",
        "COMP": "L",
        "SIGNAL_QUALITY": 1.0,
    }

    # Setup JAX
    pj = params_to_jax(p)
    sj = state_to_jax(s)
    str_j = strategies_to_jax(strategies)

    key = jax.random.PRNGKey(42)
    next_sj = step_jax(sj, pj, str_j, key)

    # Legacy step
    rng = np.random.default_rng(42)
    next_s = step(s, p, strategies, rng)

    assert next_sj.year == next_s.year
    assert next_sj.month == next_s.month
    assert np.abs(next_sj.pressure - next_s.pressure) < 0.5
    assert np.abs(next_sj.effective_cth_share - next_s.effective_cth_share) < 0.1


def test_run_simulation_jax():
    p = Params()
    p = initialize_rules(p)
    s = baseline_state(start_year=2025, p=p)

    strategies = {
        "SIGNAL": "L",
        "DEF": "E",
        "BARG": "D",
        "SHIFT": "I",
        "DISC": "F",
        "AGED": "F",
        "NDIS": "F",
        "CODING": "H",
        "COMP": "L",
        "SIGNAL_QUALITY": 1.0,
    }

    pj = params_to_jax(p)
    sj = state_to_jax(s)
    str_j = strategies_to_jax(strategies)

    key = jax.random.PRNGKey(123)
    num_months = 12

    str_j_seq = jnp.tile(str_j, (num_months, 1))

    final_s, trajectory = jax.jit(
        lambda init, par, strat, k: jax.vmap(
            lambda sk: run_simulation_jax(init, par, strat, sk, num_months), in_axes=0
        )(jax.random.split(k, 5))
    )(sj, pj, str_j_seq, key)

    assert final_s.year.shape == (5,)
    assert final_s.year[0] == 2026
    assert final_s.month[0] == 1
    assert trajectory.pressure.shape == (5, 12)


def test_full_trajectory_mirror():
    """Rigorous check: Run 5 years of simulation and compare average results."""
    p = Params()
    p = initialize_rules(p)
    pj = params_to_jax(p)

    years = list(range(2025, 2031))
    num_months = len(years) * 12

    strat_dict = {
        "SIGNAL": "L",
        "DEF": "E",
        "BARG": "A",
        "SHIFT": "I",
        "DISC": "C",
        "AGED": "C",
        "NDIS": "C",
        "CODING": "H",
        "COMP": "L",
        "SIGNAL_QUALITY": 1.0,
    }
    strat_jax = strategies_to_jax(strat_dict)

    class ConstRNG:
        def normal(self, loc=0, scale=1, size=None):
            return loc

        def random(self, size=None):
            return 0.5

    s_legacy = baseline_state(start_year=2025, p=p)
    legacy_pressure = []
    for _ in range(num_months):
        s_legacy = step(s_legacy, p, strat_dict, ConstRNG())
        legacy_pressure.append(s_legacy.pressure)

    pj_no_noise = pj.replace(noise_sd=0.0)
    sj = state_to_jax(baseline_state(start_year=2025, p=p))

    key = jax.random.PRNGKey(0)
    str_jax_seq = jnp.tile(strat_jax, (num_months, 1))
    _, traj = run_simulation_jax(sj, pj_no_noise, str_jax_seq, key, num_months)

    for i in range(num_months):
        diff = np.abs(traj.pressure[i] - legacy_pressure[i])
        assert diff < 1.0, f"Pressure divergence at month {i}: {diff}"
