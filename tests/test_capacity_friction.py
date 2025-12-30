from __future__ import annotations

from dataclasses import replace

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import Params, baseline_state, step
from nhra_gt.engine_jax import baseline_state_jax, step_jax
from nhra_gt.rules import initialize_rules


def test_legacy_asymmetric_lag():
    """Verify that expansion lag differs from contraction lag in legacy engine."""
    p = Params(expansion_lag=0.1, contraction_lag=0.5, bed_capacity_index=1.0)
    p = initialize_rules(p)

    # 1. Test Expansion (Target > Current)
    s_exp = baseline_state(p=p)  # current=1.0
    s_exp = replace(s_exp, target_capacity=1.5, current_capacity=1.0)

    # Run one step
    s_next_exp = step(s_exp, p, {}, np.random.default_rng(42))

    # Expected: 1.0 + 0.1 * (1.5 - 1.0) = 1.05
    assert pytest.approx(s_next_exp.current_capacity) == 1.05

    # 2. Test Contraction (Target < Current)
    s_con = replace(s_exp, target_capacity=0.5, current_capacity=1.0)
    s_next_con = step(s_con, p, {}, np.random.default_rng(42))

    # Expected: 1.0 + 0.5 * (0.5 - 1.0) = 0.75
    assert pytest.approx(s_next_con.current_capacity) == 0.75


def test_legacy_adjustment_costs():
    """Verify that adjustment costs are calculated and subtracted from balance."""
    p = Params(adjustment_cost_beta=10.0, expansion_lag=1.0)  # Lag 1.0 means instant move
    p = initialize_rules(p)
    s = baseline_state(p=p)
    s = replace(s, target_capacity=1.1, current_capacity=1.0, reconciliation_balance=0.0)

    # Delta Cap = 1.1 - 1.0 = 0.1
    # Cost = 10.0 * (0.1^2) = 10.0 * 0.01 = 0.1

    s_next = step(s, p, {}, np.random.default_rng(42))

    assert s_next.adjustment_costs == pytest.approx(0.1)
    # Check that it hit reconciliation
    assert s_next.reconciliation_balance <= -0.1


def test_jax_asymmetric_lag():
    """Verify that expansion lag differs from contraction lag in JAX engine."""
    p = ParamsJax(expansion_lag=0.1, contraction_lag=0.5, bed_capacity_index=1.0)
    p = initialize_rules(p)
    key = jax.random.PRNGKey(42)

    # 1. Test Expansion
    s_exp = baseline_state_jax(2025, p)
    s_exp = s_exp.replace(target_capacity=1.5, current_capacity=1.0)

    strategies = jnp.zeros(12)
    s_next_exp = step_jax(s_exp, p, strategies, key)

    assert pytest.approx(float(s_next_exp.current_capacity)) == 1.05

    # 2. Test Contraction
    s_con = s_exp.replace(target_capacity=0.5, current_capacity=1.0)
    s_next_con = step_jax(s_con, p, strategies, key)

    assert pytest.approx(float(s_next_con.current_capacity)) == 0.75


def test_jax_adjustment_costs():
    """Verify adjustment costs in JAX engine."""
    p = ParamsJax(adjustment_cost_beta=10.0, expansion_lag=1.0)
    p = initialize_rules(p)
    key = jax.random.PRNGKey(42)

    s = baseline_state_jax(2025, p)
    s = s.replace(target_capacity=1.1, current_capacity=1.0, reconciliation_balance=0.0)

    strategies = jnp.zeros(12)
    s_next = step_jax(s, p, strategies, key)

    assert s_next.metrics.cumulative_adjustment_costs > 0
    assert float(s_next.reconciliation_balance) < 0
