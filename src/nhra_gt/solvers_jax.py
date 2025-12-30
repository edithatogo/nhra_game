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
    u_row: Float[Array, "m n"],
    u_col: Float[Array, "m n"],
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Float[Array, "m"], Float[Array, "n"], Float[Array, ""]]:
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

    def logit_choice(utilities: Array) -> Array:
        # Stable logit/softmax
        u = utilities - jnp.max(utilities)
        z = jnp.exp(lam * u)
        return z / jnp.sum(z)

    def scan_body(val, _):
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

    return p_final, q_final, res_final


# ----------------------------
# Regret Minimization Solver
# ----------------------------


@beartype
def regret_min_solver_jax(
    u_row: Float[Array, "m n"],
    u_col: Float[Array, "m n"],
    learning_rate: float = 0.1,
    max_iter: int = 500,
    tol: float = 1e-5,
) -> tuple[Float[Array, "m"], Float[Array, "n"], Float[Array, ""]]:
    """
    Finds approximate equilibrium by minimizing total regret using gradient descent.
    Differentiable through the optimization process.
    """
    m, n = u_row.shape

    def total_regret(params):
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
    def scan_body(logits, _):
        grads = jax.grad(total_regret)(logits)
        next_logits = (logits[0] - learning_rate * grads[0], logits[1] - learning_rate * grads[1])
        # Calculate current regret
        curr_regret = total_regret(next_logits)
        return next_logits, curr_regret

    final_logits, regrets = lax.scan(scan_body, (p_logits, q_logits), jnp.arange(max_iter))

    return jax.nn.softmax(final_logits[0]), jax.nn.softmax(final_logits[1]), regrets[-1]


# ----------------------------
# Discrete Nash Oracle (Support Enumeration Wrapper)
# ----------------------------


@beartype
def discrete_nash_jax(
    u_row: Float[Array, "m n"], u_col: Float[Array, "m n"]
) -> tuple[Float[Array, "m"], Float[Array, "n"]]:
    """
    JAX-friendly wrapper for finding a pure Nash equilibrium.
    Since pure Nash is non-differentiable, this is used as an Oracle or for comparison.
    If multiple exist, it returns the payoff-dominant one.
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
    macro_row_matrix: Float[Array, "m n"],
    macro_col_matrix: Float[Array, "m n"],
    micro_game_factory: Any,  # Function that takes macro outcome and returns matrices
    lam: float = 5.0,
) -> tuple[Float[Array, "m"], Float[Array, "n"], Float[Array, "m n"]]:
    """
    Solves a nested hierarchical game.
    The macro game results determine the parameters of the micro games.
    Uses backward induction (or approximation thereof) for equilibrium.
    """
    m, n = macro_row_matrix.shape

    def get_micro_utility(i, j):
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
    u2: Float[Array, "m n k"],  # Payoff for P2
    u3: Float[Array, "m n k"],  # Payoff for P3
    lam: float = 5.0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> tuple[Float[Array, "m"], Float[Array, "n"], Float[Array, "k"], Float[Array, ""]]:
    """
    Solves for QRE in a 3-player normal form game.
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
