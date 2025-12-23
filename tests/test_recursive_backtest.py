from __future__ import annotations

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from nhra_game_theory.v9 import Params

# We'll implement this in Phase 2/3
from nhra_game_theory.domain.validation import RecursiveBacktest, RecursiveResult

@pytest.fixture
def mock_historical_data():
    return pd.DataFrame({
        "year": [2011, 2012, 2013, 2014, 2015],
        "within4": [0.70, 0.68, 0.65, 0.60, 0.55],
        "occupancy": [0.85, 0.86, 0.88, 0.90, 0.92]
    })

def test_recursive_backtest_windowing(mock_historical_data):
    """Verify that the backtest correctly windows the historical data."""
    # Train on 2 years, test on 1
    engine = RecursiveBacktest(
        historical_data=mock_historical_data,
        train_window=2,
        test_window=1
    )
    
    # Windows should be:
    # 1. Train: [2011, 2012], Test: 2013
    # 2. Train: [2012, 2013], Test: 2014
    # 3. Train: [2013, 2014], Test: 2015
    
    windows = list(engine.generate_windows())
    assert len(windows) == 3
    
    train_0, test_0 = windows[0]
    assert train_0["year"].tolist() == [2011, 2012]
    assert test_0["year"].tolist() == [2013]

@patch("nhra_game_theory.domain.validation.run_hybrid")
def test_recursive_backtest_step(mock_run, mock_historical_data):
    """Verify that a single step of the backtest produces a RecursiveResult."""
    # Mock run_hybrid to return a trajectory matching the year
    def side_effect(years, p, seed, n_mc):
        return pd.DataFrame({
            "year": years,
            "within4_mean": [0.66] * len(years),
            "occupancy_mean": [0.87] * len(years)
        }), None
    
    mock_run.side_effect = side_effect
    
    engine = RecursiveBacktest(
        historical_data=mock_historical_data,
        train_window=2
    )
    
    train_df = mock_historical_data.iloc[:2]
    test_df = mock_historical_data.iloc[2:3]
    
    result = engine.run_step(train_df, test_df)
    
    assert isinstance(result, RecursiveResult)
    assert result.test_year == 2013
    assert result.predicted["within4"] == 0.66
    assert result.actual["within4"] == 0.65

def test_recursive_backtest_full_loop(mock_historical_data):
    """Verify that the full loop aggregates results correctly."""
    with patch.object(RecursiveBacktest, "run_step") as mock_step:
        mock_step.return_value = RecursiveResult(
            test_year=2013,
            predicted={"within4": 0.66},
            actual={"within4": 0.65},
            params=Params()
        )
        
        engine = RecursiveBacktest(mock_historical_data, train_window=2)
        all_results = engine.run_all()
        
        assert len(all_results) == 3
        assert all_results[0].test_year == 2013
