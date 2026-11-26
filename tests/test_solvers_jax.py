"""Tests for solvers JAX."""

from __future__ import annotations

from math import isnan

import jax
import jax.numpy as jnp
import numpy as np
import pytest
from jax import Array

from nhra_gt.solvers_jax import (
    discrete_nash_jax,
    qre_3player_jax,
    qre_solver_jax,
    regret_min_solver_jax,
    solve_three_player_qre,
)

_MIN_DOMINANT_ACTION_PROBABILITY = 0.9
_MAX_TOTAL_REGRET = 0.1
_MAX_LOGIT_RESIDUAL = 0.1
_COUPLED_QRE_TOLERANCE = 1e-10
_DEFAULT_QRE_TOLERANCE = 1e-6


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


def _unique_coupled_payoffs() -> tuple[Array, Array, Array]:
    a, b, c = np.indices((2, 2, 2))
    return (
        jnp.asarray(a * (0.35 - b)),
        jnp.asarray(b * (c - 0.45)),
        jnp.asarray(c * (a - 0.65)),
    )


@pytest.mark.parametrize(
    ("iterations", "expected_error"), [(99, 0.8975736051769919), (100, 0.9462680213183089)]
)
def test_three_player_qre_caller_requires_convergence(
    iterations: int, expected_error: float
) -> None:
    """Replay the independent binary64 controls with the original error bound."""
    with jax.enable_x64():
        payoffs = _unique_coupled_payoffs()
        accepted = solve_three_player_qre(
            payoffs, lam=0.5, max_iter=iterations, tol=_COUPLED_QRE_TOLERANCE
        )
        p1, p2, p3, converged_error = qre_3player_jax(*payoffs, lam=0.5, max_iter=iterations)
        rejected = solve_three_player_qre(
            payoffs, lam=8.0, max_iter=iterations, tol=_COUPLED_QRE_TOLERANCE
        )
        *_, nonconverged_error = qre_3player_jax(*payoffs, lam=8.0, max_iter=iterations)

    assert accepted.status == "converged"
    assert accepted.residual == float(converged_error)
    assert 0.0 <= accepted.residual <= _COUPLED_QRE_TOLERANCE
    assert accepted.strategies is not None
    np.testing.assert_array_equal(accepted.strategies, (p1, p2, p3))
    np.testing.assert_allclose(
        [float(strategy[1]) for strategy in accepted.strategies],
        (0.4808084462248103, 0.5036078948003780, 0.4788636593639917),
        atol=_COUPLED_QRE_TOLERANCE,
        rtol=0,
    )

    assert rejected.status == "nonconverged"
    assert rejected.residual == float(nonconverged_error)
    assert rejected.residual == pytest.approx(expected_error, abs=1e-12, rel=0)
    assert rejected.strategies is None


def test_three_player_qre_caller_applies_tolerance_inclusively() -> None:
    """Use the same finite-budget error for the default, stricter and exact bounds."""
    with jax.enable_x64():
        payoffs = _unique_coupled_payoffs()
        *_, residual = qre_3player_jax(*payoffs, lam=0.5, max_iter=6)
        error = float(residual)
        assert _COUPLED_QRE_TOLERANCE < error <= _DEFAULT_QRE_TOLERANCE
        assert solve_three_player_qre(payoffs, lam=0.5, max_iter=6).status == "converged"
        assert solve_three_player_qre(payoffs, lam=0.5, max_iter=6, tol=error).status == "converged"
        strict = solve_three_player_qre(payoffs, lam=0.5, max_iter=6, tol=_COUPLED_QRE_TOLERANCE)
    assert strict.status == "nonconverged"
    assert strict.residual == error
    assert strict.strategies is None


def test_three_player_qre_caller_preserves_nonfinite_error() -> None:
    """A nonfinite diagnostic cannot qualify the returned profile."""
    first, second, third = _unique_coupled_payoffs()
    payoffs = (first.at[0, 0, 0].set(jnp.nan), second, third)
    *_, raw_error = qre_3player_jax(*payoffs, max_iter=0)
    result = solve_three_player_qre(payoffs, max_iter=0)
    assert isnan(float(raw_error))
    assert isnan(result.residual)
    assert result.status == "nonconverged"
    assert result.strategies is None


@pytest.mark.parametrize("tolerance", [-1.0, float("inf"), float("nan")])
def test_three_player_qre_caller_rejects_invalid_tolerance(tolerance: float) -> None:
    """An invalid bound cannot admit an arbitrary profile."""
    with pytest.raises(ValueError, match="QRE tolerance must be finite and nonnegative"):
        solve_three_player_qre(_unique_coupled_payoffs(), tol=tolerance)
