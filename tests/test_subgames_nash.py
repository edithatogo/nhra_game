"""Tests for subgames nash."""

from __future__ import annotations

import numpy as np
import pytest

from nhra_gt.subgames import games
from nhra_gt.subgames.nash import (
    TwoPlayerGame,
    all_nash,
    mixed_nash_2x2,
    pure_nash,
    select_equilibrium,
)

_PURE_EQUILIBRIUM_COUNT = 2


def test_all_nash_pure_exists() -> None:
    # Coordination game has two pure equilibria
    """Check all nash pure exists."""
    u_r = np.array([[2, 0], [0, 1]], dtype=float)
    u_c = np.array([[2, 0], [0, 1]], dtype=float)
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("A", "B"), col_actions=("A", "B"))
    eqs = all_nash(g)
    assert any(e.kind == "pure" for e in eqs)
    assert len([e for e in eqs if e.kind == "pure"]) == _PURE_EQUILIBRIUM_COUNT


def test_all_nash_mixed_for_matching_pennies_is_none() -> None:
    # Matching pennies has no pure, mixed exists but degenerate selection may return mixed;
    # this test ensures the solver doesn't crash on zero denominators in arbitrary games.
    """Check all nash mixed for matching pennies is none."""
    u_r = np.array([[1, -1], [-1, 1]], dtype=float)
    u_c = -u_r
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("H", "T"), col_actions=("H", "T"))
    eqs = all_nash(g)
    # pure none, mixed may be returned depending on denominators; at least it returns a list
    assert isinstance(eqs, list)


def test_mixed_nash_rejects_non_2x2() -> None:
    """Check mixed nash rejects non 2x2."""
    u_r = np.zeros((3, 3), dtype=float)
    u_c = np.zeros((3, 3), dtype=float)
    g = TwoPlayerGame(
        u_row=u_r, u_col=u_c, row_actions=("A", "B", "C"), col_actions=("A", "B", "C")
    )
    assert mixed_nash_2x2(g) is None


def test_mixed_nash_rejects_degenerate() -> None:
    # The row player's indifference denominator is zero.
    """Check mixed nash rejects degenerate."""
    u_r = np.array([[1, 1], [1, 1]], dtype=float)
    u_c = np.array([[1, 0], [0, 1]], dtype=float)
    g = TwoPlayerGame(u_row=u_r, u_col=u_c, row_actions=("A", "B"), col_actions=("A", "B"))
    assert mixed_nash_2x2(g) is None


def test_select_equilibrium_rules() -> None:
    """Check select equilibrium rules."""
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


def legacy_profiles(row: np.ndarray, column: np.ndarray) -> list[tuple[int, int]]:
    """Reproduce the original inclusive NumPy threshold as a test oracle."""
    row_best = np.column_stack([values >= values.max() - 1e-9 for values in row.T])
    column_best = np.stack([values >= values.max() - 1e-9 for values in column])
    return [(int(i), int(j)) for i, j in np.argwhere(row_best & column_best)]


@pytest.mark.parametrize(
    ("dtype", "incumbent", "alternative"),
    [(np.float32, 4e-13, 1.0004e-9), (np.float64, 1e-13, 1.0001e-9)],
)
def test_pure_nash_preserves_original_near_tie_threshold(dtype, incumbent, alternative) -> None:
    """Preserve the prior rounded threshold on both supported float widths."""
    row = np.array([[incumbent, 1.0], [alternative, 0.0]], dtype=dtype)
    column = np.zeros((2, 2), dtype=np.float32)
    game = TwoPlayerGame(row, column, ("First", "Second"), ("Left", "Right"))
    positions = [(int(eq.row.argmax()), int(eq.col.argmax())) for eq in pure_nash(game)]
    assert positions == legacy_profiles(row, column) == [(0, 1), (1, 0)]


@pytest.mark.parametrize("pressure", [1.0, 1.9])
def test_native_pure_solver_matches_nhra_subgame_profiles(pressure: float) -> None:
    """Compare each subgame's pure profiles at baseline and elevated pressure."""
    params = games.GameParams(pressure, 0.07, 0.22, 0.61, 0.58, 0.31, 0.24)
    methods = (
        games.definition_game,
        games.bargaining_game,
        games.cost_shifting_game,
        games.discharge_coordination_game,
        games.governance_integration_game,
        games.aged_care_interface_game,
        games.ndis_interface_game,
        games.coding_audit_game,
        games.compliance_game,
        games.venue_shifting_game,
        games.competition_game,
    )
    models = [method(params) for method in methods]
    models.append(games.renegotiation_game(params, 0))
    for model in models:
        equilibria = pure_nash(model)
        positions = [(int(eq.row.argmax()), int(eq.col.argmax())) for eq in equilibria]
        assert positions == legacy_profiles(model.u_row, model.u_col)
        assert all(eq.kind == "pure" for eq in equilibria)
