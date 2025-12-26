from __future__ import annotations

from pathlib import Path

import pandas as pd

from nhra_gt.domain.aihw_api import AIHWClient
from nhra_gt.domain.schemas import AIHWSchema


def process_api_data(raw_data: pd.DataFrame, datasets: list[dict]) -> pd.DataFrame:
    """Merges API results with metadata and normalizes fields."""
    # 1. Map dataset_id to metadata
    ds_info = {
        d["data_set_id"]: {
            "year": int(d["reporting_end_date"][:4]),
            "end_date": d["reporting_end_date"],
        }
        for d in datasets
    }

    df = raw_data.copy()
    df["Year"] = df["data_set_id"].apply(lambda x: ds_info.get(x, {}).get("year"))
    df["EndDate"] = df["data_set_id"].apply(lambda x: ds_info.get(x, {}).get("end_date"))

    # 2. Extract unit code
    df["Unit_Code"] = df["reporting_unit_summary"].apply(lambda x: x.get("reporting_unit_code"))

    # 3. Filter for National (NAT) aggregate (where peer_group is None)
    df = df[(df["Unit_Code"] == "NAT") & (df["peer_group_summary"].isna())]

    # AND filter for 'All patients' (MYH-RM0015) to get total aggregate across triage
    df = df[df["reported_measure_code"] == "MYH-RM0015"]

    # 4. Resolve duplicates (multiple periods per year) - Pick latest by EndDate
    df = df.sort_values("EndDate", ascending=False).drop_duplicates(subset=["Year"])

    # 5. Normalize Value (Percentage -> Fraction)
    df["Value"] = df["value"] / 100.0

    # 6. Format for AIHWSchema
    df["Metric"] = "Within 4 Hours"
    df["Lower_CI"] = None
    df["Upper_CI"] = None
    df["Source"] = "AIHW MyHospitals API"

    return df.sort_values("Year")[["Year", "Metric", "Value", "Lower_CI", "Upper_CI", "Source"]]


def main():
    client = AIHWClient()

    print("Fetching metadata...")
    datasets = client._get("/datasets")

    print("Fetching ED performance data (MYH0005)...")
    raw_data = client.get_measure_data("MYH0005")

    print("Processing...")
    processed = process_api_data(raw_data, datasets)

    # Validate
    AIHWSchema.validate(processed)

    out_path = Path("data/raw/historical_aihw_api.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(out_path, index=False)

    print(f"Saved API-sourced data to {out_path}")
    print(processed.tail())


if __name__ == "__main__":
    import os

    # Ensure logfire doesn't hang
    os.environ["LOGFIRE_SEND_TO_LOGFIRE"] = "false"
    main()
