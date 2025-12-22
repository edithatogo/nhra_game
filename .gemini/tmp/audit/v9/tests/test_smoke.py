from nhra_game_theory.v8 import Params, run_hybrid

def test_run_hybrid_smoke():
    years = [2025, 2026, 2027]
    agg, freq = run_hybrid(years, Params(), seed=1, n_mc=30)
    assert not agg.empty
    assert set(["year", "pressure_mean", "within4_mean"]).issubset(agg.columns)
    assert not freq.empty
