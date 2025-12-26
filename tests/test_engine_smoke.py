from nhra_gt.engine import Params, run_hybrid


def test_v26_engine_smoke():
    p = Params()  # n_mc is passed to run_hybrid
    years = [2025, 2026]

    print("Running v26 smoke test...")
    agg, freq = run_hybrid(years, p, n_mc=5)

    print("Aggregation columns:", agg.columns.tolist())
    print("Years simulated:", agg["year"].unique().tolist())

    assert 2025 in agg["year"].values
    assert 2026 in agg["year"].values
    assert "polcap_mean" in agg.columns
    assert "equity_mean" in agg.columns

    print("Smoke test passed!")


if __name__ == "__main__":
    test_v26_engine_smoke()
