"""Tests for robustness."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

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


@pytest.mark.parametrize("include_occupancy", [True, False], ids=["complete", "missing-occupancy"])
def test_pipeline_generate_report(tmp_path, include_occupancy):
    """Exercise the real report workflow with controlled synthetic observations."""
    source = Path(__file__).resolve().parents[2]
    shutil.copy2(source / "Snakefile", tmp_path)
    for directory in ("src", "workflow", "scripts"):
        shutil.copytree(
            source / directory, tmp_path / directory, ignore=shutil.ignore_patterns("__pycache__")
        )

    raw = tmp_path / "data/raw"
    raw.mkdir(parents=True)
    rows = []
    for offset in range(6):
        rows.append((2010 + offset, "Within 4 Hours", 0.62 + 0.009 * offset))
        if include_occupancy:
            rows.append((2010 + offset, "Occupancy", 0.85 - 0.002 * offset))
    pd.DataFrame(rows, columns=["Year", "Metric", "Value"]).to_csv(
        raw / "historical_aihw_ed.csv", index=False
    )

    gsa = tmp_path / "data/gsa"
    gsa.mkdir(parents=True)
    for artifact in ("morris_results.csv", "morris_tornado.png"):
        shutil.copy2(source / "data/gsa" / artifact, gsa / artifact)

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
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    report = tmp_path / "reports/validation_report.md"
    holdouts = tmp_path / "data/calibration/recursive_results.json"
    if not include_occupancy:
        assert result.returncode != 0
        assert "Historical observations require occupancy" in result.stdout + result.stderr
        assert not holdouts.exists()
        assert not report.exists()
        return

    assert result.returncode == 0, result.stderr
    assert holdouts.is_file()
    assert (
        (tmp_path / "outputs/validation/theil_decomposition.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )
    text = report.read_text(encoding="utf-8")
    assert "Mean RMSE criterion" in text
    assert "| within4 |" in text
    assert "| occupancy |" in text
