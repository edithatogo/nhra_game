from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pandas as pd


def run_snakemake(rule: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Helper to run a snakemake rule."""
    cmd = [
        "snakemake",
        "--cores",
        "1",
        rule,
        "--printshellcmds",
        "--show-failed-logs",
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def test_pipeline_gsa_morris():
    """Verify that the GSA Morris rule runs and produces expected output."""
    out_path = Path("data/gsa/morris_results.csv")
    out_path.unlink(missing_ok=True)

    result = run_snakemake("gsa_morris")
    assert result.returncode == 0
    assert out_path.exists()

    # Integrity check: non-empty CSV with expected columns
    df = pd.read_csv(out_path)
    assert not df.empty
    assert "mu_star" in df.columns


def test_pipeline_calibrate_minimal():
    """Verify that the calibrate rule runs with a minimal trial count."""
    out_path = Path("data/calibration/calibration_optuna_best.csv")
    out_path.unlink(missing_ok=True)

    # Use environment variable to speed up test
    result = run_snakemake("calibrate", env={"NHRA_CALIBRATION_TRIALS": "1"})

    assert result.returncode == 0
    assert out_path.exists()

    df = pd.read_csv(out_path)
    assert not df.empty
    assert "best_value" in df.columns


def test_pipeline_baseline_integrity():
    """Verify that the baseline trajectory contains plausible data."""
    out_path = Path("data/baseline/tables/trajectory.csv")
    # Rule might have already run, or we run it
    run_snakemake("run_baseline")

    assert out_path.exists()
    df = pd.read_csv(out_path)

    # Check years
    assert df["year"].min() >= 2020
    assert df["year"].max() <= 2040

    # Check within4_mean (share should be 0-1)
    if "within4_mean" in df.columns:
        assert df["within4_mean"].between(0, 1).all()

    # Check occupancy (should be positive and generally < 1.1)
    if "occupancy_mean" in df.columns:
        assert (df["occupancy_mean"] > 0).all()
        assert (df["occupancy_mean"] < 1.5).all()


def test_pipeline_generate_report():
    """Verify that the validation report can be generated."""
    # This rule depends on others, snakemake will run them if needed.
    # We might want to ensure they run or at least that the report is produced.
    out_path = Path("reports/validation_report.md")
    out_path.unlink(missing_ok=True)

    result = run_snakemake("generate_report")

    assert result.returncode == 0
    assert out_path.exists()
    assert out_path.stat().st_size > 0
