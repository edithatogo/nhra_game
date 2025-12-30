from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from nhra_gt.domain.abs_api import ABSApiClient


def test_abs_client_initialization():
    client = ABSApiClient(cache_dir="data/test_cache")
    assert client.cache_dir == Path("data/test_cache")


@pytest.mark.vcr
def test_fetch_wpi_health_structure():
    """Verify the structure of the fetched WPI data."""
    client = ABSApiClient()
    # Use cache=False to ensure it hits the API (or VCR)
    df = client.fetch_wpi_health(use_cache=False)

    assert isinstance(df, pd.DataFrame)
    assert "year" in df.columns
    assert "wpi_health_index" in df.columns
    assert len(df) > 0

    # Check normalization (approximate if 2011 is present)
    if 2011 in df["year"].values:
        val_2011 = df.loc[df["year"] == 2011, "wpi_health_index"].values[0]
        assert pytest.approx(val_2011) == 100.0


def test_fetch_wpi_health_cache():
    """Verify that caching works."""
    cache_dir = "data/test_cache"
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    cache_file = Path(cache_dir) / "abs_wpi_health_raw.csv"

    # Create a fake cache file
    fake_data = (
        "DATAFLOW,MEASURE,INDEX,SECTOR,INDUSTRY,TSEST,REGION,FREQ,TIME_PERIOD,OBS_VALUE\n"
        "ABS:WPI(1.2.0),1,THRPEB,7,Q,10,AUS,Q,2011-Q1,100.0\n"
        "ABS:WPI(1.2.0),1,THRPEB,7,Q,10,AUS,Q,2011-Q2,100.0\n"
        "ABS:WPI(1.2.0),1,THRPEB,7,Q,10,AUS,Q,2011-Q3,100.0\n"
        "ABS:WPI(1.2.0),1,THRPEB,7,Q,10,AUS,Q,2011-Q4,100.0\n"
    )

    with open(cache_file, "w") as f:
        f.write(fake_data)

    client = ABSApiClient(cache_dir=cache_dir)
    df = client.fetch_wpi_health(use_cache=True)

    assert 2011 in df["year"].values
    assert df.loc[df["year"] == 2011, "wpi_health_index"].values[0] == 100.0

    # Cleanup
    cache_file.unlink()
    Path(cache_dir).rmdir()
