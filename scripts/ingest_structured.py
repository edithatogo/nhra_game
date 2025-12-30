from __future__ import annotations

from pathlib import Path

import polars as pl

from nhra_gt.domain.registry import EvidenceEntry


class AIHWIngestor:
    def __init__(self, source_path: Path):
        self.source_path = source_path

    def extract_entries(self) -> list[EvidenceEntry]:
        df = pl.read_csv(self.source_path)
        # Filter for latest year
        latest_year = df["Year"].max()
        latest_df = df.filter(pl.col("Year") == latest_year)

        entries = []
        for row in latest_df.to_dicts():
            if row["Metric"] == "Within 4 Hours":
                entries.append(
                    EvidenceEntry(
                        parameter="within4_base",
                        mean=float(row["Value"]),
                        lower_ci=float(row["Lower_CI"]) if row["Lower_CI"] is not None else None,
                        upper_ci=float(row["Upper_CI"]) if row["Upper_CI"] is not None else None,
                        source_url=str(row["Source"]),
                        nhmrc_level="III-2",
                        unit="proportion",
                        access_date="2025-12-23",
                    )
                )
        return entries


class ABSIngestor:
    def __init__(self, source_path: Path):
        self.source_path = source_path

    def extract_entries(self) -> list[EvidenceEntry]:
        df = pl.read_csv(self.source_path)
        latest_year = df["Year"].max()
        latest_df = df.filter((pl.col("Year") == latest_year) & (pl.col("State") == "Australia"))

        entries = []
        for row in latest_df.to_dicts():
            entries.append(
                EvidenceEntry(
                    parameter="demand_base_growth",
                    mean=float(row["Growth_Rate"]),
                    source_url="ABS Population Data",
                    nhmrc_level="IV",
                    unit="annual_rate",
                    access_date="2025-12-23",
                )
            )
        return entries
