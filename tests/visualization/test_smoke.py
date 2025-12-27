import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from nhra_gt.visualization.distributional import (
    plot_cdf,
    plot_comparison_bar,
    plot_distributions,
    plot_pareto,
    plot_strategy_heatmap,
)
from nhra_gt.visualization.interactive import (
    plot_ghost_overlay,
    plot_risk_pressure,
    plot_share_drift,
    plot_stability_heatmap,
)
from nhra_gt.visualization.sensitivity import (
    plot_morris_tornado,
    plot_rank_tornado,
    plot_sobol_heatmap,
    plot_sobol_indices,
)
from nhra_gt.visualization.trajectories import (
    plot_comparison_trajectory,
    plot_trajectory,
)


@pytest.fixture
def sample_trajectory_data():
    return pd.DataFrame(
        {
            "year": [2025, 2026, 2027, 2025, 2026, 2027],
            "metric": [0.5, 0.6, 0.7, 0.4, 0.45, 0.5],
            "q_low": [0.4, 0.5, 0.6, 0.3, 0.35, 0.4],
            "q_high": [0.6, 0.7, 0.8, 0.5, 0.55, 0.6],
            "Scenario": ["A", "A", "A", "B", "B", "B"],
        }
    )


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


@pytest.fixture
def sample_sobol_data():
    return {
        "names": ["alpha", "beta"],
        "S1": [0.4, 0.5],
        "ST": [0.6, 0.7],
        "S1_conf": [0.05, 0.05],
        "ST_conf": [0.05, 0.05],
        "S2": np.array([[0, 0.1], [0.1, 0]]),
    }


def test_plot_trajectory_smoke(sample_trajectory_data):
    sub = sample_trajectory_data[sample_trajectory_data["Scenario"] == "A"]
    fig = plot_trajectory(sub, "metric", "Value", q_low_col="q_low", q_high_col="q_high")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_comparison_trajectory_smoke(sample_trajectory_data):
    fig = plot_comparison_trajectory(sample_trajectory_data, "metric", "Value")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_strategy_heatmap_smoke(sample_strategy_data):
    fig = plot_strategy_heatmap(sample_strategy_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_distributions_smoke(sample_trajectory_data):
    fig = plot_distributions(sample_trajectory_data, "metric")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_pareto_smoke(sample_trajectory_data):
    fig = plot_pareto(sample_trajectory_data, "metric", "q_low", label_col="year")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_comparison_bar_smoke(sample_trajectory_data):
    fig = plot_comparison_bar(sample_trajectory_data, "Scenario", "metric", "Title", "Y")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_cdf_smoke(sample_trajectory_data):
    fig = plot_cdf(sample_trajectory_data, value_col="metric")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_sobol_indices_smoke(sample_sobol_data):
    fig = plot_sobol_indices(sample_sobol_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_sobol_heatmap_smoke(sample_sobol_data):
    fig = plot_sobol_heatmap(sample_sobol_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_morris_tornado_smoke():
    df = pd.DataFrame({"mu_star": [0.5, 0.8], "mu_star_conf": [0.1, 0.1]}, index=["p1", "p2"])
    fig = plot_morris_tornado(df)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_rank_tornado_smoke(sample_trajectory_data):
    sample_trajectory_data["p1"] = [1, 2, 3, 4, 5, 6]
    fig = plot_rank_tornado(sample_trajectory_data, "metric", ["p1"])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_risk_pressure_smoke(sample_trajectory_data):
    sample_trajectory_data["Scenario"] = "Baseline"
    fig = plot_risk_pressure(sample_trajectory_data, "metric", "Title", "YLabel")
    assert isinstance(fig, go.Figure)


def test_plot_share_drift_smoke():
    df = pd.DataFrame(
        {"year": [2025, 2026], "cth_nominal_mean": [0.45, 0.45], "cth_effective_mean": [0.42, 0.41]}
    )
    fig = plot_share_drift(df, 0.4)
    assert isinstance(fig, go.Figure)


def test_plot_ghost_overlay_smoke():
    df = pd.DataFrame(
        {"year": [2020, 2021], "value": [0.5, 0.52], "type": ["Historical", "Historical"]}
    )
    fig = plot_ghost_overlay(df, "Metric")
    assert isinstance(fig, go.Figure)


def test_plot_stability_heatmap_smoke():
    df = pd.DataFrame([[0, 1], [1, 0]], columns=[0.1, 0.2], index=[0.8, 0.9])
    fig = plot_stability_heatmap(df)
    assert isinstance(fig, go.Figure)
