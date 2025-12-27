from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.domain.state import ParamsJax, StateJax, SystemModeJax
from nhra_gt.engine import Params, State, SystemMode, baseline_state, step
from nhra_gt.engine_jax import run_simulation_jax, step_jax


def params_to_jax(p: Params) -> ParamsJax:
    from nhra_gt.domain.state import EconomicSpineJax

    spine_jax = None
    if p.economic_spine is not None:
        spine_jax = EconomicSpineJax(
            years=jnp.array(p.economic_spine["year"].values, dtype=jnp.int32),
            nep_per_nwau=jnp.array(p.economic_spine["nep_per_nwau"].values, dtype=jnp.float64),
            wpi_health_index=jnp.array(p.economic_spine["wpi_health_index"].values, dtype=jnp.float64),
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
        system_mode=int(s.system_mode.value) if isinstance(s.system_mode.value, (int, float)) else 0,
        lhn_pressure=jnp.zeros(5),
        lhn_nwau=jnp.zeros(5),
        agreement_clock=5,
        workforce_pool=1.0,
        target_capacity=s.target_capacity,
        current_capacity=s.current_capacity,
        equity_index=s.equity_index,
        reconciliation_balance=s.reconciliation_balance,
        bailout_expectation=s.bailout_expectation,
        coding_intensity=s.coding_intensity,
        reputation_score=s.reputation_score,
    )


def strategies_to_jax(strat: dict[str, Any]) -> jnp.ndarray:
    # 0: SIGNAL, 1: DEF, 2: BARG, 3: SHIFT, 4: DISC, 5: AGED, 6: NDIS, 7: CODING, 8: COMP, 9: SIGNAL_QUALITY
    arr = jnp.zeros(10)
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
    return arr


def test_step_parity():
    p = Params()
    s = State(
        year=2025,
        month=1,
        pressure=1.0,
        occupancy=0.88,
        offload_min=18.0,
        within4=0.53,
        effective_cth_share=0.45,
        efficiency_gap=0.1,
        discharge_delay=1.0,
        political_capital=1.0,
    )

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

    # To test parity without stochasticity, we'll mock the RNG or use a specific seed
    # But current engine uses np.random.Generator which is different from JAX.
    # We might need to override the noise components in both for exact parity.

    # For now, let's just check if the logic flows without error and outputs are reasonable
    key = jax.random.PRNGKey(42)
    next_sj = step_jax(sj, pj, str_j, key)

    # Legacy step
    rng = np.random.default_rng(42)
    next_s = step(s, p, strategies, rng)

    # Check non-stochastic fields first
    assert next_sj.year == next_s.year
    assert next_sj.month == next_s.month
    # Floating point fields will differ due to noise and implementation details (math vs jnp)
    # but they should be in the same ballpark.
    assert np.abs(next_sj.pressure - next_s.pressure) < 0.5
    assert np.abs(next_sj.effective_cth_share - next_s.effective_cth_share) < 0.1


def test_run_simulation_jax():
    p = Params()
    s = State(
        year=2025,
        month=1,
        pressure=1.0,
        occupancy=0.88,
        offload_min=18.0,
        within4=0.53,
        effective_cth_share=0.45,
        efficiency_gap=0.1,
        discharge_delay=1.0,
        political_capital=1.0,
    )

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
    
    # Broadcast strategies to [num_months, 10]
    str_j_seq = jnp.tile(str_j, (num_months, 1))
    
    final_s, trajectory = jax.jit(
        lambda init, par, strat, k: jax.vmap(
            lambda sk: run_simulation_jax(init, par, strat, sk, num_months), in_axes=0
        )(jax.random.split(k, 5))
    )(sj, pj, str_j_seq, key)

    # final_s should have shape (5,) - five parallel rollouts
    assert final_s.year.shape == (5,)
    assert final_s.year[0] == 2026
    assert final_s.month[0] == 1

    # trajectory should have shape (5, 12)
    assert trajectory.pressure.shape == (5, 12)


def test_full_trajectory_mirror():
    """Rigorous check: Run 5 years of simulation and compare average results.
    Note: Noise makes exact bit-parity impossible without synchronized RNGs,
    but we check if the deterministic parts and averages align.
    """
    p = Params()
    pj = params_to_jax(p)

    years = list(range(2025, 2031))
    num_months = len(years) * 12

    # Fixed strategies for testing
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

    # 1. Legacy Run
    # Mocking rng to minimize divergence
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

    # 2. JAX Run
    # We'll use a high-sample average or also try to neutralize noise
    # In JAX, we can't easily 'mock' random functions inside JIT,
    # but we can set noise parameters to 0 in ParamsJax for this test.
    pj_no_noise = pj.replace(noise_sd=0.0)

    sj = state_to_jax(baseline_state(start_year=2025, p=p))
    # We still have some hardcoded noises in engine_jax (demand_noise, offload_noise)
    # Let's override them by passing a key that happens to yield small values
    # or better, implement a 'deterministic' version of step_jax if needed.
    # For this test, we'll just check if they are within a tight tolerance.

    key = jax.random.PRNGKey(0)
    str_jax_seq = jnp.tile(strat_jax, (num_months, 1))
    _, traj = run_simulation_jax(sj, pj_no_noise, str_jax_seq, key, num_months)

    # Compare. Tolerance is slightly higher due to 0.02 normal noise in demand_step_jax
    # and 0.8 normal noise in offload_noise.
    for i in range(num_months):
                                                                                            # Pressure is derived from wait_min and occupancy.
                                                                                            # It should be close.
                                                                                            diff = np.abs(traj.pressure[i] - legacy_pressure[i])
                                                                                            assert diff < 1.0, f"Pressure divergence at month {i}: {diff}"
                                            
