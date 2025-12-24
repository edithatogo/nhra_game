from __future__ import annotations

import numpy as np
import pytest

# Skip if jax not installed
try:
    import jax  # noqa: F401
    import jax.numpy as jnp

    HAS_JAX = True
except ImportError:
    HAS_JAX = False


@pytest.mark.skipif(not HAS_JAX, reason="JAX not installed")
def test_jax_array_compatibility() -> None:
    """Verify that we can create JAX arrays from numpy arrays."""
    arr = np.array([1.0, 2.0, 3.0])
    jarr = jnp.array(arr)
    assert jnp.allclose(jarr, arr)


@pytest.mark.skipif(not HAS_JAX, reason="JAX not installed")
def test_nash_solver_placeholder() -> None:
    """Placeholder for JAX-based Nash solver verification."""
    # Future: implement projected gradient descent here
    pass
