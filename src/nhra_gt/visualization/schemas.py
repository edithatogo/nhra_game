from __future__ import annotations

import pandera as pa
from pandera.typing import Series


class TrajectorySchema(pa.DataFrameModel):
    year: Series[int] = pa.Field(coerce=True)
    # y_col and quantile cols are dynamic, so we might use a base schema
    # or validate presence of columns in the function.


class StrategyFrequencySchema(pa.DataFrameModel):
    year: Series[int] = pa.Field(coerce=True)
    game: Series[str] = pa.Field(coerce=True)
    strategy: Series[str] = pa.Field(coerce=True)
    share: Series[float] = pa.Field(coerce=True, ge=0, le=1)


class MorrisSchema(pa.DataFrameModel):
    mu_star: Series[float] = pa.Field(coerce=True)
    mu_star_conf: Series[float] = pa.Field(coerce=True)


class RankCorrelationSchema(pa.DataFrameModel):
    # Requires year and at least the outcome_col and params
    year: Series[int] = pa.Field(coerce=True)
