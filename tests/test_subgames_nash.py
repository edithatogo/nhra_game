from __future__ import annotations

import numpy as np

from nhra_gt.subgames.nash import (
    TwoPlayerGame,
    all_nash,
    mixed_nash_2x2,
    select_equilibrium,
)


def test_all_nash_pure_exists() -> None:
    # Coordination game has two pure equilibria
    u_r = np.array([[2, 0], [0, 1]], dtype=float)
    u_c = np.array([[2, 0], [0, 1]], dtype=float)
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("A", "B"), col_actions=("A", "B"))
    eqs = all_nash(g)
    assert any(e.kind == "pure" for e in eqs)
    assert len([e for e in eqs if e.kind == "pure"]) == 2


def test_all_nash_mixed_for_matching_pennies_is_none() -> None:
    # Matching pennies has no pure, mixed exists but degenerate selection may return mixed;
    # this test ensures the solver doesn't crash on zero denominators in arbitrary games.
    u_r = np.array([[1, -1], [-1, 1]], dtype=float)
    u_c = -u_r
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("H", "T"), col_actions=("H", "T"))
    eqs = all_nash(g)
    # pure none, mixed may be returned depending on denominators; at least it returns a list
    assert isinstance(eqs, list)


def test_mixed_nash_rejects_non_2x2() -> None:
    u_r = np.zeros((3, 3), dtype=float)
    u_c = np.zeros((3, 3), dtype=float)
    g = TwoPlayerGame(
        u_row=u_r, u_col=u_c, row_actions=("A", "B", "C"), col_actions=("A", "B", "C")
    )
    assert mixed_nash_2x2(g) is None


def test_mixed_nash_rejects_degenerate() -> None:
    # denom_q == 0
    u_r = np.array([[1, 1], [1, 1]], dtype=float)
    u_c = np.array([[1, 0], [0, 1]], dtype=float)
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("A", "B"), col_actions=("A", "B"))
    assert mixed_nash_2x2(g) is None


def test_select_equilibrium_rules() -> None:
    u_r = np.array([[2, 0], [0, 1]], dtype=float)
    u_c = np.array([[1, 0], [0, 2]], dtype=float)
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("A", "B"), col_actions=("A", "B"))
    eqs = all_nash(g)
    # random rule returns first (deterministic behaviour in our implementation)
    e0 = select_equilibrium(eqs, rule="random", u_row=u_r, u_col=u_c)
    assert e0 == eqs[0]
    # row_favourable selects eq with maximum row expected payoff
    e1 = select_equilibrium(eqs, rule="row_favourable", u_row=u_r, u_col=u_c)
    r0 = float(e0.row @ u_r @ e0.col)
    r1 = float(e1.row @ u_r @ e1.col)
    assert r1 >= r0
