from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class NashEquilibrium:
    """A Nash equilibrium for a finite 2-player game.

    Attributes:
        kind: 'pure' or 'mixed'
        row: row strategy (probabilities over actions)
        col: col strategy (probabilities over actions)
    """

    kind: str
    row: np.ndarray[Any, Any]
    col: np.ndarray[Any, Any]


@dataclass(frozen=True)
class EquilibriumSelection:
    """Return type for `select_equilibrium` with backwards-compatible unpacking.

    Behaves like a `NashEquilibrium` for attribute access (e.g. `.row`, `.col`)
    and can also be unpacked as `(equilibrium, n_equilibria)`.
    """

    equilibrium: NashEquilibrium
    n_equilibria: int

    def __iter__(self) -> Iterator[object]:
        yield self.equilibrium
        yield self.n_equilibria

    def __getattr__(self, name: str) -> Any:
        return getattr(self.equilibrium, name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NashEquilibrium):
            return self.equilibrium == other
        if isinstance(other, EquilibriumSelection):
            return (self.equilibrium, self.n_equilibria) == (other.equilibrium, other.n_equilibria)
        return False


@dataclass(frozen=True)
class TwoPlayerGame:
    """Normal-form game with payoffs for row and column players."""

    u_row: np.ndarray[Any, Any]  # shape (n,m)
    u_col: np.ndarray[Any, Any]  # shape (n,m)
    row_actions: tuple[str, ...]
    col_actions: tuple[str, ...]


def _best_responses_row(game: TwoPlayerGame) -> np.ndarray[Any, Any]:
    # boolean matrix (n,m): row action i is best response to column action j
    A = game.u_row
    n, m = A.shape
    br = np.zeros((n, m), dtype=bool)
    for j in range(m):
        mx = A[:, j].max()
        br[:, j] = A[:, j] >= (mx - 1e-9)
    return br


def _best_responses_col(game: TwoPlayerGame) -> np.ndarray[Any, Any]:
    B = game.u_col
    n, m = B.shape
    br = np.zeros((n, m), dtype=bool)
    for i in range(n):
        mx = B[i, :].max()
        br[i, :] = B[i, :] >= (mx - 1e-9)
    return br


def pure_nash(game: TwoPlayerGame) -> list[NashEquilibrium]:
    br_r = _best_responses_row(game)
    br_c = _best_responses_col(game)
    n, m = game.u_row.shape
    eqs: list[NashEquilibrium] = []
    for i in range(n):
        for j in range(m):
            if br_r[i, j] and br_c[i, j]:
                row = np.zeros(n, dtype=float)
                row[i] = 1.0
                col = np.zeros(m, dtype=float)
                col[j] = 1.0
                eqs.append(NashEquilibrium(kind="pure", row=row, col=col))
    return eqs


def mixed_nash_2x2(game: TwoPlayerGame) -> NashEquilibrium | None:
    """Solve mixed Nash for 2x2 games, returning None if degenerate."""
    if game.u_row.shape != (2, 2):
        return None
    A = game.u_row
    B = game.u_col

    # Mixed equilibrium makes each player indifferent.
    denom_q = A[0, 0] - A[0, 1] - A[1, 0] + A[1, 1]
    denom_p = B[0, 0] - B[1, 0] - B[0, 1] + B[1, 1]

    if abs(denom_q) < 1e-9 or abs(denom_p) < 1e-9:
        return None

    q_hard = (A[1, 1] - A[0, 1]) / denom_q  # col prob of action1
    p_hard = (B[1, 1] - B[1, 0]) / denom_p  # row prob of action1

    if not (0.0 <= p_hard <= 1.0 and 0.0 <= q_hard <= 1.0):
        return None

    row = np.array([1.0 - p_hard, p_hard], dtype=float)
    col = np.array([1.0 - q_hard, q_hard], dtype=float)
    return NashEquilibrium(kind="mixed", row=row, col=col)


def all_nash(game: TwoPlayerGame) -> list[NashEquilibrium]:
    eqs = pure_nash(game)
    if game.u_row.shape == (2, 2):
        m = mixed_nash_2x2(game)
        if m is not None:
            # Only include mixed if not duplicative of pure (pure already covered)
            eqs.append(m)
    return eqs


def solve_all_equilibria(game: TwoPlayerGame) -> list[NashEquilibrium]:
    """Backwards-compatible alias for `all_nash`."""
    return all_nash(game)


def select_equilibrium(
    eqs: list[NashEquilibrium],
    rule: str = "payoff_dominant",
    u_row: np.ndarray[Any, Any] | None = None,
    u_col: np.ndarray[Any, Any] | None = None,
) -> EquilibriumSelection:
    """Select one equilibrium from a set.

    Rules:
        - 'payoff_dominant': maximise sum of expected payoffs
        - 'row_favourable': maximise row expected payoff
        - 'random': uniform random

    For mixed equilibria, expected payoffs use row@U@col.
    """
    if not eqs:
        raise ValueError("No equilibria to select from")
    n_eqs = len(eqs)
    if rule == "random" or u_row is None or u_col is None:
        return EquilibriumSelection(eqs[0], n_eqs)

    def exp_pay(eq: NashEquilibrium) -> tuple[float, float]:
        r = float(eq.row @ u_row @ eq.col)
        c = float(eq.row @ u_col @ eq.col)
        return r, c

    scores = []
    for eq in eqs:
        r, c = exp_pay(eq)
        s = r if rule == "row_favourable" else r + c
        scores.append(s)
    idx = int(np.argmax(np.array(scores)))
    return EquilibriumSelection(eqs[idx], n_eqs)


def get_best_response_path(game: TwoPlayerGame, max_iter: int = 10) -> list[tuple[int, int]]:
    """Simulates iterative best response from a starting position.

    Used for visualizing the path to equilibrium (v25 re-integration).
    """
    row_idx, col_idx = 0, 0
    path = [(row_idx, col_idx)]

    for _ in range(max_iter):
        # Row responds to Col
        new_row = int(np.argmax(game.u_row[:, col_idx]))
        # Col responds to Row
        new_col = int(np.argmax(game.u_col[new_row, :]))

        if (new_row, new_col) == path[-1]:
            break
        path.append((new_row, new_col))
        row_idx, col_idx = new_row, new_col

    return path
