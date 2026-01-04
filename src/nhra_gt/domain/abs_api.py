"""
ABS Data API Client.

Handles fetching and parsing Wage Price Index (WPI) data for the health sector.
"""

from __future__ import annotations

import contextlib
import logging
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ABS_API_BASE_URL = "https://data.api.abs.gov.au/rest/data"
WPI_DATAFLOW = "ABS,WPI"
# MEASURE=1 (Index), INDEX=THRPEB (Total hourly), SECTOR=7 (Total), INDUSTRY=Q (Health), TSEST=10 (Original), REGION=AUS, FREQ=Q
WPI_HEALTH_KEY = "1.THRPEB.7.Q.10.AUS.Q"


class ABSApiClient:
    """Client for fetching data from the Australian Bureau of Statistics Data API."""

    def __init__(self, cache_dir: Path | str = "data/raw"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_wpi_health(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetches the WPI for Health Care and Social Assistance.

        Returns:
            DataFrame with columns ['year', 'wpi_health_index'] normalized to 2011=100.
        """
        cache_path = self.cache_dir / "abs_wpi_health_raw.csv"

        if use_cache and cache_path.exists():
            logger.info(f"Using cached WPI data from {cache_path}")
            df_raw = pd.read_csv(cache_path)
        else:
            url = f"{ABS_API_BASE_URL}/{WPI_DATAFLOW}/{WPI_HEALTH_KEY}"
            headers = {"Accept": "application/vnd.sdmx.data+csv"}

            logger.info(f"Fetching WPI data from {url}")
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                with open(cache_path, "w") as f:
                    f.write(response.text)

                df_raw = pd.read_csv(cache_path)
            except Exception as e:
                logger.error(f"Failed to fetch WPI data from ABS API: {e}")
                if cache_path.exists():
                    logger.warning("Falling back to existing cache.")
                    df_raw = pd.read_csv(cache_path)
                else:
                    raise

        # Process: Convert TIME_PERIOD (YYYY-QX) to year and average
        df_raw["year"] = df_raw["TIME_PERIOD"].str[:4].astype(int)

        # Annual average
        df_annual = df_raw.groupby("year")["OBS_VALUE"].mean().reset_index()
        df_annual = df_annual.rename(columns={"OBS_VALUE": "wpi_health_index"})

        # Normalize to 2011 = 100.0
        if 2011 in df_annual["year"].values:
            base_val = df_annual.loc[df_annual["year"] == 2011, "wpi_health_index"].values[0]
            df_annual["wpi_health_index"] = (df_annual["wpi_health_index"] / base_val) * 100.0
        else:
            logger.warning("2011 not found in WPI data. Normalization might be inconsistent.")

        return df_annual.sort_values("year")


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    client = ABSApiClient()
    with contextlib.suppress(Exception):
        wpi_df = client.fetch_wpi_health(use_cache=False)
