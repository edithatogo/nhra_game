from __future__ import annotations

import subprocess
from pathlib import Path


def test_snakemake_baseline_pipeline():
    """
    E2E test to verify that the snakemake pipeline can run the baseline simulation.
    """
    # If outputs are checked into git, Snakemake >=9 can treat them as lacking provenance metadata
    # and refuse to "force" reruns. Ensure the output is absent so the rule must execute.
    out_path = Path("data/baseline/tables/trajectory.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.unlink(missing_ok=True)

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
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert out_path.exists()


def test_snakemake_context_pack():
    """
    E2E test for the context pack generation.
    """
    out_path = Path("context/CONTEXT_PACK.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.unlink(missing_ok=True)

    result = subprocess.run(
        ["snakemake", "--cores", "1", "context_pack"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert out_path.exists()
