from __future__ import annotations

import requests
import pandas as pd
from typing import Any

class AIHWClient:
    """Client for the AIHW MyHospitals API (v1)."""
    
    BASE_URL = "https://myhospitalsapi.aihw.gov.au/api/v1"
    
    def __init__(self):
        self.session = requests.Session()

    def _get(self, endpoint: str) -> Any:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_measures(self) -> list[dict[str, Any]]:
        """Fetch all available measures."""
        return self._get("/measures")

    def get_measure_data(self, measure_code: str) -> pd.DataFrame:
        """Fetch data items for a specific measure code."""
        endpoint = f"/measures/{measure_code}/data-items"
        data = self._get(endpoint)
        return pd.DataFrame(data)

    def get_reporting_units(self) -> list[dict[str, Any]]:
        """Fetch all available reporting units."""
        return self._get("/reporting-units")
