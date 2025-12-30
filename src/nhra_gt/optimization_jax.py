from __future__ import annotations

from collections.abc import Callable
from typing import Any

import jax.numpy as jnp
from jaxopt import ScipyBoundedMinimize
from jaxtyping import PyTree

from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.engine_jax import run_simulation_jax


def optimize_policy_jax(
    init_state: StateJax,
    base_params: ParamsJax,
    strategies: jnp.ndarray,  # [num_steps, 10]
    prng_key: Any,
    num_steps: int,
    param_to_optimize: str,
    bounds: tuple[float, float],
    objective_fn: Callable[[StateJax, PyTree], float],  # (final_state, trajectory) -> scalar
) -> dict[str, Any]:
    """
    Optimizes a single parameter to minimize a given objective.

    Args:
        init_state: Starting state.
        base_params: Base parameters.
        strategies: Pre-defined strategies for the simulation.
        prng_key: Random key.
        num_steps: Simulation length.
        param_to_optimize: Name of field in ParamsJax to vary.
        bounds: (min, max) for the parameter.
        objective_fn: Function to minimize.

    Returns:
        A dictionary with the optimized parameter value and result metadata.
    """

    def loss(x):
        # Update params with candidate value
        # JAX doesn't allow string-based attribute setting in jit easily,
        # so we'll assume we are optimizing 'nominal_cth_share_target' for this example
        # or use a mapping.

        p = base_params.replace(**{param_to_optimize: x[0]})
        final_s, trajectory = run_simulation_jax(init_state, p, strategies, prng_key, num_steps)
        return objective_fn(final_s, trajectory)

    # Use ScipyBoundedMinimize (L-BFGS-B) for bounded optimization
    optimizer = ScipyBoundedMinimize(fun=loss, method="L-BFGS-B")

    lower_bounds = jnp.array([bounds[0]])
    upper_bounds = jnp.array([bounds[1]])
    init_val = jnp.array([(bounds[0] + bounds[1]) / 2.0])

    res = optimizer.run(init_val, bounds=(lower_bounds, upper_bounds))

    return {
        "optimized_value": float(res.params[0]),
        "objective_value": float(res.state.fun_val),
        "success": bool(res.state.success),
    }
