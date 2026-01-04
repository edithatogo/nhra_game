"""
Pandera Schemas for Data Validation.

Defines the expected structure and constraints for external data sources
(AIHW, ABS) and internal simulation results.
"""

from __future__ import annotations

import pandera.pandas as pa
from pandera.typing import Series


class AIHWSchema(pa.DataFrameModel):
    """Schema for AIHW hospital performance data."""
    Year: Series[int] = pa.Field(ge=2000, le=2100)
    Metric: Series[str] = pa.Field(isin=["Within 4 Hours", "Occupancy", "Handover"])
    Value: Series[float] = pa.Field(ge=0.0, le=120.0)
    Lower_CI: Series[float] | None = pa.Field(ge=0.0, le=120.0, nullable=True)
    Upper_CI: Series[float] | None = pa.Field(ge=0.0, le=120.0, nullable=True)
    Source: Series[str] | None = pa.Field(nullable=True)

    class Config:
        strict = True
        coerce = True


class ABSSchema(pa.DataFrameModel):
    """Schema for ABS Wage Price Index (WPI) data."""
    State: Series[str] = pa.Field(
        isin=["Australia", "NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]
    )
    Year: Series[int] = pa.Field(ge=2000, le=2100)
    Growth_Rate: Series[float] = pa.Field(ge=-0.1, le=0.1)

    class Config:
        strict = True
        coerce = True


class EconomicSpineSchema(pa.DataFrameModel):
    """Schema for the consolidated economic data spine."""
    year: Series[int] = pa.Field(ge=2000, le=2100)
    nep_per_nwau: Series[float] = pa.Field(ge=4000, le=10000)
    wpi_health_index: Series[float] = pa.Field(ge=80, le=200)

    class Config:
        strict = True
        coerce = True
