"""Tests for recursive backtest."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest
from scripts.validation import (
    generate_validation_report,
    plot_theil_decomposition,
    recursive_backtest,
)

# We'll implement this in Phase 2/3
from nhra_gt.domain.validation import RecursiveBacktest, RecursiveResult
from nhra_gt.engine import Params

_WINDOW_COUNT = 3
_INVALID_INPUT_EXIT = 2
_FIRST_TEST_YEAR = 2013
_FIRST_PREDICTION = 0.66
_FIRST_ACTUAL = 0.65


@pytest.fixture
def mock_historical_data():
    """Provide the historical data used in the backtest fixture."""
    return pd.DataFrame(
        {
            "year": [2011, 2012, 2013, 2014, 2015],
            "within4": [0.70, 0.68, 0.65, 0.60, 0.55],
            "occupancy": [0.85, 0.86, 0.88, 0.90, 0.92],
        }
    )


def test_recursive_backtest_windowing(mock_historical_data):
    """Verify that the backtest correctly windows the historical data."""
    # Train on 2 years, test on 1
    engine = RecursiveBacktest(historical_data=mock_historical_data, train_window=2, test_window=1)

    # Windows should be:
    # 1. Train: [2011, 2012], Test: 2013
    # 2. Train: [2012, 2013], Test: 2014
    # 3. Train: [2013, 2014], Test: 2015

    windows = list(engine.generate_windows())
    assert len(windows) == _WINDOW_COUNT

    train_0, test_0 = windows[0]
    assert train_0["year"].tolist() == [2011, 2012]
    assert test_0["year"].tolist() == [2013]


@patch("nhra_gt.domain.validation.run_hybrid")
def test_recursive_backtest_step(mock_run, mock_historical_data):
    """Verify that a single step of the backtest produces a RecursiveResult."""

    # Mock run_hybrid to return a trajectory matching the year
    def side_effect(years, *_args, **_kwargs):
        return pd.DataFrame(
            {
                "year": years,
                "within4_mean": [0.66] * len(years),
                "occupancy_mean": [0.87] * len(years),
            }
        ), None

    mock_run.side_effect = side_effect

    engine = RecursiveBacktest(historical_data=mock_historical_data, train_window=2)

    train_df = mock_historical_data.iloc[:2]
    test_df = mock_historical_data.iloc[2:3]

    result = engine.run_step(train_df, test_df)

    assert isinstance(result, RecursiveResult)
    assert result.test_year == _FIRST_TEST_YEAR
    assert result.predicted["within4"] == _FIRST_PREDICTION
    assert result.actual["within4"] == _FIRST_ACTUAL


def test_recursive_backtest_full_loop(mock_historical_data):
    """Verify that the full loop aggregates results correctly."""
    with patch.object(RecursiveBacktest, "run_step") as mock_step:
        mock_step.return_value = RecursiveResult(
            test_year=2013, predicted={"within4": 0.66}, actual={"within4": 0.65}, params=Params()
        )

        engine = RecursiveBacktest(mock_historical_data, train_window=2)
        all_results = engine.run_all()

        assert len(all_results) == _WINDOW_COUNT
        assert all_results[0].test_year == _FIRST_TEST_YEAR


def test_command_requires_observed_occupancy(tmp_path, monkeypatch, capsys, mock_historical_data):
    """Missing occupancy fails the backtest and produces no validation outputs."""
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "data/calibration"
    output.mkdir(parents=True)
    mock_historical_data.drop(columns="occupancy").to_csv(
        output / "historical_normalized.csv", index=False
    )
    assert recursive_backtest.main() == _INVALID_INPUT_EXIT
    assert "occupancy" in capsys.readouterr().err
    assert not (output / "recursive_results.json").exists()


def test_validation_commands_use_the_expected_output_paths(tmp_path, monkeypatch):
    """Synthetic holdouts exercise the backtest, figure and report entry points."""

    def simulate(*, years, **_settings):
        offsets = [year - 2010 for year in years]
        return pd.DataFrame(
            {
                "year": years,
                "within4_mean": [0.67 + 0.004 * offset for offset in offsets],
                "occupancy_mean": [0.83 + 0.003 * offset for offset in offsets],
            }
        ), None

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("nhra_gt.domain.validation.run_hybrid", simulate)
    output = tmp_path / "data/calibration"
    output.mkdir(parents=True)
    offsets = range(9)
    pd.DataFrame(
        {
            "year": [2010 + offset for offset in offsets],
            "within4": [0.62 + 0.009 * offset for offset in offsets],
            "occupancy": [0.85 - 0.002 * offset for offset in offsets],
        }
    ).to_csv(output / "historical_normalized.csv", index=False)

    assert recursive_backtest.main() == 0
    assert plot_theil_decomposition.main() == 0
    assert generate_validation_report.main() == 0
    assert (output / "recursive_results.json").is_file()
    figure = tmp_path / "outputs/validation/theil_decomposition.png"
    assert figure.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    report = (tmp_path / "reports/validation_report.md").read_text(encoding="utf-8")
    assert "Mean RMSE criterion" in report
    assert "default model parameters" in report
    assert "- [x]" not in report
