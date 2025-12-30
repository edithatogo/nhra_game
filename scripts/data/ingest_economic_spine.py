from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_gt.domain.abs_api import ABSApiClient
from nhra_gt.domain.ihacpa_api import IHACPAClient
from nhra_gt.domain.schemas import EconomicSpineSchema

# Fallback Data (Synthetic based on ABS WPI Health trends)
WPI_SERIES_FALLBACK = {
    2011: 100.0,
    2012: 103.5,
    2013: 106.8,
    2014: 109.5,
    2015: 112.2,
    2016: 114.8,
    2017: 117.4,
    2018: 120.3,
    2019: 123.3,
    2020: 125.8,
    2021: 128.3,
    2022: 131.5,
    2023: 137.9,
    2024: 144.8,
    2025: 152.0,
}


def process_economic_data(nep_df: pd.DataFrame, wpi_df: pd.DataFrame) -> pd.DataFrame:
    """Merges and validates NEP and WPI data."""
    merged = pd.merge(nep_df, wpi_df, on="year")
    # Ensure column names match schema
    if "NEP" in merged.columns:
        merged = merged.rename(columns={"NEP": "nep_per_nwau"})
    if "WPI" in merged.columns:
        merged = merged.rename(columns={"WPI": "wpi_health_index"})

    # Sort and validate
    merged = merged.sort_values("year")
    EconomicSpineSchema.validate(merged)

    return merged


def main():
    # 1. Fetch WPI Data (Automated)
    abs_client = ABSApiClient()
    try:
        print("Fetching automated WPI data from ABS API...")
        wpi_df = abs_client.fetch_wpi_health(use_cache=False)
        wpi_df = wpi_df[wpi_df["year"] >= 2011]
    except Exception as e:
        print(f"Warning: Failed to fetch automated WPI data: {e}")
        print("Using fallback synthetic WPI series.")
        wpi_df = pd.DataFrame(
            list(WPI_SERIES_FALLBACK.items()), columns=["year", "wpi_health_index"]
        )

    # 2. Fetch NEP Data (Automated via local file parsing)
    ihacpa_client = IHACPAClient()
    try:
        print("Parsing local IHACPA calculators for NEP data...")
        nep_df = ihacpa_client.fetch_nep_series()
        nep_df = nep_df[nep_df["year"] >= 2011]
    except Exception as e:
        print(f"Error: Failed to process IHACPA data: {e}")
        return

    print("Processing Economic Spine data...")
    spine_df = process_economic_data(nep_df, wpi_df)

    # Save to data/calibration_v21/economic_spine.csv
    out_path = Path("data/calibration_v21/economic_spine.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    spine_df.to_csv(out_path, index=False)

    print(f"Economic Spine saved to {out_path}")
    print("\nSample Data:")
    print(spine_df.tail())


if __name__ == "__main__":
    main()
