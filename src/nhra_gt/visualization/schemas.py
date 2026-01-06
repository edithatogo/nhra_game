"""Pandera schemas for validating visualization dataframes."""

from __future__ import annotations

import pandera.pandas as pa


class TrajectorySchema(pa.DataFrameModel):
    """Schema for simulation trajectory data."""

    year: int = pa.Field(coerce=True)


class StrategyFrequencySchema(pa.DataFrameModel):
    """Schema for strategy frequency data."""

    year: int = pa.Field(coerce=True)
    game: str = pa.Field(coerce=True)
    strategy: str = pa.Field(coerce=True)
    share: float = pa.Field(coerce=True, ge=0, le=1)


class MorrisSchema(pa.DataFrameModel):
    """Schema for Morris sensitivity analysis results."""

    mu_star: float = pa.Field(coerce=True)
    mu_star_conf: float = pa.Field(coerce=True)


class RankCorrelationSchema(pa.DataFrameModel):
    """Schema for rank correlation results."""

    year: int = pa.Field(coerce=True)
