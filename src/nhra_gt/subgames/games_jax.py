from __future__ import annotations

import jax.numpy as jnp
from beartype import beartype
from flax import struct
from jaxtyping import Array, Float


@struct.dataclass
class GameParamsJax:
    pressure: float
    efficiency_gap: float
    discharge_delay: float
    political_salience: float
    audit_pressure: float
    cost_shifting_intensity: float
    political_capital: float


@beartype
def renegotiation_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """
    JAX-native renegotiation game.
    Returns (u_row, u_col) matrices.
    Actions: Row(C, E), Col(A, H)
    """
    pr = gp.pressure
    cth_fallout_cost = 0.8 * pr
    state_failure_cost = 0.6 * pr

    u_row = jnp.array([[1.0 - 0.1, 1.0 - 0.3], [1.0, 1.0 - cth_fallout_cost]])

    u_col = jnp.array([[1.0 + 0.2, 1.0 + 0.5], [1.0, 1.0 - state_failure_cost]])

    return u_row, u_col


@beartype
def definition_game_jax(gp: GameParamsJax) -> tuple[Float[Array, "2 2"], Float[Array, "2 2"]]:
    """Actions: Row(R, E), Col(R, E)"""
    pr, eg, ps = gp.pressure, gp.efficiency_gap, gp.political_salience

    realism_benefit = 0.5 + 0.8 * eg + 0.4 * (pr - 1.0)
    realism_cost = 0.25 + 0.35 * ps
    strict_benefit = 0.35 + 0.45 * ps
    strict_cost = 0.30 + 0.50 * pr

    u_row = jnp.array(
        [
            [1.0 + realism_benefit - realism_cost, 1.0 - 0.15 - realism_cost],
            [1.0 + strict_benefit - strict_cost, 1.0 - 0.45 - strict_cost],
        ]
    )
    u_col = jnp.array([[1.0 + realism_benefit - 0.15, 1.0 - 0.20], [1.0 - 0.35, 1.0 - 0.55]])
    return u_row, u_col
