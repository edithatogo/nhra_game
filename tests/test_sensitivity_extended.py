from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from nhra_gt.sensitivity import (
    generate_sensitivity_summary,
    get_salib_problem,
    plot_sobol_heatmap,
    run_psa,
)


def test_generate_sensitivity_summary_logic(tmp_path):
    """Verify markdown summary generation with mock data."""
    morris_csv = tmp_path / "morris.csv"
    sobol_csv = tmp_path / "sobol.csv"
    out_md = tmp_path / "summary.md"

    # Create mock morris data
    pd.DataFrame({"mu_star": [0.5, 0.2], "sigma": [0.1, 0.05]}, index=["param1", "param2"]).to_csv(
        morris_csv
    )

    # Create mock sobol data
    pd.DataFrame({"Parameter": ["param1", "param2"], "S1": [0.4, 0.1], "ST": [0.6, 0.2]}).to_csv(
        sobol_csv, index=False
    )

    generate_sensitivity_summary(morris_csv, sobol_csv, out_md)
    assert out_md.exists()
    content = out_md.read_text()
    assert "## 1. Morris Screening" in content
    assert "## 2. Sobol Analysis" in content
    assert "Primary Driver" in content


def test_plot_sobol_heatmap_with_interactions(tmp_path):
    """Verify heatmap plotting when S2 interaction indices are present."""
    output = tmp_path / "heatmap"
    si = {
        "names": ["p1", "p2"],
        "S1": [0.4, 0.3],
        "ST": [0.6, 0.5],
        "S1_conf": [0.05, 0.05],
        "ST_conf": [0.05, 0.05],
        "S2": np.array([[0.0, 0.1], [0.1, 0.0]]),
    }
    plot_sobol_heatmap(si, output)
    assert Path(str(output) + ".png").exists()


def dummy_model(params):
    return float(np.sum(params))


def test_run_psa_flow():
    """Verify PSA execution with simple distributions."""
    distributions = {
        "p1": lambda n: np.random.uniform(0, 1, n),
        "p2": lambda n: np.random.uniform(10, 20, n),
    }

    df = run_psa(distributions, dummy_model, n_samples=10, n_procs=1)
    assert len(df) == 10
    assert "outcome" in df.columns
    assert "p1" in df.columns


def test_get_salib_problem_invalid():
    """Verify error handling for invalid parameter names."""
    with pytest.raises(ValueError, match="not found in Params"):
        get_salib_problem(["invalid_param_name"])
