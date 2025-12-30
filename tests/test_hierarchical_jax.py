from __future__ import annotations

import jax
import jax.numpy as jnp
import pytest

from nhra_gt.domain.state import MetricsJax, Params, StateJax
from nhra_gt.hierarchical_jax import hierarchical_step_jax


def test_multi_jurisdiction_vmap():
    p = Params()

    # Initialize 8 jurisdictions (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
    num_j = 8
    years = jnp.full(num_j, 2025, dtype=jnp.int32)
    months = jnp.full(num_j, 1, dtype=jnp.int32)
    pressure = jnp.linspace(0.9, 1.1, num_j)  # Different starting pressures

    # Batch metrics
    mj = MetricsJax(
        cumulative_pressure=jnp.zeros(num_j),
        cumulative_budget_variance=jnp.zeros(num_j),
        max_occupancy=jnp.zeros(num_j),
        min_within4=jnp.ones(num_j),
    )

    # Create batch of states
    js = StateJax(
        year=years,
        month=months,
        pressure=pressure,
        occupancy=jnp.full(num_j, 0.88),
        offload_min=jnp.full(num_j, 18.0),
        within4=jnp.full(num_j, 0.53),
        effective_cth_share=jnp.full(num_j, 0.45),
        efficiency_gap=jnp.full(num_j, 0.1),
        discharge_delay=jnp.full(num_j, 1.0),
        political_capital=jnp.full(num_j, 1.0),
        system_mode=jnp.zeros(num_j, dtype=jnp.int32),
        lhn_pressure=jnp.zeros((num_j, 5)),
        lhn_nwau=jnp.zeros((num_j, 5)),
        agreement_clock=jnp.full(num_j, 5, dtype=jnp.int32),
        workforce_pool=jnp.ones(num_j),
        target_capacity=jnp.ones(num_j),
        current_capacity=jnp.ones(num_j),
        equity_index=jnp.ones(num_j),
        reconciliation_balance=jnp.zeros(num_j),
        bailout_expectation=jnp.zeros(num_j),
        coding_intensity=jnp.ones(num_j),
        reputation_score=jnp.ones(num_j),
        jurisdiction_id=jnp.arange(num_j),
        metrics=mj,
    )

    cs = StateJax(
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
        system_mode=0,
        lhn_pressure=jnp.zeros(5),
        lhn_nwau=jnp.zeros(5),
        agreement_clock=5,
        workforce_pool=1.0,
    )
    macro_strats = jnp.array([1.0, 1.0])  # DEF=R, BARG=A
    key = jax.random.PRNGKey(42)

    # Run one step
    new_cs, new_js = jax.jit(hierarchical_step_jax)(cs, js, p, macro_strats, key)

    assert new_js.year.shape == (8,)
    assert new_js.month[0] == 2
    assert jnp.mean(new_js.pressure) == pytest.approx(new_cs.pressure)

    # Verify that different jurisdictions ended up with different pressures due to starting point
    assert new_js.pressure[0] != new_js.pressure[-1]
