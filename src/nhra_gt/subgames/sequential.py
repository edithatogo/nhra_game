"""Sequential and Alternating-Offer Bargaining Solvers.

Includes Rubinstein infinite-horizon bargaining and Stackelberg leader-follower
equilibrium solvers.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from nhra_gt._paignia import MAX_COMMITMENT_NODES, commitment_choice

_MATRIX_DIMENSIONS = 2
_BINARY64_BYTES = np.dtype(np.float64).itemsize
_MAX_EXACT_INTEGER = 2**53


def _native_payoffs(payoffs: np.ndarray[Any, Any]) -> bool:
    if payoffs.dtype.kind not in "biuf" or payoffs.dtype.itemsize > _BINARY64_BYTES:
        return False
    if payoffs.dtype.kind in "iu" and payoffs.dtype.itemsize == _BINARY64_BYTES:
        return (
            int(payoffs.min()) >= -_MAX_EXACT_INTEGER and int(payoffs.max()) <= _MAX_EXACT_INTEGER
        )
    return bool(np.isfinite(payoffs).all())


def rubinstein_solution(
    pie_size: float = 1.0, delta_1: float = 0.9, delta_2: float = 0.9, first_mover: int = 0
) -> float:
    """Calculates the Subgame Perfect Equilibrium share for the first mover.

    in an infinite-horizon alternating offers bargaining game.

    Formula: share = (1 - delta_2) / (1 - delta_1 * delta_2)

    Args:
        pie_size: Total value to split.
        delta_1: Discount factor for Player 1 (First Mover).
        delta_2: Discount factor for Player 2 (Second Mover).
        first_mover: 0 for Player 1, 1 for Player 2. (Not used in formula directly, assumes caller handles mapping).

    Returns:
        The share of the pie received by the First Mover.
    """
    # Callers provide discount factors in first-mover order.
    del first_mover
    # Prevent division by zero
    if delta_1 * delta_2 == 1.0:
        return pie_size * 0.5  # Historical perfect-patience convention.

    share = (1 - delta_2) / (1 - delta_1 * delta_2)
    return float(pie_size * share)


def stackelberg_solution(
    u_leader: np.ndarray[Any, Any], u_follower: np.ndarray[Any, Any]
) -> tuple[int, int]:
    """Solve the two-stage game with Row as leader and first-index ties.

    Use Paignia for bounded finite tables that preserve ordering in binary64.
    The legacy NumPy path handles inputs outside that provider profile.

    Args:
        u_leader: Payoff matrix for Leader (Row player).
        u_follower: Payoff matrix for Follower (Col player).

    Returns:
        Tuple (leader_action_idx, follower_action_idx).
    """
    if (
        u_leader.ndim == _MATRIX_DIMENSIONS
        and u_leader.shape == u_follower.shape
        and u_leader.size > 0
        and u_leader.size + u_leader.shape[0] + 1 <= MAX_COMMITMENT_NODES
        and _native_payoffs(u_leader)
        and _native_payoffs(u_follower)
    ):
        return commitment_choice(u_leader.tolist(), u_follower.tolist())

    n_rows, _n_cols = u_leader.shape

    # Step 1: Determine Follower's Best Response for each Leader action
    follower_responses = []
    for r in range(n_rows):
        # Follower maximizes u_follower given row r
        # NumPy keeps the first index at ties.
        best_c = int(np.argmax(u_follower[r, :]))
        follower_responses.append(best_c)

    # Step 2: Leader maximizes their payoff given Follower's response
    leader_outcomes = []
    for r in range(n_rows):
        c = follower_responses[r]
        leader_outcomes.append(u_leader[r, c])

    best_r = int(np.argmax(leader_outcomes))
    best_c = follower_responses[best_r]

    return best_r, best_c
