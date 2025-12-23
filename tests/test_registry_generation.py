from __future__ import annotations

import pytest
import pandas as pd
from pathlib import Path
from scripts.reporting.generate_parameter_registry import generate_manuscript_table

def test_generate_manuscript_table(tmp_path):
    """Verify generation of clean parameter table for manuscript."""
    out_file = tmp_path / "manuscript_table.csv"
    
    generate_manuscript_table(out_file)
    
    assert out_file.exists()
    df = pd.read_csv(out_file)
    
    assert "Parameter" in df.columns
    assert "Value" in df.columns
    assert "Source" in df.columns
    assert len(df) > 5
