"""JAX-compatible simulation solvers and game-theoretic equilibrium tools."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Literal

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
        tol: Legacy tolerance argument. Callers compare the returned residual.

    Returns:
        A tuple of (row_strategy, col_strategy, residual). The residual measures
        the logit response error at the returned profile, with the telemetry floor.
    """
    # Keep the original fixed-length scan for callers of the compiled solver.
    del tol
    m, n = u_row.shape

    def logit_choice(utilities):
        u = utilities - jnp.max(utilities)
        z = jnp.exp(lam * u)
        return z / jnp.sum(z)

    def responses(p: Array, q: Array) -> tuple[Array, Array]:
        return logit_choice(u_row @ q), logit_choice(p @ u_col)

    def scan_body(val: tuple[Array, Array], _: Any) -> tuple[tuple[Array, Array], None]:
        return responses(*val), None

    (p_final, q_final), _ = lax.scan(
        scan_body, (jnp.ones(m) / m, jnp.ones(n) / n), jnp.arange(max_iter)
    )
    p_response, q_response = responses(p_final, q_final)
    res_final = jnp.max(jnp.abs(p_response - p_final)) + jnp.max(jnp.abs(q_response - q_final))

    return p_final, q_final, jnp.maximum(res_final, jnp.asarray(1e-12, dtype=res_final.dtype))


@beartype
def regret_min_solver_jax(
    u_row: Any,
    u_col: Any,
    max_iter: int = 500,
    learning_rate: float = 0.05,
) -> tuple[Any, Any, Any]:
    """Finds approximate Nash equilibrium by minimizing total regret using gradient descent.

    Args:
        u_row: Payoff matrix for the row player.
        u_col: Payoff matrix for the column player.
        max_iter: Number of optimization iterations.
        learning_rate: Step size for gradient descent.

    Returns:
        A tuple of (row_strategy, col_strategy, final_regret).
    """
    m, n = u_row.shape

    def total_regret(params: tuple[Array, Array]) -> Float[Array, ""]:
        p_logit, q_logit = params
        p = jax.nn.softmax(p_logit)
        q = jax.nn.softmax(q_logit)

        # Expected payoffs
        pay_row = p @ u_row @ q
        pay_col = p @ u_col @ q

        # Best possible payoffs
        best_row = jnp.max(u_row @ q)
        best_col = jnp.max(p @ u_col)

        return (best_row - pay_row) + (best_col - pay_col)

    # Initial logits (uniform)
    p_logits = jnp.zeros(m)
    q_logits = jnp.zeros(n)

    # Simple gradient descent loop
    def scan_body(logits: tuple[Array, Array], _: Any) -> tuple[tuple[Array, Array], Array]:
        grads = jax.grad(total_regret)(logits)
        next_logits = (
            logits[0] - learning_rate * grads[0],
            logits[1] - learning_rate * grads[1],
        )
        # Calculate current regret
        curr_regret = total_regret(next_logits)
        return next_logits, curr_regret

    final_logits, regrets = lax.scan(scan_body, (p_logits, q_logits), jnp.arange(max_iter))

    final_regret = regrets[-1]
    return (
        jax.nn.softmax(final_logits[0]),
        jax.nn.softmax(final_logits[1]),
        jnp.maximum(final_regret, jnp.asarray(1e-12, dtype=final_regret.dtype)),
    )


@beartype
@dataclass(frozen=True)
class _ThreePlayerQreOptions:
    """Parameters of the fixed-point QRE iteration."""

    lam: float = 5.0
    max_iter: int = 100
    tol: float = 1e-06


@beartype
def qre_3player_jax(
    u1: Float[Array, "m n k"], u2: Any, u3: Any, *options: Any, **named_options: Any
) -> tuple[Any, Any, Any, Any]:
    """Run fixed-budget logit response iteration for a three-player game.

    Args:
        u1: Payoff for player 1.
        u2: Payoff for player 2.
        u3: Payoff for player 3.
        *options: Historical positional values for lam, max_iter and tol.
        **named_options: The same values by keyword.
        lam: Rationality parameter.
        max_iter: Max iterations.
        tol: Legacy tolerance argument. Use solve_three_player_qre to qualify the result.

    Returns:
        The final three strategy vectors and their summed maximum response errors.
    """
    settings = _ThreePlayerQreOptions(*options, **named_options)
    lam = settings.lam
    max_iter = settings.max_iter
    tol = settings.tol
    # Keep the tolerance argument for callers of the fixed-iteration solver.
    del tol
    m, n, k_dim = u1.shape

    def responses(p1: Array, p2: Array, p3: Array) -> tuple[Array, Array, Array]:
        e1 = jnp.einsum("ijk,j,k->i", u1, p2, p3)
        e2 = jnp.einsum("ijk,i,k->j", u2, p1, p3)
        e3 = jnp.einsum("ijk,i,j->k", u3, p1, p2)
        return (
            jax.nn.softmax(lam * e1),
            jax.nn.softmax(lam * e2),
            jax.nn.softmax(lam * e3),
        )

    def scan_body(
        probs: tuple[Array, Array, Array], _: Any
    ) -> tuple[tuple[Array, Array, Array], None]:
        return responses(*probs), None

    initial = (jnp.ones(m) / m, jnp.ones(n) / n, jnp.ones(k_dim) / k_dim)
    (p1, p2, p3), _ = lax.scan(scan_body, initial, jnp.arange(max_iter))
    response1, response2, response3 = responses(p1, p2, p3)
    residual = (
        jnp.max(jnp.abs(response1 - p1))
        + jnp.max(jnp.abs(response2 - p2))
        + jnp.max(jnp.abs(response3 - p3))
    )
    return p1, p2, p3, residual


@dataclass(frozen=True)
class ThreePlayerQreResult:
    """Convergence status, measured response error and any qualified strategies."""

    status: Literal["converged", "nonconverged"]
    residual: float
    strategies: tuple[Array, Array, Array] | None


def solve_three_player_qre(
    payoffs: tuple[Array, Array, Array],
    *,
    lam: float = _ThreePlayerQreOptions.lam,
    max_iter: int = _ThreePlayerQreOptions.max_iter,
    tol: float = _ThreePlayerQreOptions.tol,
) -> ThreePlayerQreResult:
    """Qualify the fixed-budget result at the Python boundary.

    Supply one payoff tensor per player in seat order. A residual in
    [0, tol] qualifies the corresponding strategies. Other residuals are
    reported as nonconverged with no strategies. Use qre_3player_jax inside
    JAX transformations.
    """
    if not isfinite(tol) or tol < 0.0:
        message = "QRE tolerance must be finite and nonnegative"
        raise ValueError(message)

    p1, p2, p3, residual = qre_3player_jax(*payoffs, lam=lam, max_iter=max_iter)
    error = float(residual)
    if 0.0 <= error <= tol:
        return ThreePlayerQreResult("converged", error, (p1, p2, p3))
    return ThreePlayerQreResult("nonconverged", error, None)


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
