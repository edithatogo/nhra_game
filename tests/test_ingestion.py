from __future__ import annotations

import pandas as pd

# I'll implement these ingestors in a new module
from scripts.ingest_structured import ABSIngestor, AIHWIngestor


def test_aihw_ingestor_mock_file(tmp_path):
    """Verify that the AIHW ingestor can parse a simulated CSV and return EvidenceEntries."""
    # Create a simulated AIHW CSV
    csv_path = tmp_path / "aihw_ed.csv"
    data = {
        "Year": [2023, 2024],
        "Metric": ["Within 4 Hours", "Within 4 Hours"],
        "Value": [0.55, 0.53],
        "Lower_CI": [0.54, 0.51],
        "Upper_CI": [0.56, 0.55],
        "Source": ["Table 1.1", "Table 1.1"],
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)

    ingestor = AIHWIngestor(source_path=csv_path)
    entries = ingestor.extract_entries()

    assert len(entries) >= 1
    target = next(e for e in entries if e.parameter == "within4_base")
    assert target.mean == 0.53
    assert target.lower_ci == 0.51
    assert "Table 1.1" in target.source_url


def test_abs_ingestor_mock_file(tmp_path):
    """Verify that the ABS ingestor can parse simulated population data."""
    csv_path = tmp_path / "abs_pop.csv"
    data = {
        "State": ["Australia", "Australia"],
        "Year": [2023, 2024],
        "Growth_Rate": [0.021, 0.024],
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)

    ingestor = ABSIngestor(source_path=csv_path)
    entries = ingestor.extract_entries()

    target = next(e for e in entries if e.parameter == "demand_base_growth")
    assert target.mean == 0.024
