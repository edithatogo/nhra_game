from __future__ import annotations

from pathlib import Path

import pandas as pd
import polars as pl

# Note: We'll skip runtime schema validation via Pandera here as we are moving to Polars.
# Future enhancement: use patito or similar for Polars validation.

def normalize_nhra_data(df: pl.DataFrame | pd.DataFrame) -> pl.DataFrame:
    """Normalizes raw NHRA metrics and interpolates missing years.

    Expected columns: Year, Metric, Value
    Returns: DataFrame with columns [year, within4, occupancy, effective_share]
    """
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)

    # 1. Pivot to wide format
    pivot_df = df.pivot(
        on="Metric",
        index="Year",
        values="Value",
        aggregate_function="first"
    )
    pivot_df = pivot_df.rename({"Year": "year"})

    # 2. Rename columns to standard internal names
    column_map = {
        "Within 4 Hours": "within4",
        "Occupancy": "occupancy",
        "Effective Share": "effective_share",
    }

    # Map only columns that exist
    actual_map = {old: new for old, new in column_map.items() if old in pivot_df.columns}
    pivot_df = pivot_df.rename(actual_map)

    # 3. Create complete year range and join to ensure all years exist
    min_year = pivot_df["year"].min()
    max_year = pivot_df["year"].max()

    if min_year is not None and max_year is not None:
        full_years = pl.DataFrame({"year": range(min_year, max_year + 1)})
        pivot_df = full_years.join(pivot_df, on="year", how="left")

    # 4. Linearly interpolate missing values
    # In Polars, we can interpolate specific columns
    metrics = ["within4", "occupancy", "effective_share"]
    for m in metrics:
        if m in pivot_df.columns:
            pivot_df = pivot_df.with_columns(
                pl.col(m).interpolate()
            )

    return pivot_df


if __name__ == "__main__":
    API_RAW_PATH = Path("data/raw/historical_aihw_api.csv")
    LEGACY_RAW_PATH = Path("data/raw/historical_aihw_ed.csv")
    OUT_PATH = Path("data/calibration/historical_normalized.csv")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 1. Prioritize automated API path
    raw_path = API_RAW_PATH if API_RAW_PATH.exists() else LEGACY_RAW_PATH

    if raw_path.exists():
        print(f"Processing {raw_path}...")
        df_raw = pl.read_csv(raw_path)
        df_norm = normalize_nhra_data(df_raw)
        df_norm.write_csv(OUT_PATH)
        print(f"Saved normalized data to {OUT_PATH}")
    else:
        print(f"Error: No raw data found at {API_RAW_PATH} or {LEGACY_RAW_PATH}")
