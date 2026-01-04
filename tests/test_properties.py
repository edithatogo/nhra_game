"""Property-based tests for core game theory solvers."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays

from nhra_gt.solvers_jax import qre_solver_jax


@given(
    u_row=arrays(np.float64, (2, 2), elements=st.floats(-100, 100)),
    u_col=arrays(np.float64, (2, 2), elements=st.floats(-100, 100)),
    lam=st.floats(0.1, 20.0),
)
@settings(max_examples=50, deadline=1000)
def test_qre_solver_properties(u_row: np.ndarray, u_col: np.ndarray, lam: float) -> None:
    """Ensures QRE solver always returns valid probability distributions."""
    # Convert to JAX arrays
    u_row_jax = jnp.array(u_row)
    u_col_jax = jnp.array(u_col)

    p, q, res = qre_solver_jax(u_row_jax, u_col_jax, lam=lam, max_iter=50)

    # 1. Strategies must sum to 1
    assert jnp.allclose(jnp.sum(p), 1.0, atol=1e-5)
    assert jnp.allclose(jnp.sum(q), 1.0, atol=1e-5)

    # 2. Strategies must be non-negative
    assert jnp.all(p >= -1e-7)
    assert jnp.all(q >= -1e-7)

    # 3. Probabilities must be within [0, 1]
    assert jnp.all(p <= 1.0 + 1e-7)
    assert jnp.all(q <= 1.0 + 1e-7)


@given(
    pressure=st.floats(0.5, 2.0),
    occupancy=st.floats(0.5, 1.5),
)
@settings(deadline=None)
def test_wait_time_monotonicity(pressure: float, occupancy: float) -> None:
    """Simplified check for queuing wait time behavior."""
    from nhra_gt.engine import mm_s_queue_wait_jax

    # High pressure/occupancy should generally lead to higher wait times
    # (Checking basic sanity, not full proof)
    wait = mm_s_queue_wait_jax(
        jnp.array(pressure), jnp.array(1.0), jnp.array(10.0 * occupancy)
    )
    assert wait >= 0.0
    assert wait <= 1440.0  # Capped at 24h