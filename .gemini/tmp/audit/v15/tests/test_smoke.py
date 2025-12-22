from nhra_game_theory.v8 import Params, run_hybrid, scenario_summary, one_way_sensitivity, probabilistic_sensitivity


def test_run_hybrid_smoke():
    years = [2025, 2026, 2027]
    agg, freq = run_hybrid(years, Params(), seed=1, n_mc=30)
    assert not agg.empty
    assert set(["year", "pressure_mean", "within4_mean"]).issubset(agg.columns)
    assert not freq.empty


def test_scenario_summary_smoke():
    years = [2025, 2026, 2027]
    p = Params()
    scen = scenario_summary(years, p, {"baseline": [], "pooled": ["pooled"]}, seed=1, n_mc=20)
    assert set(["scenario", "rr_mean", "pressure_mean"]).issubset(scen.columns)
    assert len(scen) == 2


def test_one_way_sensitivity_smoke():
    years = [2025, 2026, 2027]
    p = Params()
    out = one_way_sensitivity(years, p, {"noise_sd": [0.01, 0.03]}, seed=1, n_mc=15)
    assert not out.empty
    assert set(["param", "value", "rr_end"]).issubset(out.columns)


def test_psa_smoke():
    years = [2025, 2026, 2027]
    p = Params()
    psa = probabilistic_sensitivity(years, p, ["pooled"], seed=1, n_param=10, n_mc=10)
    assert len(psa) == 10
