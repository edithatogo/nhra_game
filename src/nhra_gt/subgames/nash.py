"""Nash Equilibrium Solvers for 2-Player Normal-Form Games.

This module provides standard game-theoretic solvers for computing Pure and Mixed
Nash Equilibria, as well as Stackelberg and Rubinstein bargaining solutions.
It includes equilibrium selection rules (payoff dominant, risk dominant).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import numpy as np

from nhra_gt._paignia import mixed_profile, pure_profiles
from nhra_gt.subgames.sequential import _native_payoffs, stackelberg_solution

_MATRIX_DIMENSIONS = 2
_INDIFFERENCE_TOLERANCE = 1e-9
_BINARY64_BYTES = np.dtype(np.float64).itemsize


@dataclass(frozen=True)
class NashEquilibrium:
    """A Nash equilibrium for a finite 2-player game.

    Represents a steady state where no player can benefit by changing their
    strategy while the other players keep theirs unchanged.
    """

    kind: str
    row: np.ndarray[Any, Any]
    col: np.ndarray[Any, Any]


@dataclass(frozen=True)
class EquilibriumSelection:
    """Result of an equilibrium selection process.

    Wraps a chosen equilibrium and the total count of equilibria found,
    providing a backwards-compatible interface for callers.
    """

    equilibrium: NashEquilibrium
    n_equilibria: int

    def __hash__(self) -> int:
        """Reject hashing of selections that contain mutable strategy arrays."""
        message = "Equilibrium selections contain mutable strategy arrays"
        raise TypeError(message)

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
    """Represents a 2-player normal-form game.

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
        mechanism: 'nash' or 'stackelberg'. The legacy 'rubinstein' name invokes Nash.
        rule: Equilibrium selection rule for Nash ('payoff_dominant', 'risk_dominant', 'random').
        discount_rate: Delta for Rubinstein/Sequential.
        first_mover: Index of the first mover (Stackelberg Leader).

    Returns:
        EquilibriumSelection wrapping the solution.
    """
    # Reserved for Rubinstein dispatch with explicit pie payoffs.
    del discount_rate
    if mechanism == "stackelberg":
        if first_mover == 0:  # Row Leader
            r, c = stackelberg_solution(game.u_row, game.u_col)
        else:  # Col Leader
            # Swap roles: Col is Leader (Row in stackelberg_solution terms)
            # Need to transpose payoffs?
            # If Col is Leader, they choose column j to max u_col[i, j] given Row response.
            # Easiest way: Transpose the game.
            c, r = stackelberg_solution(game.u_col.T, game.u_row.T)

        row_strat = np.zeros(len(game.row_actions))
        row_strat[r] = 1.0
        col_strat = np.zeros(len(game.col_actions))
        col_strat[c] = 1.0
        eq = NashEquilibrium("pure", row_strat, col_strat)
        return EquilibriumSelection(eq, 1)

    if mechanism == "rubinstein":
        # Historical dispatch predates a pie size and two discount factors.
        return solve_game(game, mechanism="nash", rule=rule)

    # Find all equilibria for the simultaneous game.
    eqs = all_nash(game)
    if not eqs:
        # Should not happen in finite games (mixed always exists)
        message = "No Nash Equilibrium found."
        raise ValueError(message)
    return select_equilibrium(eqs, rule=rule, u_row=game.u_row, u_col=game.u_col)


def pure_nash(game: TwoPlayerGame) -> list[NashEquilibrium]:
    """Find pure equilibria with Paignia using NHRA's inclusive tolerance."""
    row_payoffs, column_payoffs = game.u_row, game.u_col
    if row_payoffs.ndim != _MATRIX_DIMENSIONS or column_payoffs.ndim != _MATRIX_DIMENSIONS:
        msg = "Expected two-dimensional payoff tables"
        raise ValueError(msg)
    for payoffs in (row_payoffs, column_payoffs):
        if payoffs.dtype.kind not in "biuf" or payoffs.dtype.itemsize > _BINARY64_BYTES:
            msg = "Unsupported payoff precision for the Paignia adapter"
            raise ValueError(msg)
    positions = pure_profiles(
        row_payoffs.tolist(),
        column_payoffs.tolist(),
        [payoffs.dtype.type is np.float32 for payoffs in (row_payoffs, column_payoffs)],
    )
    height, width = row_payoffs.shape
    equilibria = []
    for i, j in positions:
        row = np.zeros(height, dtype=float)
        row[i] = 1.0
        column = np.zeros(width, dtype=float)
        column[j] = 1.0
        equilibria.append(NashEquilibrium(kind="pure", row=row, col=column))
    return equilibria


def _absolute_indifference_denominator(payoffs: np.ndarray[Any, Any]) -> float:
    a, b, c, d = payoffs.ravel()
    if payoffs.dtype.kind in "biu":
        return float(abs(int(a) - int(b) - int(c) + int(d)))
    return float(abs(a - b - c + d))


def mixed_nash_2x2(game: TwoPlayerGame) -> NashEquilibrium | None:
    """Find the Paignia-verified full-support Nash witness for a 2x2 game.

    Preserve the NHRA indifference cutoff and use the provider's deviation
    checks. Return None when this search yields no verified interior witness.
    """
    if game.u_row.shape != (2, 2):
        return None
    row, column = game.u_row, game.u_col
    if column.shape != row.shape or not (_native_payoffs(row) and _native_payoffs(column)):
        msg = "Expected matching finite 2x2 payoffs representable in binary64"
        raise ValueError(msg)

    # Retain the existing admission cutoff before the bounded support search.
    row_denominator = _absolute_indifference_denominator(row)
    column_denominator = _absolute_indifference_denominator(column.T)

    if min(row_denominator, column_denominator) < _INDIFFERENCE_TOLERANCE:
        return None

    witness = mixed_profile(row.tolist(), column.tolist())
    if witness is None:
        return None
    row_strategy, column_strategy = witness
    return NashEquilibrium("mixed", np.array(row_strategy), np.array(column_strategy))


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
        message = "No equilibria to select from"
        raise ValueError(message)
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
