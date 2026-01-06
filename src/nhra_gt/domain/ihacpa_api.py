"""IHACPA API Client and Data Ingestion.

Handles fetching and parsing National Efficient Price (NEP) series data.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

try:
    from pyxlsb import open_workbook
except ImportError:  # pragma: no cover
    open_workbook = None

logger = logging.getLogger(__name__)


class IHACPAClient:
    """Simulated client for IHACPA data.

    Actually parses local NWAU calculators (Excel .xlsb) to extract NEP values.
    """

    def __init__(self, raw_dir: Path | str = "data/raw"):
        """Initialize the IHACPA client with a directory for raw Excel files."""
        self.raw_dir = Path(raw_dir)

    def extract_nep_from_file(self, file_path: Path) -> float | None:
        """Parses a single .xlsb file to find the NEP value."""
        if open_workbook is None:
            logger.warning("pyxlsb is not installed; cannot parse %s", file_path)
            return None
        try:
            with open_workbook(str(file_path)) as wb:
                if "Formula breakdown" not in wb.sheets:
                    return None

                with wb.get_sheet("Formula breakdown") as sheet:
                    for row in sheet.rows():
                        # Based on inspection, NEP label is followed by value
                        # Usually row 14, col 9 is 'NEP', col 10 is value
                        # We search for 'NEP' string then take next cell
                        row_vals = [cell.v for cell in row]
                        for i, val in enumerate(row_vals):
                            if val == "NEP" and i + 1 < len(row_vals):
                                nep_val = row_vals[i + 1]
                                if isinstance(nep_val, int | float):
                                    return float(nep_val)
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return None

    def fetch_nep_series(self) -> pd.DataFrame:
        """Scans raw_dir for calculators and builds the NEP series.

        Returns:
            DataFrame with columns ['year', 'nep_per_nwau'].
        """
        # Historical hardcoded values as baseline (pre-2025)
        # Sourced from Determination documents
        data = {
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

        # Scan for newer files (e.g. nwau26...)
        pattern = re.compile(r"nwau(\d{2})_calculator")
        for file in self.raw_dir.glob("*.xlsb"):
            match = pattern.search(file.name)
            if match:
                yy = int(match.group(1))
                year = 2000 + yy
                # If we don't have it or want to verify
                nep = self.extract_nep_from_file(file)
                if nep:
                    logger.info(f"Extracted NEP {nep} for year {year} from {file.name}")
                    data[year] = nep

        df = pd.DataFrame(list(data.items()), columns=["year", "nep_per_nwau"])
        return df.sort_values("year")


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    client = IHACPAClient()
    nep_df = client.fetch_nep_series()
