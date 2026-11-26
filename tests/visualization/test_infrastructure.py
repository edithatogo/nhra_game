"""Tests for infrastructure."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from nhra_gt.visualization.base import Plotter, save_figure
from nhra_gt.visualization.config import PlotConfig

_DEFAULT_RESOLUTION = 200
_MIN_PALETTE_COLORS = 3
_OVERRIDE_RESOLUTION = 300


def test_plot_config_defaults():
    """Check plot config defaults."""
    config = PlotConfig()
    assert config.dpi == _DEFAULT_RESOLUTION
    assert config.primary_color == "#008080"
    assert len(config.color_palette) >= _MIN_PALETTE_COLORS


def test_plot_config_custom():
    """Check plot config custom."""
    config = PlotConfig(dpi=300, primary_color="#FF0000")
    assert config.dpi == _OVERRIDE_RESOLUTION
    assert config.primary_color == "#FF0000"


def test_save_figure_smoke(tmp_path: Path):
    """Check save figure smoke."""
    config = PlotConfig(format="png")
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])

    out_path = tmp_path / "test_plot"
    save_figure(fig, out_path, config)

    expected_path = tmp_path / "test_plot.png"
    assert expected_path.exists()
    assert expected_path.stat().st_size > 0


def test_plotter_protocol_compliance():
    # Verify that a function matching the signature complies with the Protocol
    """Check plotter protocol compliance."""

    def my_plotter(data: pd.DataFrame, config: PlotConfig | None = None, **_kwargs) -> plt.Figure:
        assert isinstance(data, pd.DataFrame)
        assert config is None or isinstance(config, PlotConfig)
        return plt.figure()

    assert isinstance(my_plotter, Plotter)
