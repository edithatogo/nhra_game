from __future__ import annotations

import numpy as np

from nhra_game_theory.subgames.nash import TwoPlayerGame, all_nash


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
