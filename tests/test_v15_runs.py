from __future__ import annotations

from nhra_game_theory.v8 import Params, run_hybrid


def test_run_hybrid_with_equilibria() -> None:
    years = list(range(2025, 2028))
    p = Params(use_stage_game_equilibria=True)
    df, strat = run_hybrid(years=years, p=p, seed=123, n_mc=30)
    assert not df.empty
    assert not strat.empty
