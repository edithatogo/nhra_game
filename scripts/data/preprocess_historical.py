from __future__ import annotations
import pandas as pd
import numpy as np
from nhra_game_theory.domain.schemas import AIHWSchema

def normalize_nhra_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes raw NHRA metrics and interpolates missing years.
    
    Expected columns: Year, Metric, Value
    Returns: DataFrame with columns [year, within4, occupancy, effective_share]
    """
    # 0. Validate input data using AIHWSchema
    AIHWSchema.validate(df)

    # 1. Pivot to wide format
    pivot_df = df.pivot(index="Year", columns="Metric", values="Value")
    pivot_df.index.name = "year"
    
    # 2. Rename columns to standard internal names
    column_map = {
        "Within 4 Hours": "within4",
        "Occupancy": "occupancy",
        "Effective Share": "effective_share"
    }
    pivot_df = pivot_df.rename(columns=column_map)
    
    # 3. Create complete year range
    all_years = range(pivot_df.index.min(), pivot_df.index.max() + 1)
    pivot_df = pivot_df.reindex(all_years)
    
    # 4. Linearly interpolate missing values
    pivot_df = pivot_df.interpolate(method="linear")
    
    return pivot_df.reset_index()

if __name__ == "__main__":
    import os
    
    # Define paths relative to the script's location or CWD
    RAW_PATH = "data/raw/historical_aihw_ed.csv"
    OUT_PATH = "data/calibration_v21/historical_normalized.csv"
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    if os.path.exists(RAW_PATH):
        print(f"Processing {RAW_PATH}...")
        df_raw = pd.read_csv(RAW_PATH)
        df_norm = normalize_nhra_data(df_raw)
        df_norm.to_csv(OUT_PATH, index=False)
        print(f"Saved normalized data to {OUT_PATH}")
    else:
        print(f"Error: {RAW_PATH} not found.")