from __future__ import annotations
import pandera.pandas as pa
from pandera.typing import Series
from typing import Optional

class AIHWSchema(pa.DataFrameModel):
    Year: Series[int] = pa.Field(ge=2000, le=2100)
    Metric: Series[str] = pa.Field(isin=["Within 4 Hours", "Occupancy", "Handover"])
    Value: Series[float] = pa.Field(ge=0.0, le=120.0)
    Lower_CI: Optional[Series[float]] = pa.Field(ge=0.0, le=120.0, nullable=True)
    Upper_CI: Optional[Series[float]] = pa.Field(ge=0.0, le=120.0, nullable=True)
    Source: Optional[Series[str]] = pa.Field(nullable=True)

    class Config:
        strict = True
        coerce = True

class ABSSchema(pa.DataFrameModel):
    State: Series[str] = pa.Field(isin=["Australia", "NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"])
    Year: Series[int] = pa.Field(ge=2000, le=2100)
    Growth_Rate: Series[float] = pa.Field(ge=-0.1, le=0.1)

    class Config:
        strict = True
        coerce = True