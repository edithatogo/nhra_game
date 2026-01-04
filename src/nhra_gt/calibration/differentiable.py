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

from nhra_gt.domain.state import Params, StateJax
from nhra_gt.engine import step_jax

# Define which parameters we want to calibrate and their typical bounds
PARAM_NAMES = [
    "cost_shifting_intensity",
    "fragmentation_index",
    "discharge_delay_base",
    "political_salience",
]


def map_to_params(values: Float[Array, n], base_params: Params) -> Params:
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
        # Simplified 'soft' heuristics for differentiability
        obs_pressure = carry_state.reported_pressure

        # Probability of 'Aggressive' or 'Reform' moves
        p_barg = jax.nn.sigmoid(0.6 * (1.2 - obs_pressure) - 0.4 * params.political_salience)
        p_def = jax.nn.sigmoid(1.3 * (carry_state.reported_efficiency_gap - 0.25))
        p_shift = jax.nn.sigmoid(-1.1 * (obs_pressure - 1.0))
        p_aged = 0.5
        p_ndis = 0.5

        # We return EXPECTED strategies (floats between 0 and 1)
        # step_jax handles these as weights in its logic
        strats = jnp.zeros(13)
        strats = strats.at[1].set(p_def)  # DEF
        strats = strats.at[2].set(p_barg)  # BARG
        strats = strats.at[3].set(p_shift)  # SHIFT
        strats = strats.at[5].set(p_aged)  # AGED
        strats = strats.at[6].set(p_ndis)  # NDIS
        strats = strats.at[9].set(0.9)  # SIGNAL_QUALITY

        next_s = step_jax(carry_state, params, strats, key)
        return next_s, next_s

    keys = jax.random.split(prng_key, num_steps)
    final_state, trajectory = lax.scan(body_func, init_state, keys)
    return final_state, trajectory


def loss_fn(
    values: Float[Array, n],
    target_within4: Float[Array, num_steps],
    init_state: StateJax,
    base_params: Params,
    prng_key: Any,
) -> Float[Array, ""]:
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
) -> Float[Array, n]:
    """Performs differentiable calibration using manual Gradient Descent."""

    # Initial guess (from base_params)
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
    grad_fn = jax.jit(jax.grad(loss_fn))

    for i in range(max_iter):
        grads = grad_fn(x, target_within4, init_state, base_params, prng_key)

        # Simple GD update
        x = x - learning_rate * grads

        if i % 20 == 0:
            loss_fn(x, target_within4, init_state, base_params, prng_key)

    return x
