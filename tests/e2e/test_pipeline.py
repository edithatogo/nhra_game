from __future__ import annotations

import subprocess
from pathlib import Path


def test_snakemake_baseline_pipeline():
    """
    E2E test to verify that the snakemake pipeline can run the baseline simulation.
    """
    # Force dry-run first to check dependencies
    subprocess.run(["snakemake", "--dry-run", "run_baseline"], check=True)

    # Run the actual rule (minimal)
    # We use --cores 1 for the test environment
    result = subprocess.run(
        [
            "snakemake",
            "--cores",
            "1",
            "run_baseline",
            "--forceall",  # ensure it actually runs even if files exist
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert Path("data/baseline/tables/trajectory.csv").exists()


def test_snakemake_context_pack():
    """
    E2E test for the context pack generation.
    """
    result = subprocess.run(
        ["snakemake", "--cores", "1", "context_pack", "--forceall"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert Path("context/CONTEXT_PACK.md").exists()
