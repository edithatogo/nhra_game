from __future__ import annotations

from pathlib import Path

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None  # type: ignore[assignment]

from nhra_gt.domain.registry import EvidenceEntry


class AIHWIngestor:
    def __init__(self, source_path: Path):
        self.source_path = source_path

    def extract_entries(self) -> list[EvidenceEntry]:
        if pl is None:
            import pandas as pd

            df = pd.read_csv(self.source_path)
            latest_year = df["Year"].max()
            latest_df = df[df["Year"] == latest_year]
            rows = latest_df.to_dict("records")
        else:
            df = pl.read_csv(self.source_path)
            latest_year = df["Year"].max()
            latest_df = df.filter(pl.col("Year") == latest_year)
            rows = latest_df.to_dicts()

        entries = []
        for row in rows:
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
        if pl is None:
            import pandas as pd

            df = pd.read_csv(self.source_path)
            latest_year = df["Year"].max()
            latest_df = df[(df["Year"] == latest_year) & (df["State"] == "Australia")]
            rows = latest_df.to_dict("records")
        else:
            df = pl.read_csv(self.source_path)
            latest_year = df["Year"].max()
            latest_df = df.filter(
                (pl.col("Year") == latest_year) & (pl.col("State") == "Australia")
            )
            rows = latest_df.to_dicts()

        entries = []
        for row in rows:
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
