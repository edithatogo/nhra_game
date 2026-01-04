from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError
from scripts.data.ingest_economic_spine import process_economic_data

from nhra_gt.domain.schemas import EconomicSpineSchema


def test_economic_data_processing():
    """Verify that economic data is correctly merged and validated."""
    # Input data should match IHACPA/ABS series
    nep_data = pd.DataFrame({"Year": [2023, 2024], "NEP": [6032.0, 6465.0]})
    wpi_data = pd.DataFrame({"Year": [2023, 2024], "WPI": [137.9, 144.8]})

    processed = process_economic_data(nep_data, wpi_data)

    # Should follow schema
    EconomicSpineSchema.validate(processed)

    assert processed.loc[processed["year"] == 2024, "nep_per_nwau"].iloc[0] == 6465.0
    assert processed.loc[processed["year"] == 2024, "wpi_health_index"].iloc[0] == 144.8


def test_economic_data_schema_failure():
    """Verify that invalid data raises SchemaError."""
    bad_data = pd.DataFrame(
        {
            "year": [2024],
            "nep_per_nwau": [1.0],  # Too low
            "wpi_health_index": [144.8],
        }
    )

    with pytest.raises(SchemaError):
        EconomicSpineSchema.validate(bad_data)
