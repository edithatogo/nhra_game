import pandas as pd
import pytest
from nhra_gt.visualization.trajectories import plot_trajectory
from nhra_gt.visualization.distributional import plot_strategy_heatmap
from nhra_gt.visualization.schemas import StrategyFrequencySchema

def test_plot_trajectory_missing_year():
    df = pd.DataFrame({"metric": [1, 2]})
    with pytest.raises(KeyError):
        plot_trajectory(df, "metric", "Label")

def test_plot_strategy_heatmap_invalid_shares():
    # StrategyFrequencySchema checks share ge=0, le=1
    df = pd.DataFrame({
        "year": [2025],
        "game": ["G1"],
        "strategy": ["S1"],
        "share": [1.5] # Invalid
    })
    with pytest.raises(Exception): # Pandera SchemaError
        StrategyFrequencySchema.validate(df)

def test_plot_strategy_heatmap_missing_cols():
    df = pd.DataFrame({"year": [2025]})
    with pytest.raises(KeyError):
        plot_strategy_heatmap(df)
