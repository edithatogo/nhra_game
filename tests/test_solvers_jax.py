"""Tests for solvers JAX."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from nhra_gt.solvers_jax import (
    discrete_nash_jax,
    qre_3player_jax,
    qre_solver_jax,
    regret_min_solver_jax,
)

_MIN_DOMINANT_ACTION_PROBABILITY = 0.9
_MAX_TOTAL_REGRET = 0.1
_MAX_LOGIT_RESIDUAL = 0.1


def test_qre_solver_basic():
    # Prisoners' Dilemma
    """Check qre solver basic."""
    u_row = jnp.array([[-1, -10], [0, -5]], dtype=float)
    u_col = jnp.array([[-1, 0], [-10, -5]], dtype=float)

    # At high lambda, should converge toward Nash (Defect, Defect) -> ([0, 1], [0, 1])
    p, q, _res = qre_solver_jax(u_row, u_col, lam=10.0)

    assert p[1] > _MIN_DOMINANT_ACTION_PROBABILITY
    assert q[1] > _MIN_DOMINANT_ACTION_PROBABILITY


def test_qre_differentiability():
    """Check qre differentiability."""

    def get_eq_prob(eg):
        # Payoffs depend on efficiency gap
        u_row = jnp.array([[1.0, 0.5], [eg, 0.0]], dtype=float)
        u_col = jnp.array([[1.0, eg], [0.5, 0.0]], dtype=float)
        p, _q, _res = qre_solver_jax(u_row, u_col, lam=2.0)
        return p[0]  # Probability of choosing first action

    grad_func = jax.grad(get_eq_prob)
    g = grad_func(0.5)

    # Should be a finite float
    assert not jnp.isnan(g)
    assert jnp.abs(g) > 0.0


def test_qre_reports_fixed_point_error_of_returned_profile() -> None:
    """One iteration returns an approximation with a measurable response error."""
    u_row = jnp.array([[4.0, 0.0], [2.0, 3.0]])
    u_col = jnp.array([[3.0, 1.0], [0.0, 4.0]])
    rationality = 2.0
    row, column, residual = qre_solver_jax(u_row, u_col, lam=rationality, max_iter=1)

    def logit(utility):
        odds = np.exp(rationality * (utility - np.max(utility)))
        return odds / odds.sum()

    row_response = logit(np.asarray(u_row @ column))
    column_response = logit(np.asarray(row @ u_col))
    fixed_point_error = max(abs(row_response - row)) + max(abs(column_response - column))
    np.testing.assert_allclose(residual, fixed_point_error, atol=1e-6, rtol=0)


def test_discrete_nash_oracle():
    # Coordination game
    """Check discrete nash oracle."""
    u_row = jnp.array([[2, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[2, 0], [0, 1]], dtype=float)

    p, q = discrete_nash_jax(u_row, u_col)

    # Should pick payoff dominant (2,2) -> action 0
    assert p[0] == 1.0
    assert q[0] == 1.0


def test_regret_min_basic():
    # Coordination game
    """Check regret min basic."""
    u_row = jnp.array([[2, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[2, 0], [0, 1]], dtype=float)

    p, q, _regret = regret_min_solver_jax(u_row, u_col)

    # Should approach one of the Nash equilibria
    # Note: Regret min can be sensitive, but should yield a valid profile
    total_regret = (jnp.max(u_row @ q) - p @ u_row @ q) + (jnp.max(p @ u_col) - p @ u_col @ q)
    assert total_regret < _MAX_TOTAL_REGRET


def test_qre_3player_basic():
    # Symmetric 3-player coordination game
    """Check qre 3player basic."""
    u = jnp.zeros((2, 2, 2))
    u = u.at[0, 0, 0].set(2.0)
    u = u.at[1, 1, 1].set(1.0)

    p1, p2, p3, res = jax.jit(lambda x: qre_3player_jax(x, x, x, lam=10.0))(u)

    # Should converge to (0,0,0) as it's payoff dominant
    assert p1[0] > _MIN_DOMINANT_ACTION_PROBABILITY
    assert p2[0] > _MIN_DOMINANT_ACTION_PROBABILITY
    assert p3[0] > _MIN_DOMINANT_ACTION_PROBABILITY
    assert res < _MAX_LOGIT_RESIDUAL


@pytest.mark.parametrize(("rationality", "iterations"), [(0.5, 0), (0.5, 1), (8.0, 100)])
def test_qre_3player_reports_fixed_point_error_of_returned_profile(
    rationality: float, iterations: int
) -> None:
    """Use the closed-form binary logit response for every seat in a coupled game."""
    a, b, c = np.indices((2, 2, 2))
    bias = 1.1
    utilities = [
        jnp.array(a * (bias - b - c)),
        jnp.array(b * (bias - a - c)),
        jnp.array(c * (bias - a - b)),
    ]

    @jax.jit
    def solve(u1, u2, u3):
        return qre_3player_jax(u1, u2, u3, lam=rationality, max_iter=iterations)

    p1, p2, p3, observed = solve(*utilities)
    first, second, third = (float(profile[1]) for profile in (p1, p2, p3))

    def probability(other_actions: float) -> float:
        return float(1.0 / (1.0 + np.exp(-rationality * (bias - other_actions))))

    expected = (
        abs(probability(second + third) - first)
        + abs(probability(first + third) - second)
        + abs(probability(first + second) - third)
    )
    np.testing.assert_allclose(observed, expected, atol=1e-6, rtol=0)
