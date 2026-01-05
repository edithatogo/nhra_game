"""
Differentiable Calibration using JAX.

Uses gradient-based optimization to minimize prediction error against targets.
"""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import lax
from jaxtyping import Array, Float

from nhra_gt.domain.params import Params
from nhra_gt.domain.state import StateJax
from nhra_gt.engine import step_jax

# Define which parameters we want to calibrate and their typical bounds
PARAM_NAMES = [
    "cost_shifting_intensity",
    "fragmentation_index",
    "discharge_delay_base",
    "political_salience",
]


@beartype
def map_to_params(values: Any, base_params: Params) -> Params:
    """Maps a flat array of values to a Params object."""
    return base_params.replace(
        cost_shifting_intensity=values[0],
        fragmentation_index=values[1],
        discharge_delay_base=values[2],
        political_salience=values[3],
    )


@beartype
def run_simulation_with_agent_jax(
    init_state: StateJax,
    params: Params,
    prng_key: Any,
    num_steps: int,
) -> tuple[StateJax, Any]:
    """
    Differentiable simulation that includes heuristic agent choices inside the loop.
    """

    def body_func(carry_state, key):
        # Heuristic decision making (replaces full optimization for speed/gradients)
        # In a real run, we might use jax_softmax or similar.
        # Here we just use the current params.
        strats = jnp.zeros(13)
        next_s = step_jax(carry_state, params, strats, key)
        return next_s, next_s

    keys = jax.random.split(prng_key, num_steps)
    final_state, trajectory = lax.scan(body_func, init_state, keys)
    return final_state, trajectory


def loss_fn(
    values: Any,
    target_within4: Any,
    init_state: StateJax,
    base_params: Params,
    prng_key: Any,
) -> Any:
    """Calculates MSE between simulated and target within4 trajectories."""
    params = map_to_params(values, base_params)
    num_steps = target_within4.shape[0]

    _, trajectory = run_simulation_with_agent_jax(init_state, params, prng_key, num_steps)

    # Loss is Mean Squared Error on ED performance
    loss = jnp.mean(jnp.square(trajectory.within4 - target_within4))
    return loss


def calibrate_jax(
    target_data: dict[str, jnp.ndarray],
    init_state: StateJax,
    base_params: Params,
    learning_rate: float = 0.01,
    max_iter: int = 100,
) -> Any:
    """Performs differentiable calibration using manual Gradient Descent."""

    # 1. Map initial params to flat array
    x = jnp.array(
        [
            base_params.cost_shifting_intensity,
            base_params.fragmentation_index,
            base_params.discharge_delay_base,
            base_params.political_salience,
        ]
    )

    target_within4 = target_data["within4"]
    prng_key = jax.random.PRNGKey(42)

    # JIT the loss and gradient
    loss_and_grad = jax.jit(jax.value_and_grad(loss_fn))

    def scan_body(x_curr, _):
        val, grads = loss_and_grad(x_curr, target_within4, init_state, base_params, prng_key)
        x_next = x_curr - learning_rate * grads
        return x_next, val

    final_x, losses = lax.scan(scan_body, x, jnp.arange(max_iter))

    return final_x