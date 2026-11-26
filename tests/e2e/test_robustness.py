"""Tests for robustness."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

_FIRST_SCENARIO_YEAR = 2020
_LAST_SCENARIO_YEAR = 2040
_MAX_OCCUPANCY = 1.5


def test_pipeline_gsa_morris():
    """Verify that the GSA Morris rule runs and produces expected output."""
    out_path = Path("data/gsa/morris_results.csv")
    out_path.unlink(missing_ok=True)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "snakemake",
            "--cores",
            "1",
            "gsa_morris",
            "--printshellcmds",
            "--show-failed-logs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
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
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "snakemake",
            "--cores",
            "1",
            "calibrate",
            "--printshellcmds",
            "--show-failed-logs",
        ],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "NHRA_CALIBRATION_TRIALS": "1"},
    )

    assert result.returncode == 0, result.stderr
    assert out_path.exists()

    df = pd.read_csv(out_path)
    assert not df.empty
    assert "best_value" in df.columns


def test_pipeline_baseline_integrity():
    """Verify that the baseline trajectory contains plausible data."""
    out_path = Path("data/baseline/tables/trajectory.csv")
    # Rule might have already run, or we run it
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "snakemake",
            "--cores",
            "1",
            "run_baseline",
            "--printshellcmds",
            "--show-failed-logs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert out_path.exists()
    df = pd.read_csv(out_path)

    assert result.returncode == 0, result.stderr

    # Check years
    assert df["year"].min() >= _FIRST_SCENARIO_YEAR
    assert df["year"].max() <= _LAST_SCENARIO_YEAR

    # Check within4_mean (share should be 0-1)
    if "within4_mean" in df.columns:
        assert df["within4_mean"].between(0, 1).all()

    # Check occupancy (should be positive and generally < 1.1)
    if "occupancy_mean" in df.columns:
        assert (df["occupancy_mean"] > 0).all()
        assert (df["occupancy_mean"] < _MAX_OCCUPANCY).all()


def test_pipeline_generate_report():
    """Verify that the validation report can be generated."""
    # This rule depends on others, snakemake will run them if needed.
    # We might want to ensure they run or at least that the report is produced.
    out_path = Path("reports/validation_report.md")
    out_path.unlink(missing_ok=True)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "snakemake",
            "--cores",
            "1",
            "generate_report",
            "--printshellcmds",
            "--show-failed-logs",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert out_path.exists()
    assert out_path.stat().st_size > 0
