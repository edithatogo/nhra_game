from __future__ import annotations

import pandas as pd
import pytest

# Implementation will be in a new module
from nhra_game_theory.domain.schemas import ABSSchema, AIHWSchema
from pandera.errors import SchemaError


def test_aihw_schema_validation():
    """Verify that the AIHW schema enforces column presence and types."""
    valid_data = pd.DataFrame({
        "Year": [2023, 2024],
        "Metric": ["Within 4 Hours", "Within 4 Hours"],
        "Value": [0.55, 0.53],
        "Lower_CI": [0.54, 0.51],
        "Upper_CI": [0.56, 0.55],
        "Source": ["Table 1.1", "Table 1.1"]
    })
    # Should not raise
    AIHWSchema.validate(valid_data)
    
    invalid_data = valid_data.drop(columns=["Metric"])
    with pytest.raises(SchemaError):
        AIHWSchema.validate(invalid_data)

def test_abs_schema_validation():
    """Verify that the ABS schema enforces column presence and ranges."""
    valid_data = pd.DataFrame({
        "State": ["Australia"],
        "Year": [2024],
        "Growth_Rate": [0.024]
    })
    ABSSchema.validate(valid_data)
    
    # Growth rate must be realistic (e.g. < 10%)
    invalid_data = pd.DataFrame({
        "State": ["Australia"],
        "Year": [2024],
        "Growth_Rate": [1.5] # 150% growth is invalid
    })
    with pytest.raises(SchemaError):
        ABSSchema.validate(invalid_data)
