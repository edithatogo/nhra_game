"""Verification of JAX purity for core simulation logic."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.domain.state import BaselineProvider
from nhra_gt.engine import step_jax, _pad_strategies


def test_step_jax_is_jitable():
    """Ensure the core step function can be JIT-compiled without errors."""
    params, state = BaselineProvider.get_baseline()
    key = jax.random.PRNGKey(42)
    strategies = jnp.zeros(13)

    # JIT compile
    jitted_step = jax.jit(step_jax)

    # Run once to compile
    next_state = jitted_step(state, params, strategies, key)

    # Run again to ensure no side effects
    next_state_2 = jitted_step(state, params, strategies, key)

    # Check structural equality (leaf by leaf)
    chex_available = False
    try:
        import chex
        chex_available = True
        chex.assert_trees_all_close(next_state, next_state_2)
    except ImportError:
        pass

    # Basic check
    assert jnp.allclose(next_state.pressure, next_state_2.pressure)


def test_pad_strategies_purity():
    """Ensure strategy padding works within JIT."""
    
    @jax.jit
    def padded_op(s):
        return _pad_strategies(s)

    s = jnp.ones(5)
    out = padded_op(s)
    assert out.shape == (13,)
    assert out[0] == 1.0
    assert out[12] == 0.0
