from __future__ import annotations

import pandas as pd
from scripts.reporting.generate_methods_appendix import generate_appendix


def test_generate_appendix(tmp_path):
    """Verify methods appendix generation."""
    out_file = tmp_path / "methods.md"

    # Mock registry
    registry_path = tmp_path / "registry.csv"
    pd.DataFrame(
        {
            "parameter": ["cost_shifting_intensity"],
            "description": ["Test param"],
            "evidence_source": ["Source A"],
            "default": [0.35],
        }
    ).to_csv(registry_path, index=False)

    # Mock references
    refs_path = tmp_path / "refs.json"
    with open(refs_path, "w") as f:
        import json

        json.dump([], f)

    generate_appendix(registry_path, out_file, refs_path)

    assert out_file.exists()
    content = out_file.read_text()
    assert "# Methods Appendix" in content
    assert "cost_shifting_intensity" in content
    assert "Source A" in content
