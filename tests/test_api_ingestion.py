"""Tests for API ingestion."""

from __future__ import annotations

import pandas as pd
from scripts.data.ingest_aihw_api import process_api_data

_OBSERVATION_COUNT = 2
_LATER_YEAR = 2024
_NORMALIZED_LATER = 0.53
_EARLIER_YEAR = 2023
_NORMALIZED_EARLIER = 0.55


def test_process_api_data():
    """Verify that raw API data is correctly merged with dataset info."""
    raw_data = pd.DataFrame(
        [
            {
                "data_set_id": 1,
                "value": 53.0,
                "reporting_unit_summary": {"reporting_unit_code": "NAT"},
                "peer_group_summary": None,
                "reported_measure_code": "MYH-RM0015",
            },
            {
                "data_set_id": 2,
                "value": 55.0,
                "reporting_unit_summary": {"reporting_unit_code": "NAT"},
                "peer_group_summary": None,
                "reported_measure_code": "MYH-RM0015",
            },
        ]
    )

    datasets = [
        {"data_set_id": 1, "reporting_end_date": "2024-06-30"},
        {"data_set_id": 2, "reporting_end_date": "2023-06-30"},
    ]

    df = process_api_data(raw_data, datasets)

    assert len(df) == _OBSERVATION_COUNT
    assert "Year" in df.columns
    assert (
        df.loc[df["Year"] == _LATER_YEAR, "Value"].iloc[0] == _NORMALIZED_LATER
    )  # 53.0 -> 0.53 normalized
    assert df.loc[df["Year"] == _EARLIER_YEAR, "Value"].iloc[0] == _NORMALIZED_EARLIER
