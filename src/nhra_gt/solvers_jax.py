"""JAX-compatible simulation solvers and game-theoretic equilibrium tools."""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import lax
from jaxtyping import Array, Float


@beartype
def qre_solver_jax(
    u_row: Float[Array, "m n"],
    u_col: Float[Array, "m n"],
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Any, Any, Any]:
    """Solves for the Quantal Response Equilibrium (Logit-equilibrium).

    Uses fixed-point iteration: p = logit(u_row @ q), q = logit(p @ u_col).

    Args:
        u_row: Payoff matrix for the row player.
        u_col: Payoff matrix for the column player.
        lam: Rationality parameter (lambda). Higher = closer to Nash.
        max_iter: Maximum number of iterations.
        tol: Convergence tolerance.

    Returns:
        A tuple of (row_strategy, col_strategy, residual).
    """
    m, n = u_row.shape

    def logit_choice(utilities):
        u = utilities - jnp.max(utilities)
        z = jnp.exp(lam * u)
        return z / jnp.sum(z)

    def scan_body(
        val: tuple[Array, Array, Array], _: Any
    ) -> tuple[tuple[Array, Array, Array], None]:
        p, q, _ = val
        exp_u_row = u_row @ q
        exp_u_col = p @ u_col

        # Update distributions
        next_p = logit_choice(exp_u_row)
        next_q = logit_choice(exp_u_col)

        # Convergence residual
        res = jnp.max(jnp.abs(next_p - p)) + jnp.max(jnp.abs(next_q - q))

        return (next_p, next_q, res), None

    (p_final, q_final, res_final), _ = lax.scan(
        scan_body, (jnp.ones(m) / m, jnp.ones(n) / n, jnp.array(1.0)), jnp.arange(max_iter)
    )

    return p_final, q_final, jnp.maximum(res_final, jnp.asarray(1e-12, dtype=res_final.dtype))


@beartype
def qre_3player_jax(
    u1: Float[Array, "m n k"],
    u2: Any,
    u3: Any,
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Any, Any, Any, Any]:
    """Solves for QRE in a 3-player normal form game using tensor contractions.

    Args:
        u1: Payoff for player 1.
        u2: Payoff for player 2.
        u3: Payoff for player 3.
        lam: Rationality parameter.
        max_iter: Max iterations.
        tol: Tolerance.

    Returns:
        Strategies for all three players and the final residual.
    """
    m, n, k_dim = u1.shape

    def scan_body(probs, _):
        p1, p2, p3, _ = probs

        # Expected utilities for P1
        e1 = jnp.einsum("ijk,j,k->i", u1, p2, p3)
        e2 = jnp.einsum("ijk,i,k->j", u2, p1, p3)
        e3 = jnp.einsum("ijk,i,j->k", u3, p1, p2)

        # Softmax
        next_p1 = jax.nn.softmax(lam * e1)
        next_p2 = jax.nn.softmax(lam * e2)
        next_p3 = jax.nn.softmax(lam * e3)

        # Residual
        res = (
            jnp.max(jnp.abs(next_p1 - p1))
            + jnp.max(jnp.abs(next_p2 - p2))
            + jnp.max(jnp.abs(next_p3 - p3))
        )

        return (next_p1, next_p2, next_p3, res), None

    p1_0 = jnp.ones(m) / m
    p2_0 = jnp.ones(n) / n
    p3_0 = jnp.ones(k_dim) / k_dim

    (pf1, pf2, pf3, res_final), _ = lax.scan(
        scan_body, (p1_0, p2_0, p3_0, jnp.array(1.0)), jnp.arange(max_iter)
    )

    return pf1, pf2, pf3, res_final


@beartype
def rubinstein_jax(
    pie_size: float | Float[Array, ""],
    delta_1: float | Float[Array, ""],
    delta_2: float | Float[Array, ""],
) -> Float[Array, ""]:
    """JAX implementation of Rubinstein bargaining share for Player 1 (First Mover).

    Share = (1 - delta_2) / (1 - delta_1 * delta_2).
    """
    # Clip deltas to avoid division by zero or singularity at 1.0
    d1 = jnp.clip(delta_1, 0.0, 0.9999)
    d2 = jnp.clip(delta_2, 0.0, 0.9999)

    share = (1.0 - d2) / (1.0 - d1 * d2)
    return pie_size * share


@beartype
def stackelberg_jax(u_leader: Any, u_follower: Any) -> tuple[Any, Any]:
    """JAX implementation of Stackelberg Equilibrium (Row=Leader).

    Returns one-hot strategies.
    """
    m, n = u_leader.shape

    # 1. Follower Best Response for each Row
    follower_best_vals = jnp.max(u_follower, axis=1, keepdims=True)
    is_best_response = u_follower == follower_best_vals

    # 2. Leader Payoff given Follower BR
    leader_outcomes = jnp.where(is_best_response, u_leader, -jnp.inf)

    # 3. Leader Maximization
    flat_idx = jnp.argmax(leader_outcomes.flatten())
    row_idx = flat_idx // n
    col_idx = flat_idx % n

    p = jnp.zeros(m).at[row_idx].set(1.0)
    q = jnp.zeros(n).at[col_idx].set(1.0)

    return p, q


@beartype
def discrete_nash_jax(u_row: Any, u_col: Any) -> tuple[Any, Any]:
    """JAX-friendly wrapper for finding a pure Nash equilibrium in a discrete game.

    Since pure Nash is non-differentiable, this is used as an Oracle or for comparison.
    If multiple exist, it returns the payoff-dominant one.

    Args:
        u_row: Payoff matrix for the row player.
        u_col: Payoff matrix for the column player.

    Returns:
        A tuple of (row_strategy, col_strategy) as one-hot vectors if a pure NE is found.
    """
    m, n = u_row.shape
    row_best = jnp.max(u_row, axis=0)
    col_best = jnp.max(u_col, axis=1)

    is_row_best = u_row == row_best
    is_col_best = u_col == col_best.reshape(-1, 1)

    is_ne = is_row_best & is_col_best

    total_payoff = u_row + u_col
    masked_payoff = jnp.where(is_ne, total_payoff, -1e9)

    best_idx = jnp.argmax(masked_payoff.flatten())
    row_idx = best_idx // n
    col_idx = best_idx % n

    p = jnp.zeros(m).at[row_idx].set(1.0)
    q = jnp.zeros(n).at[col_idx].set(1.0)

    return p, q
