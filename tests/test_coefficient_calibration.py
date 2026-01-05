from __future__ import annotations

import jax
import jax.numpy as jnp

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import baseline_state_jax, step_jax


def test_coefficient_calibration_demo():
    """
    Demonstrates that previously hardcoded coefficients can now be optimized
    using JAX gradients.
    """
    p_base = ParamsJax()
    init_state = baseline_state_jax(2025, p_base)
    key = jax.random.PRNGKey(42)
    strat = jnp.zeros(13)

    # 1. Define a loss function that depends on a nested coefficient
    def compute_loss(slope_value):
        # Create a modified params object with the new slope
        # NOTE: In JAX, we must use replace() to stay functional
        p_mod = p_base.replace(ops=p_base.ops.replace(occ_demand_slope=slope_value))

        # Run one step
        next_s = step_jax(init_state, p_mod, strat, key)

        # Target: we want occupancy to reach exactly 0.90
        target_occ = 0.90
        return jnp.square(next_s.occupancy - target_occ)

    # 2. Compute gradient of the loss with respect to the coefficient
    grad_fn = jax.grad(compute_loss)

    # Initial slope is 0.015
    initial_slope = 0.015
    initial_loss = compute_loss(initial_slope)

    gradient = grad_fn(initial_slope)

    # 3. Perform one step of gradient descent
    learning_rate = 0.1
    new_slope = initial_slope - learning_rate * gradient
    new_loss = compute_loss(new_slope)

    # Assertions
    assert new_loss < initial_loss
    print(f"Initial Loss: {initial_loss:.6f}")
    print(f"Gradient: {gradient:.6f}")
    print(f"New Slope: {new_slope:.6f}")
    print(f"New Loss: {new_loss:.6f}")


if __name__ == "__main__":
    test_coefficient_calibration_demo()
