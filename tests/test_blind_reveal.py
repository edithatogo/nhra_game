from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from nhra_gt.domain.validation import BlindReveal


@pytest.fixture
def mock_data():
    return pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023, 2024, 2025],
            "within4": [0.7, 0.65, 0.6, 0.55, 0.53, 0.52],
            "occupancy": [0.85, 0.88, 0.90, 0.92, 0.93, 0.94],
        }
    )


def test_blind_reveal_split(mock_data):
    """Verify data splitting for holdout."""
    revealer = BlindReveal(mock_data, holdout_years=[2024, 2025])

    assert len(revealer.train_df) == 4  # 2020-2023
    assert len(revealer.holdout_df) == 2  # 2024-2025
    assert 2024 not in revealer.train_df["year"].values


@patch("nhra_gt.domain.validation.run_hybrid")
def test_blind_reveal_run(mock_run, mock_data):
    """Verify execution of the blind run."""

    # Mock output for 2024-2025
    def side_effect(years, p, seed, n_mc):
        return pd.DataFrame(
            {"year": years, "within4_mean": [0.54, 0.53], "occupancy_mean": [0.92, 0.93]}
        ), None

    mock_run.side_effect = side_effect

    revealer = BlindReveal(mock_data, holdout_years=[2024, 2025])
    result = revealer.run_prediction()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].test_year == 2024
    assert result[0].predicted["within4"] == 0.54
    assert result[1].test_year == 2025
