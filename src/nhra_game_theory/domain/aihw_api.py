from __future__ import annotations

from typing import Any, cast

import pandas as pd
import requests


class AIHWClient:
    """Client for the AIHW MyHospitals API (v1)."""

    BASE_URL = "https://myhospitalsapi.aihw.gov.au/api/v1"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
        )

    def _get(self, endpoint: str) -> Any:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "result" in data:
            return data["result"]
        return data

    def get_measures(self) -> list[dict[str, Any]]:
        """Fetch all available measures."""
        return cast(list[dict[str, Any]], self._get("/measures"))

    def get_measure_data(self, measure_code: str) -> pd.DataFrame:
        """Fetch data items for a specific measure code."""
        endpoint = f"/measures/{measure_code}/data-items"
        data = self._get(endpoint)
        return pd.DataFrame(data)

    def get_reporting_units(self) -> list[dict[str, Any]]:
        """Fetch all available reporting units."""
        return cast(list[dict[str, Any]], self._get("/reporting-units"))
