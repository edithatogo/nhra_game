from __future__ import annotations

import pandas as pd
import pytest

from nhra_gt.visualization.distributional import plot_distributions, plot_strategy_heatmap
from nhra_gt.visualization.trajectories import plot_trajectory


@pytest.fixture
def sample_traj():
    return pd.DataFrame(
        {
            "year": [2025, 2026, 2027],
            "metric": [0.5, 0.6, 0.7],
            "q_low": [0.4, 0.5, 0.6],
            "q_high": [0.6, 0.7, 0.8],
        }
    )


@pytest.fixture
def sample_strat():
    return pd.DataFrame(
        {
            "year": [2025, 2025, 2026, 2026],
            "game": ["BARG", "BARG", "BARG", "BARG"],
            "strategy": ["Invest", "Shift", "Invest", "Shift"],
            "share": [0.8, 0.2, 0.7, 0.3],
        }
    )


@pytest.mark.mpl_image_compare
def test_plot_trajectory_regression(sample_traj):
    return plot_trajectory(sample_traj, "metric", "Value", q_low_col="q_low", q_high_col="q_high")


@pytest.mark.mpl_image_compare
def test_plot_strategy_heatmap_regression(sample_strat):
    return plot_strategy_heatmap(sample_strat)


@pytest.mark.mpl_image_compare
def test_plot_distributions_regression(sample_traj):
    return plot_distributions(sample_traj, "metric")
