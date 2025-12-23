from __future__ import annotations

import pytest
import pandas as pd
from pathlib import Path
from scripts.reporting.generate_methods_appendix import generate_appendix

def test_generate_appendix(tmp_path):
    """Verify methods appendix generation."""
    out_file = tmp_path / "methods.md"
    
    # Mock registry
    registry_path = tmp_path / "registry.csv"
    pd.DataFrame({
        "parameter": ["cost_shifting_intensity"],
        "description": ["Test param"],
        "evidence_source": ["Source A"],
        "default": [0.35]
    }).to_csv(registry_path, index=False)
    
    generate_appendix(registry_path, out_file)
    
    assert out_file.exists()
    content = out_file.read_text()
    assert "# Methods Appendix" in content
    assert "cost_shifting_intensity" in content
    assert "Source A" in content
