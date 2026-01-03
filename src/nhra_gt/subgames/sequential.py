from __future__ import annotations
import numpy as np
from typing import Any


def rubinstein_solution(
    pie_size: float = 1.0, delta_1: float = 0.9, delta_2: float = 0.9, first_mover: int = 0
) -> float:
    """
    Calculates the Subgame Perfect Equilibrium share for the first mover
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
    # Prevent division by zero
    if delta_1 * delta_2 == 1.0:
        return pie_size * 0.5  # Limit case (perfect patience -> equal split)

    share = (1 - delta_2) / (1 - delta_1 * delta_2)
    return float(pie_size * share)


def stackelberg_solution(
    u_leader: np.ndarray[Any, Any], u_follower: np.ndarray[Any, Any]
) -> tuple[int, int]:
    """
    Solves for the Stackelberg Equilibrium where Row is Leader and Col is Follower.

    Args:
        u_leader: Payoff matrix for Leader (Row player).
        u_follower: Payoff matrix for Follower (Col player).

    Returns:
        Tuple (leader_action_idx, follower_action_idx).
    """
    n_rows, n_cols = u_leader.shape

    # Step 1: Determine Follower's Best Response for each Leader action
    follower_responses = []
    for r in range(n_rows):
        # Follower maximizes u_follower given row r
        # Using argmax (ties broken by first index)
        # TODO: Handle ties robustly? Standard is usually optimistic or pessimistic.
        # Here we assume standard argmax.
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
