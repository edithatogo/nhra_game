import numpy as np

from nhra_gt.subgames.sequential import rubinstein_solution, stackelberg_solution


def test_rubinstein_symmetric_patience():
    # Both players have delta = 0.5
    # Share = 1 / (1 + 0.5) = 1 / 1.5 = 2/3 approx 0.666...
    # Formula: (1 - d2) / (1 - d1*d2)
    # (1-0.5) / (1-0.25) = 0.5 / 0.75 = 2/3.

    share_p1 = rubinstein_solution(pie_size=1.0, delta_1=0.5, delta_2=0.5)
    assert np.isclose(share_p1, 2 / 3)


def test_rubinstein_extreme_patience():
    # As delta -> 1, share -> 0.5
    share_p1 = rubinstein_solution(1.0, 0.999, 0.999)
    assert np.isclose(share_p1, 0.5, atol=0.01)


def test_rubinstein_asymmetric():
    # P1 impatient (0.1), P2 patient (0.9)
    # Share = (1-0.9) / (1 - 0.09) = 0.1 / 0.91 = 0.109...
    # P1 gets very little despite moving first.
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

    u_row = np.array([[2, 0], [1, 1]])
    u_col = np.array([[1, 0], [0, 2]])

    idx_leader, idx_follower = stackelberg_solution(u_row, u_col)

    assert idx_leader == 0
    assert idx_follower == 0
