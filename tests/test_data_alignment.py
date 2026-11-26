"""Tests for data alignment."""

from __future__ import annotations

import polars as pl
import pytest
from scripts.data.preprocess_historical import normalize_nhra_data

_BASE_YEAR = 2011
_BASE_WITHIN_FOUR = 0.70
_NEXT_YEAR = 2012


def test_historical_data_alignment():
    """Verify that historical data can be aligned to model years."""
    raw_data = pl.DataFrame(
        {
            "Year": [2011, 2012, 2020],
            "Metric": ["Within 4 Hours", "Within 4 Hours", "Within 4 Hours"],
            "Value": [0.70, 0.68, 0.55],
        }
    )

    # We expect normalization to produce a standard format
    normalized = normalize_nhra_data(raw_data)

    assert _BASE_YEAR in normalized["year"].to_list()
    assert normalized.filter(pl.col("year") == _BASE_YEAR)["within4"][0] == _BASE_WITHIN_FOUR


def test_historical_data_missing_years():
    """Verify that the aligner handles missing data points (e.g. interpolation)."""
    raw_data = pl.DataFrame(
        {
            "Year": [2011, 2013],
            "Metric": ["Within 4 Hours", "Within 4 Hours"],
            "Value": [0.70, 0.60],
        }
    )

    normalized = normalize_nhra_data(raw_data)
    # Should fill in 2012
    assert _NEXT_YEAR in normalized["year"].to_list()
    # Simple linear interpolation check
    assert normalized.filter(pl.col("year") == _NEXT_YEAR)["within4"][0] == pytest.approx(0.65)
