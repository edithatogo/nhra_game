import pandas as pd
import pytest

from nhra_gt.visualization.distributional import plot_strategy_heatmap
from nhra_gt.visualization.trajectories import plot_trajectory


@pytest.fixture
def sample_trajectory_data():
    return pd.DataFrame({"year": [2025, 2026, 2027], "metric": [0.5, 0.6, 0.7]})


@pytest.fixture
def sample_strategy_data():
    return pd.DataFrame(
        {
            "year": [2025, 2025, 2026, 2026],
            "game": ["BARG", "BARG", "BARG", "BARG"],
            "strategy": ["Invest", "Shift", "Invest", "Shift"],
            "share": [0.8, 0.2, 0.7, 0.3],
        }
    )


@pytest.mark.mpl_image_compare(baseline_dir="baselines", tolerance=5)
def test_plot_trajectory_visual(sample_trajectory_data):
    return plot_trajectory(sample_trajectory_data, "metric", "Value")


@pytest.mark.mpl_image_compare(baseline_dir="baselines", tolerance=5)
def test_plot_strategy_heatmap_visual(sample_strategy_data):
    return plot_strategy_heatmap(sample_strategy_data)
