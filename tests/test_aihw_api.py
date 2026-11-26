"""Tests for AIHW API."""

from __future__ import annotations

from unittest.mock import patch

import polars as pl
import pytest

from nhra_gt.domain.aihw_api import AIHWClient

_MEASURE_COUNT = 2
_DATA_ROW_COUNT = 2
_FIRST_WITHIN_FOUR = 0.53


@pytest.fixture
def client():
    """Provide the AIHW client used by the ingestion tests."""
    return AIHWClient()


@patch("requests.Session.get")
def test_fetch_measures(mock_get, client):
    """Verify that the client can fetch the list of available measures."""
    mock_get.return_value.json.return_value = [
        {"code": "ED_WAIT", "name": "Emergency department waiting times"},
        {"code": "ADMIT_OCC", "name": "Admitted patient care occupancy"},
    ]
    mock_get.return_value.status_code = 200

    measures = client.get_measures()
    assert len(measures) == _MEASURE_COUNT
    assert measures[0]["code"] == "ED_WAIT"


@patch("requests.Session.get")
def test_fetch_data_items(mock_get, client):
    """Verify that the client can fetch data items for a specific measure."""
    mock_get.return_value.json.return_value = [
        {"reportingYear": "2023-24", "value": 0.53, "reportingUnitName": "Australia"},
        {"reportingYear": "2022-23", "value": 0.55, "reportingUnitName": "Australia"},
    ]
    mock_get.return_value.status_code = 200

    df = client.get_measure_data("ED_WAIT")
    assert isinstance(df, pl.DataFrame)
    assert len(df) == _DATA_ROW_COUNT
    assert df["value"][0] == _FIRST_WITHIN_FOUR


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__]))
