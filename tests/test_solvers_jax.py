from __future__ import annotations

import jax
import jax.numpy as jnp

from nhra_gt.solvers_jax import (
    discrete_nash_jax,
    qre_3player_jax,
    qre_solver_jax,
    regret_min_solver_jax,
)


def test_qre_solver_basic():
    # Prisoners' Dilemma
    u_row = jnp.array([[-1, -10], [0, -5]], dtype=float)
    u_col = jnp.array([[-1, 0], [-10, -5]], dtype=float)

    # At high lambda, should converge toward Nash (Defect, Defect) -> ([0, 1], [0, 1])
    p, q, res = qre_solver_jax(u_row, u_col, lam=10.0)

    assert p[1] > 0.9
    assert q[1] > 0.9


def test_qre_differentiability():
    def get_eq_prob(eg):
        # Payoffs depend on efficiency gap
        u_row = jnp.array([[1.0, 0.5], [eg, 0.0]], dtype=float)
        u_col = jnp.array([[1.0, eg], [0.5, 0.0]], dtype=float)
        p, q, res = qre_solver_jax(u_row, u_col, lam=2.0)
        return p[0]  # Probability of choosing first action

    grad_func = jax.grad(get_eq_prob)
    g = grad_func(0.5)

    # Should be a finite float
    assert not jnp.isnan(g)
    assert jnp.abs(g) > 0.0


def test_discrete_nash_oracle():
    # Coordination game
    u_row = jnp.array([[2, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[2, 0], [0, 1]], dtype=float)

    p, q = discrete_nash_jax(u_row, u_col)

    # Should pick payoff dominant (2,2) -> action 0
    assert p[0] == 1.0
    assert q[0] == 1.0


def test_regret_min_basic():
    # Coordination game
    u_row = jnp.array([[2, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[2, 0], [0, 1]], dtype=float)

    p, q, regret = regret_min_solver_jax(u_row, u_col)

    # Should approach one of the Nash equilibria
    # Note: Regret min can be sensitive, but should yield a valid profile
    total_regret = (jnp.max(u_row @ q) - p @ u_row @ q) + (jnp.max(p @ u_col) - p @ u_col @ q)
    assert total_regret < 0.1


def test_qre_3player_basic():
    # Symmetric 3-player coordination game
    u = jnp.zeros((2, 2, 2))
    u = u.at[0, 0, 0].set(2.0)
    u = u.at[1, 1, 1].set(1.0)

    p1, p2, p3, res = jax.jit(lambda x: qre_3player_jax(x, x, x, lam=10.0))(u)

    # Should converge to (0,0,0) as it's payoff dominant
    assert p1[0] > 0.9
    assert p2[0] > 0.9
    assert p3[0] > 0.9
    assert res < 0.1
