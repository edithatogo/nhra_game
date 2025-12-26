from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_gt.domain.schemas import EconomicSpineSchema

# Ground Truth Data (Sourced from IHACPA Determinations 2011-2025)
NEP_SERIES = {
    2011: 4808.0,
    2012: 4808.0,
    2013: 4993.0,
    2014: 5007.0,
    2015: 4971.0,
    2016: 4883.0,
    2017: 4933.07,
    2018: 5012.0,
    2019: 5134.0,
    2020: 5320.0,
    2021: 5597.0,
    2022: 5797.0,
    2023: 6032.0,
    2024: 6465.0,
    2025: 7258.0,
}

# Ground Truth Data (Synthetic based on ABS WPI Health trends)
WPI_SERIES = {
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
    merged = pd.merge(nep_df, wpi_df, on="Year")
    merged = merged.rename(
        columns={"Year": "year", "NEP": "nep_per_nwau", "WPI": "wpi_health_index"}
    )

    # Sort and validate
    merged = merged.sort_values("year")
    EconomicSpineSchema.validate(merged)

    return merged


def main():
    # Convert dictionaries to DataFrames
    nep_df = pd.DataFrame(list(NEP_SERIES.items()), columns=["Year", "NEP"])
    wpi_df = pd.DataFrame(list(WPI_SERIES.items()), columns=["Year", "WPI"])

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
