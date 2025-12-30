from nhra_gt.engine import Params, run_hybrid


def test_new_engine_compatibility():
    p = Params()
    years = list(range(2025, 2031))
    agg, freq = run_hybrid(years, p, n_mc=10)

    print("Aggregated Columns:", agg.columns.tolist())
    assert "pressure_mean" in agg.columns
    assert "within4_mean" in agg.columns
    assert "effective_cth_share_mean" in agg.columns

    summary = agg.iloc[-1].to_dict()
    print("2030 Summary:", summary)

    assert summary["year"] == 2030


if __name__ == "__main__":
    test_new_engine_compatibility()
