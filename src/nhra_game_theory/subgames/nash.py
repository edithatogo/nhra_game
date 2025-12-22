from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

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
    row: np.ndarray
    col: np.ndarray


@dataclass(frozen=True)
class TwoPlayerGame:
    """Normal-form game with payoffs for row and column players."""
    u_row: np.ndarray  # shape (n,m)
    u_col: np.ndarray  # shape (n,m)
    row_actions: Tuple[str, ...]
    col_actions: Tuple[str, ...]


def _best_responses_row(game: TwoPlayerGame) -> np.ndarray:
    # boolean matrix (n,m): row action i is best response to column action j
    A = game.u_row
    n, m = A.shape
    br = np.zeros((n, m), dtype=bool)
    for j in range(m):
        mx = A[:, j].max()
        br[:, j] = np.isclose(A[:, j], mx)
    return br


def _best_responses_col(game: TwoPlayerGame) -> np.ndarray:
    B = game.u_col
    n, m = B.shape
    br = np.zeros((n, m), dtype=bool)
    for i in range(n):
        mx = B[i, :].max()
        br[i, :] = np.isclose(B[i, :], mx)
    return br


def pure_nash(game: TwoPlayerGame) -> List[NashEquilibrium]:
    br_r = _best_responses_row(game)
    br_c = _best_responses_col(game)
    n, m = game.u_row.shape
    eqs: List[NashEquilibrium] = []
    for i in range(n):
        for j in range(m):
            if br_r[i, j] and br_c[i, j]:
                row = np.zeros(n, dtype=float); row[i] = 1.0
                col = np.zeros(m, dtype=float); col[j] = 1.0
                eqs.append(NashEquilibrium(kind="pure", row=row, col=col))
    return eqs


def mixed_nash_2x2(game: TwoPlayerGame) -> Optional[NashEquilibrium]:
    """Solve mixed Nash for 2x2 games, returning None if degenerate."""
    if game.u_row.shape != (2, 2):
        return None
    A = game.u_row
    B = game.u_col

    # Mixed equilibrium makes each player indifferent.
    denom_q = (A[0, 0] - A[0, 1] - A[1, 0] + A[1, 1])
    denom_p = (B[0, 0] - B[1, 0] - B[0, 1] + B[1, 1])

    if np.isclose(denom_q, 0.0) or np.isclose(denom_p, 0.0):
        return None

    q_hard = (A[1, 1] - A[0, 1]) / denom_q  # col prob of action1
    p_hard = (B[1, 1] - B[1, 0]) / denom_p  # row prob of action1

    if not (0.0 <= p_hard <= 1.0 and 0.0 <= q_hard <= 1.0):
        return None

    row = np.array([1.0 - p_hard, p_hard], dtype=float)
    col = np.array([1.0 - q_hard, q_hard], dtype=float)
    return NashEquilibrium(kind="mixed", row=row, col=col)


def all_nash(game: TwoPlayerGame) -> List[NashEquilibrium]:
    eqs = pure_nash(game)
    if game.u_row.shape == (2, 2):
        m = mixed_nash_2x2(game)
        if m is not None:
            # Only include mixed if not duplicative of pure (pure already covered)
            eqs.append(m)
    return eqs


def select_equilibrium(eqs: List[NashEquilibrium], rule: str = "payoff_dominant",
                       u_row: np.ndarray | None = None, u_col: np.ndarray | None = None) -> NashEquilibrium:
    """Select one equilibrium from a set.

    Rules:
        - 'payoff_dominant': maximise sum of expected payoffs
        - 'row_favourable': maximise row expected payoff
        - 'random': uniform random

    For mixed equilibria, expected payoffs use row@U@col.
    """
    if not eqs:
        raise ValueError("No equilibria to select from")
    if rule == "random" or u_row is None or u_col is None:
        return eqs[0]
    def exp_pay(eq: NashEquilibrium) -> Tuple[float, float]:
        r = float(eq.row @ u_row @ eq.col)
        c = float(eq.row @ u_col @ eq.col)
        return r, c
    scores = []
    for eq in eqs:
        r, c = exp_pay(eq)
        if rule == "row_favourable":
            s = r
        else:
            s = r + c
        scores.append(s)
    idx = int(np.argmax(np.array(scores)))
    return eqs[idx]
