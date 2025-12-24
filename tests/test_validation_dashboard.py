from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Add project root to path so 'scripts' can be imported
sys.path.append(str(Path(__file__).parent.parent))

from scripts.dashboard_v21 import prepare_ghost_overlay_data  # noqa: E402


def test_prepare_ghost_overlay_data():
    """Verify merging of historical and predicted data for Plotly."""
    historical = pd.DataFrame({"year": [2022, 2023], "within4": [0.60, 0.55]})
    # Simulated recursive results list
    recursive_results = [
        {"test_year": 2022, "predicted": {"within4": 0.62}, "actual": {"within4": 0.60}},
        {"test_year": 2023, "predicted": {"within4": 0.54}, "actual": {"within4": 0.55}},
    ]

    df = prepare_ghost_overlay_data(historical, recursive_results, metric="within4")

    # Should have columns: year, value, type
    assert "year" in df.columns
    assert "value" in df.columns
    assert "type" in df.columns

    # Check types
    assert "Historical" in df["type"].values
    assert "Backtest Prediction" in df["type"].values

    # Check values
    hist_2022 = df[(df["year"] == 2022) & (df["type"] == "Historical")]["value"].iloc[0]
    assert hist_2022 == 0.60

    pred_2022 = df[(df["year"] == 2022) & (df["type"] == "Backtest Prediction")]["value"].iloc[0]
    assert pred_2022 == 0.62
