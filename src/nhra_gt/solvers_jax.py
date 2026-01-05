"""
JAX-Accelerated Game Theory Solvers.

This module provides high-performance solvers for various equilibrium concepts,
including Quantal Response Equilibrium (QRE), Regret Minimization,
Stackelberg (Leader-Follower), and Rubinstein bargaining. All solvers are
designed to be compatible with JAX transformations (`jit`, `vmap`, `grad`).
"""

from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import lax
from jaxtyping import Array, Float

# ----------------------------
# Quantal Response Equilibrium (QRE)
# ----------------------------


@beartype
def qre_solver_jax(
    u_row: Any,
    u_col: Any,
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Any, Any, Any]:
    """
    Solves for the Quantal Response Equilibrium (Logit-equilibrium).
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

    def logit_choice(utilities: Float[Array, ...]) -> Float[Array, ...]:
        # Stable logit/softmax
        u = utilities - jnp.max(utilities)
        z = jnp.exp(lam * u)
        return z / jnp.sum(z)

    def scan_body(
        val: tuple[Array, Array, Array], _: Any
    ) -> tuple[tuple[Array, Array, Array], None]:
        p, q, _ = val
        # Calculate expected utilities
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


# ----------------------------
# Regret Minimization Solver
# ----------------------------


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

        regret = (best_row - pay_row) + (best_col - pay_col)
        return regret

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


# ----------------------------
# Discrete Nash Oracle (Support Enumeration Wrapper)
# ----------------------------


@beartype
def discrete_nash_jax(
    u_row: Any, u_col: Any
) -> tuple[Any, Any]:
    """JAX-friendly wrapper for finding a pure Nash equilibrium in a discrete game.

    Since pure Nash is non-differentiable, this is used as an Oracle or for comparison.
    If multiple exist, it returns the payoff-dominant one.

    Args:
        u_row: Payoff matrix for the row player.
        u_col: Payoff matrix for the column player.

    Returns:
        A tuple of (row_strategy, col_strategy) as one-hot vectors if a pure NE is found.
    """
    # For 2x2 games (most of our stage games), we can do brute force
    m, n = u_row.shape

    # 1. Find all pure strategy profiles
    row_best = jnp.max(u_row, axis=0)  # shape (n,)
    col_best = jnp.max(u_col, axis=1)  # shape (m,)

    is_row_best = u_row == row_best
    is_col_best = u_col == col_best.reshape(-1, 1)

    is_ne = is_row_best & is_col_best

    # 2. Select payoff dominant
    total_payoff = u_row + u_col
    masked_payoff = jnp.where(is_ne, total_payoff, -1e9)

    best_idx = jnp.argmax(masked_payoff.flatten())
    row_idx = best_idx // n
    col_idx = best_idx % n

    p = jnp.zeros(m).at[row_idx].set(1.0)
    q = jnp.zeros(n).at[col_idx].set(1.0)

    return p, q


# ----------------------------
# Hierarchical / Hybrid Games
# ----------------------------


def solve_hierarchical_game_jax(
    macro_row_matrix: Any,
    macro_col_matrix: Any,
    micro_game_factory: Any,  # Function that takes macro outcome and returns matrices
    lam: float = 5.0,
) -> tuple[Any, Any, Any]:
    """
    Solves a nested hierarchical game using backward induction.

    The macro game payoffs are augmented by the equilibrium utilities of the
    resulting micro games for each macro strategy profile.

    Args:
        macro_row_matrix: Baseline payoffs for the macro row player.
        macro_col_matrix: Baseline payoffs for the macro column player.
        micro_game_factory: A function (i, j) -> (u_micro_row, u_micro_col).
        lam: QRE rationality parameter.

    Returns:
        A tuple of (macro_row_strat, macro_col_strat, micro_utilities_matrix).
    """
    m, n = macro_row_matrix.shape

    def get_micro_utility(i: int, j: int) -> float:
        """Helper to resolve a specific micro game cell."""
        # Resolve micro game for cell (i, j)
        u_micro_row, u_micro_col = micro_game_factory(i, j)
        p_micro, q_micro, _ = qre_solver_jax(u_micro_row, u_micro_col, lam=lam)
        return p_micro @ u_micro_row @ q_micro, p_micro @ u_micro_col @ q_micro

    # Vmap over the matrix indices
    row_indices = jnp.repeat(jnp.arange(m), n)
    col_indices = jnp.tile(jnp.arange(n), m)

    micro_utilities_row, micro_utilities_col = jax.vmap(get_micro_utility)(row_indices, col_indices)

    # 2. Add micro-utility to macro matrix
    effective_macro_row = macro_row_matrix + micro_utilities_row.reshape(m, n)
    effective_macro_col = macro_col_matrix + micro_utilities_col.reshape(m, n)

    # 3. Solve the effective macro game
    p_macro, q_macro, _ = qre_solver_jax(effective_macro_row, effective_macro_col, lam=lam)

    return p_macro, q_macro, micro_utilities_row.reshape(m, n)


# ----------------------------
# Multi-Player Games
# ----------------------------


@beartype
def qre_3player_jax(
    u1: Float[Array, "m n k"],  # Payoff for P1 (m actions) given P2 (n) and P3 (k)
    u2: Any,  # Payoff for P2
    u3: Any,  # Payoff for P3
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Any, Any, Any, Any]:
    """
    Solves for QRE in a 3-player normal form game using tensor contractions.

    Args:
        u1, u2, u3: 3D payoff tensors for each player.
        lam: QRE rationality parameter.
        max_iter: Max fixed-point iterations.
        tol: Convergence tolerance.

    Returns:
        A tuple of (strat1, strat2, strat3, residual).
    """
    m, n, k = u1.shape

    def scan_body(probs, _):
        p1, p2, p3, _ = probs

        # Expected utilities for P1
        # Sum over p2 and p3: E[U1] = sum_j sum_l u1[i,j,l] * p2[j] * p3[l]
        # Equivalent to tensor contraction
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
    p3_0 = jnp.ones(k) / k

    (pf1, pf2, pf3, res_final), _ = lax.scan(
        scan_body, (p1_0, p2_0, p3_0, jnp.array(1.0)), jnp.arange(max_iter)
    )

    return pf1, pf2, pf3, res_final


# ----------------------------
# Sequential / Extensive Form Solvers
# ----------------------------


@beartype
def rubinstein_jax(
    pie_size: float | Float[Array, ""],
    delta_1: float | Float[Array, ""],
    delta_2: float | Float[Array, ""],
) -> Float[Array, ""]:
    """
    JAX implementation of Rubinstein bargaining share for Player 1 (First Mover).
    Share = (1 - delta_2) / (1 - delta_1 * delta_2).
    """
    # Clip deltas to avoid division by zero or singularity at 1.0
    d1 = jnp.clip(delta_1, 0.0, 0.9999)
    d2 = jnp.clip(delta_2, 0.0, 0.9999)

    share = (1.0 - d2) / (1.0 - d1 * d2)
    return pie_size * share


@beartype
def stackelberg_jax(
    u_leader: Any, u_follower: Any
) -> tuple[Any, Any]:
    """
    JAX implementation of Stackelberg Equilibrium (Row=Leader).
    Returns one-hot strategies.
    """
    m, n = u_leader.shape

    # 1. Follower Best Response for each Row
    # follower_payoff[i, :] -> max over columns -> index j*(i)
    # best_col_indices[i] = argmax_j u_follower[i, j]
    follower_best_vals = jnp.max(u_follower, axis=1, keepdims=True)
    is_best_response = u_follower == follower_best_vals  # (m, n) mask

    # 2. Leader Payoff given Follower BR
    # Leader utility if they pick row i = u_leader[i, j*(i)]
    # We filter u_leader by the is_best_response mask.
    # If multiple BRs, we assume optimistic or pessimistic?
    # Standard: Leader anticipates one of them. Optimistic usually.
    # Mask u_leader, set non-BR to -inf
    leader_outcomes = jnp.where(is_best_response, u_leader, -jnp.inf)

    # 3. Leader Maximization
    # Max over the whole matrix (since only valid (i, j*(i)) pairs are not -inf)
    flat_idx = jnp.argmax(leader_outcomes.flatten())
    row_idx = flat_idx // n
    col_idx = flat_idx % n

    p = jnp.zeros(m).at[row_idx].set(1.0)
    q = jnp.zeros(n).at[col_idx].set(1.0)

    return p, q
