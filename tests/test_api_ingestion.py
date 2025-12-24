from __future__ import annotations

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from scripts.data.ingest_aihw_api import process_api_data

def test_process_api_data():
    """Verify that raw API data is correctly merged with dataset info."""
    raw_data = pd.DataFrame([
        {"data_set_id": 1, "value": 53.0, "reporting_unit_summary": {"reporting_unit_name": "Australia"}},
        {"data_set_id": 2, "value": 55.0, "reporting_unit_summary": {"reporting_unit_name": "Australia"}},
    ])
    
    datasets = [
        {"data_set_id": 1, "reporting_end_date": "2024-06-30"},
        {"data_set_id": 2, "reporting_end_date": "2023-06-30"},
    ]
    
    df = process_api_data(raw_data, datasets)
    
    assert len(df) == 2
    assert "Year" in df.columns
    assert df.loc[df["Year"] == 2024, "Value"].iloc[0] == 0.53 # 53.0 -> 0.53 normalized
    assert df.loc[df["Year"] == 2023, "Value"].iloc[0] == 0.55
