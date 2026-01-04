from __future__ import annotations

import pandera.pandas as pa


class TrajectorySchema(pa.DataFrameModel):
    year: int = pa.Field(coerce=True)


class StrategyFrequencySchema(pa.DataFrameModel):
    year: int = pa.Field(coerce=True)
    game: str = pa.Field(coerce=True)
    strategy: str = pa.Field(coerce=True)
    share: float = pa.Field(coerce=True, ge=0, le=1)


class MorrisSchema(pa.DataFrameModel):
    mu_star: float = pa.Field(coerce=True)
    mu_star_conf: float = pa.Field(coerce=True)


class RankCorrelationSchema(pa.DataFrameModel):
    year: int = pa.Field(coerce=True)
