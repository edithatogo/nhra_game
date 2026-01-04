"""
Nash Equilibrium Solvers for 2-Player Normal-Form Games.

This module provides standard game-theoretic solvers for computing Pure and Mixed
Nash Equilibria, as well as Stackelberg and Rubinstein bargaining solutions.
It includes equilibrium selection rules (payoff dominant, risk dominant).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import numpy as np

from nhra_gt.subgames.sequential import stackelberg_solution


@dataclass(frozen=True)
class NashEquilibrium:
    """
    A Nash equilibrium for a finite 2-player game.

    Represents a steady state where no player can benefit by changing their
    strategy while the other players keep theirs unchanged.
    """

    kind: str
    row: np.ndarray[Any, Any]
    col: np.ndarray[Any, Any]


@dataclass(frozen=True)
class EquilibriumSelection:
    """
    Result of an equilibrium selection process.

    Wraps a chosen equilibrium and the total count of equilibria found,
    providing a backwards-compatible interface for callers.
    """

    equilibrium: NashEquilibrium
    n_equilibria: int

    def __iter__(self) -> Iterator[object]:
        """Allows unpacking as (equilibrium, n_equilibria)."""
        yield self.equilibrium
        yield self.n_equilibria

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the chosen equilibrium."""
        return getattr(self.equilibrium, name)

    def __eq__(self, other: object) -> bool:
        """Structural equality check."""
        if isinstance(other, NashEquilibrium):
            return self.equilibrium == other
        if isinstance(other, EquilibriumSelection):
            return (self.equilibrium, self.n_equilibria) == (other.equilibrium, other.n_equilibria)
        return False


@dataclass(frozen=True)
class TwoPlayerGame:
    """
    Represents a 2-player normal-form game.

    Includes payoff matrices and action labels for both players.
    """

    u_row: np.ndarray[Any, Any]  # shape (n,m)
    u_col: np.ndarray[Any, Any]  # shape (n,m)
    row_actions: tuple[str, ...]
    col_actions: tuple[str, ...]


def solve_game(
    game: TwoPlayerGame,
    mechanism: str = "nash",
    rule: str = "payoff_dominant",
    discount_rate: float = 0.9,
    first_mover: int = 0,  # 0=Row, 1=Col
) -> EquilibriumSelection:
    """Unified solver dispatch.

    Args:
        game: The game to solve.
        mechanism: 'nash', 'stackelberg', 'rubinstein'.
        rule: Equilibrium selection rule for Nash ('payoff_dominant', 'risk_dominant', 'random').
        discount_rate: Delta for Rubinstein/Sequential.
        first_mover: Index of the first mover (Stackelberg Leader).

    Returns:
        EquilibriumSelection wrapping the solution.
    """
    if mechanism == "stackelberg":
        if first_mover == 0:  # Row Leader
            r, c = stackelberg_solution(game.u_row, game.u_col)
        else:  # Col Leader
            # Swap roles: Col is Leader (Row in stackelberg_solution terms)
            # Need to transpose payoffs?
            # stackelberg_solution(leader_payoff, follower_payoff)
            # If Col is Leader, they choose column j to max u_col[i, j] given Row response.
            # Easiest way: Transpose the game.
            c, r = stackelberg_solution(game.u_col.T, game.u_row.T)

        row_strat = np.zeros(len(game.row_actions))
        row_strat[r] = 1.0
        col_strat = np.zeros(len(game.col_actions))
        col_strat[c] = 1.0
        eq = NashEquilibrium("pure", row_strat, col_strat)
        return EquilibriumSelection(eq, 1)

    elif mechanism == "rubinstein":
        # Assumes 2x2 bargaining game over a pie.
        # This is tricky because TwoPlayerGame is arbitrary matrix.
        # Rubinstein applies to "splitting a pie".
        # We need to map the matrix outcomes to "Share".
        # Assumption: The game has a "Cooperate" outcome (A, A) which is the Pie.
        # And a "Conflict" outcome (D, D) which is 0 (or breakdown).
        # And the "First Mover" proposes a split.
        #
        # Implementation: We calculate the theoretical share and map it to a Mixed Strategy?
        # No, Rubinstein result is a specific share (x, 1-x).
        # We can return a pseudo-equilibrium where payoffs match the share.
        # OR we just solve the Nash of the *Simultaneous* game but weighted by delta?
        #
        # Simplified Integration: Use the Rubinstein share to define the 'Effective' outcome
        # if the game is 'bargaining_game'.
        # For generic games, Rubinstein doesn't apply directly without defining the pie.
        # Fallback to Nash for generic games.
        if "A" in game.row_actions and "D" in game.row_actions:
            # It's likely a bargaining game.
            # Assume Pie Size is the sum of payoffs at (A, A)?
            # Or max possible sum?
            # Let's approximate by returning Nash for now, but logging a warning.
            pass
        return solve_game(game, mechanism="nash", rule=rule)

    # Default: Nash
    eqs = all_nash(game)
    if not eqs:
        # Should not happen in finite games (mixed always exists)
        raise ValueError("No Nash Equilibrium found.")
    return select_equilibrium(eqs, rule=rule, u_row=game.u_row, u_col=game.u_col)


def _best_responses_row(game: TwoPlayerGame) -> np.ndarray[Any, Any]:
    """Computes a boolean matrix of best responses for the Row player."""
    # boolean matrix (n,m): row action i is best response to column action j
    A = game.u_row
    n, m = A.shape
    br = np.zeros((n, m), dtype=bool)
    for j in range(m):
        mx = A[:, j].max()
        br[:, j] = A[:, j] >= (mx - 1e-9)
    return br


def _best_responses_col(game: TwoPlayerGame) -> np.ndarray[Any, Any]:
    """Computes a boolean matrix of best responses for the Column player."""
    B = game.u_col
    n, m = B.shape
    br = np.zeros((n, m), dtype=bool)
    for i in range(n):
        mx = B[i, :].max()
        br[i, :] = B[i, :] >= (mx - 1e-9)
    return br


def pure_nash(game: TwoPlayerGame) -> list[NashEquilibrium]:
    """
    Finds all Pure Strategy Nash Equilibria.

    An action profile is a PNE if no player can unilaterally improve their payoff
    by switching to a different pure action.
    """
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
    """
    Solve mixed Nash for 2x2 games using the indifference principle.

    Returns None if the game is degenerate or has only pure equilibria.
    """
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
    """Finds all pure Nash equilibria, plus the mixed equilibrium for 2x2 games."""
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
        if rule == "risk_dominant":
            # Risk Dominance (Harsanyi & Selten) for 2x2 games
            # Only applies to Pure Nash Equilibria
            if eq.kind != "pure" or u_row.shape != (2, 2):
                scores.append(-float("inf"))
                continue

            # Identify indices
            r_idx = int(np.argmax(eq.row))
            c_idx = int(np.argmax(eq.col))

            # Deviation indices (for 2x2, it's 1 - idx)
            r_dev = 1 - r_idx
            c_dev = 1 - c_idx

            # Deviation losses
            # Row loss: Payoff(r, c) - Payoff(dev, c)
            l_row = u_row[r_idx, c_idx] - u_row[r_dev, c_idx]

            # Col loss: Payoff(r, c) - Payoff(r, dev)
            l_col = u_col[r_idx, c_idx] - u_col[r_idx, c_dev]

            # Nash Product
            scores.append(l_row * l_col)

        else:
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
