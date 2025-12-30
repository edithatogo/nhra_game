from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from nhra_gt.solvers_jax import qre_solver_jax, regret_min_solver_jax
from nhra_gt.subgames.nash import TwoPlayerGame, all_nash, select_equilibrium


def test_qre_telemetry_jax():
    """Verify QRE solver returns residual."""
    u_row = jnp.array([[1, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[1, 0], [0, 1]], dtype=float)

    p, q, res = qre_solver_jax(u_row, u_col, max_iter=5)

    assert res > 0
    assert not jnp.isnan(res)


def test_regret_telemetry_jax():
    """Verify regret min solver returns final regret."""
    u_row = jnp.array([[1, 0], [0, 1]], dtype=float)
    u_col = jnp.array([[1, 0], [0, 1]], dtype=float)

    p, q, regret = regret_min_solver_jax(u_row, u_col, max_iter=5)

    assert regret > 0
    assert not jnp.isnan(regret)


def test_analytic_telemetry_legacy():
    """Verify select_equilibrium returns n_equilibria."""
    u_row = np.array([[2, 0], [0, 1]], dtype=float)
    u_col = np.array([[2, 0], [0, 1]], dtype=float)

    game = TwoPlayerGame(u_row, u_col, ("A0", "A1"), ("B0", "B1"))
    eqs = all_nash(game)

    # Coordination game has 3 Nash Equilibria (2 pure, 1 mixed)
    sel, n_eqs = select_equilibrium(eqs, u_row=u_row, u_col=u_col)

    assert n_eqs == 3
    assert sel.kind == "pure"
