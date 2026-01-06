"""Pydantic schemas for dashboard components."""

from pathlib import Path

import pandas as pd


def load_parameter_schema() -> pd.DataFrame:
    """Loads the parameter registry CSV as a schema for UI generation."""
    # Assuming relative to package root
    path = Path(__file__).parent.parent.parent.parent / "context/04_parameter_registry.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def get_slider_metadata(df: pd.DataFrame) -> list[dict]:
    """Filters schema for parameters that should be shown as sliders."""
    # Parameters with range_low and range_high are candidates for sliders
    mask = df["range_low"].notna() & df["range_high"].notna()
    subset = df[mask].copy()
    return subset.to_dict(orient="records")
