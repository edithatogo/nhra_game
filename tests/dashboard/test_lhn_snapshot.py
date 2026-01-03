import pandas as pd

from nhra_gt.engine import ParamsJax, run_hybrid


def test_lhn_snapshot_population():
    """Verify that run_hybrid populates the lhn_snapshot attribute with real data."""
    years = [2025, 2026]
    params = ParamsJax()

    # Run a small simulation
    traj, _ = run_hybrid(years, params, n_mc=10, seed=42)

    # Check attributes
    assert hasattr(traj, "attrs")
    assert "lhn_snapshot" in traj.attrs

    snapshot = traj.attrs["lhn_snapshot"]
    assert isinstance(snapshot, pd.DataFrame)

    # Check columns
    expected_cols = {"LHN_ID", "Pressure Index", "NWAU Capture (Relative)", "Type"}
    assert expected_cols.issubset(snapshot.columns)

    # Check shape
    # n_mc=10, n_lhns=5 (default)
    assert len(snapshot) == 10 * 5

    # Check that it's not all zeros
    assert (snapshot["Pressure Index"] > 0).all()
