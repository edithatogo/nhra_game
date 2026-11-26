"""Tests for sequential."""

from itertools import product

import numpy as np

from nhra_gt._paignia import commitment_choice
from nhra_gt.subgames import sequential
from nhra_gt.subgames.sequential import rubinstein_solution, stackelberg_solution


def test_rubinstein_symmetric_patience():
    # Both players have delta = 0.5
    # Share = 1 / (1 + 0.5) = 1 / 1.5 = 2/3 approx 0.666...
    # Compare the first-mover share with the closed-form Rubinstein solution.
    # (1-0.5) / (1-0.25) = 0.5 / 0.75 = 2/3.
    """Check rubinstein symmetric patience."""
    share_p1 = rubinstein_solution(pie_size=1.0, delta_1=0.5, delta_2=0.5)
    assert np.isclose(share_p1, 2 / 3)


def test_rubinstein_extreme_patience():
    # As delta -> 1, share -> 0.5
    """Check rubinstein extreme patience."""
    share_p1 = rubinstein_solution(1.0, 0.999, 0.999)
    assert np.isclose(share_p1, 0.5, atol=0.01)


def test_rubinstein_asymmetric():
    # P1 impatient (0.1), P2 patient (0.9)
    # Share = (1-0.9) / (1 - 0.09) = 0.1 / 0.91 = 0.109...
    # P1 gets very little despite moving first.
    """Check rubinstein asymmetric."""
    share_p1 = rubinstein_solution(1.0, 0.1, 0.9)
    assert np.isclose(share_p1, 0.1 / 0.91)


def test_stackelberg_basic():
    # Leader (Row) chooses row to maximize payoff GIVEN Col best response.
    # Matrix:
    #       C1(0)   C2(1)
    # R1(0)  2,1     0,0
    # R2(1)  1,0     1,2

    # Col Response:
    # If R1: Col chooses C1 (payoff 1 vs 0).
    # If R2: Col chooses C2 (payoff 2 vs 0).

    # Leader:
    # If R1 -> Col C1 -> Leader 2.
    # If R2 -> Col C2 -> Leader 1.
    # Leader chooses R1. Outcome (0, 0).
    """Check stackelberg basic."""
    u_row = np.array([[2, 0], [1, 1]])
    u_col = np.array([[1, 0], [0, 2]])

    idx_leader, idx_follower = stackelberg_solution(u_row, u_col)

    assert idx_leader == 0
    assert idx_follower == 0


def test_native_commitment_matches_first_index_enumeration():
    """Compare the installed provider with an independent finite oracle."""
    for entries in product((0.0, 1.0), repeat=8):
        leader = [list(entries[:2]), list(entries[2:4])]
        follower = [list(entries[4:6]), list(entries[6:])]
        replies = [max(range(2), key=utilities.__getitem__) for utilities in follower]
        row = max(range(2), key=lambda i: leader[i][replies[i]])
        assert commitment_choice(leader, follower) == (row, replies[row])


def test_stackelberg_uses_native_lower_index_ties_and_exact_order(mocker):
    """Check the receiving path on ties and close but distinct binary64 payoffs."""
    native = mocker.spy(sequential, "commitment_choice")
    leader = np.zeros((12, 2))
    follower = np.zeros_like(leader)
    leader[2, 0] = leader[10, 0] = 1.0
    leader[0, 1] = 9.0
    assert stackelberg_solution(leader, follower) == (2, 0)

    leader[10, 0] = np.nextafter(1.0, 2.0)
    assert stackelberg_solution(leader, follower) == (10, 0)

    leader = np.array([[0.0, 9.0], [4.0, 0.0]])
    follower = np.array([[0.0, 5e-13], [1.0, 0.0]])
    assert stackelberg_solution(leader, follower) == (0, 1)

    expected_native_calls = 3
    assert native.call_count == expected_native_calls


def test_stackelberg_preserves_integer_order_outside_binary64():
    """Keep the exact legacy ordering for integers above binary64 precision."""
    leader = np.array([[2**53], [2**53 + 1]], dtype=np.int64)
    follower = np.zeros_like(leader)
    assert stackelberg_solution(leader, follower) == (1, 0)
