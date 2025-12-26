import pandas as pd
import pytest
import matplotlib.pyplot as plt
from pathlib import Path
from nhra_game_theory.visualization.config import PlotConfig
from nhra_game_theory.visualization.base import save_figure, Plotter

def test_plot_config_defaults():
    config = PlotConfig()
    assert config.dpi == 200
    assert config.primary_color == "#008080"
    assert len(config.color_palette) >= 3

def test_plot_config_custom():
    config = PlotConfig(dpi=300, primary_color="#FF0000")
    assert config.dpi == 300
    assert config.primary_color == "#FF0000"

def test_save_figure_smoke(tmp_path: Path):
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
    def my_plotter(data: pd.DataFrame, config: PlotConfig | None = None, **kwargs) -> plt.Figure:
        fig = plt.figure()
        return fig
    
    assert isinstance(my_plotter, Plotter)
