from __future__ import annotations

import pandas as pd

from scripts.dashboard import prepare_share_drift_data


def test_prepare_share_drift_data():
    """Verify calculation of effective share drift and threshold breaches."""
    # Mock trajectory data
    # Scenario: Nominal share 45%, Efficiency Gap widens -> Effective share drops
    traj_data = pd.DataFrame(
        {
            "year": [2025, 2026, 2027],
            "cth_nominal_mean": [0.45, 0.45, 0.45],
            "cth_effective_mean": [0.42, 0.40, 0.38],  # Drops below 40% in 2027
            "effgap_mean": [0.07, 0.12, 0.18],
        }
    )

    threshold = 0.40
    df, breaches = prepare_share_drift_data(traj_data, threshold)

    assert "drift_gap" in df.columns  # (nominal - effective)
    assert len(breaches) == 1
    assert breaches[0]["year"] == 2027
    assert breaches[0]["value"] == 0.38
