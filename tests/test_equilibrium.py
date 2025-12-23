from __future__ import annotations

from nhra_game_theory.equilibrium import bargaining_from_state, logistic, mixed_strategy_logit


def test_mixed_strategy_logit_bounds() -> None:
    p = mixed_strategy_logit(u_hard=1.0, u_soft=0.0, k=4.0)
    assert 0.0 <= p <= 1.0


def test_bargaining_from_state_monotone() -> None:
    # Higher pressure and higher effgap should increase "hard" probability.
    low = bargaining_from_state(pressure=0.8, effgap=0.1, k=4.0).p_hard
    high = bargaining_from_state(pressure=1.4, effgap=0.6, k=4.0).p_hard
    assert high > low



def test_logistic_negative_branch() -> None:
    v = logistic(-1.0)
    assert 0.0 < v < 0.5
