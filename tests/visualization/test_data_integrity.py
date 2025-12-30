from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError

from nhra_gt.visualization.distributional import plot_strategy_heatmap
from nhra_gt.visualization.trajectories import plot_trajectory


def test_plot_trajectory_missing_year():
    invalid_data = pd.DataFrame({"metric": [1.0, 2.0]})  # Missing 'year'

    with pytest.raises(SchemaError):
        plot_trajectory(invalid_data, "metric", "Y")


def test_plot_trajectory_wrong_type():
    invalid_data = pd.DataFrame({"year": ["abc"], "metric": [1.0]})

    # Pandera should try to coerce, but "abc" will fail

    with pytest.raises(SchemaError):
        plot_trajectory(invalid_data, "metric", "Y")


def test_plot_strategy_heatmap_invalid_share():
    invalid_data = pd.DataFrame(
        {
            "year": [2025],
            "game": ["BARG"],
            "strategy": ["Invest"],
            "share": [1.5],  # Invalid share (>1)
        }
    )

    with pytest.raises(SchemaError):
        plot_strategy_heatmap(invalid_data)
