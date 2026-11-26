"""Tests for engine smoke."""

from nhra_gt.engine import Params, run_hybrid

_FIRST_YEAR = 2025
_SECOND_YEAR = 2026


def test_engine_smoke():
    """Check engine smoke."""
    p = Params()  # n_mc is passed to run_hybrid
    years = [2025, 2026]

    print("Running engine smoke test...")
    agg, _freq = run_hybrid(years, p, n_mc=5)

    print("Aggregation columns:", agg.columns.tolist())
    print("Years simulated:", agg["year"].unique().tolist())

    assert _FIRST_YEAR in agg["year"].values
    assert _SECOND_YEAR in agg["year"].values
    assert "polcap_mean" in agg.columns
    assert "equity_mean" in agg.columns

    print("Smoke test passed!")


if __name__ == "__main__":
    test_engine_smoke()
