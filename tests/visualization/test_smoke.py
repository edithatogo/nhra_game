import pandas as pd
import numpy as np
import pytest
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from nhra_game_theory.visualization.config import PlotConfig
from nhra_game_theory.visualization.trajectories import plot_trajectory
from nhra_game_theory.visualization.distributional import (
    plot_strategy_heatmap,
    plot_distributions,
    plot_pareto
)
from nhra_game_theory.visualization.sensitivity import (
    plot_sobol_indices,
    plot_sobol_heatmap,
    plot_morris_tornado,
    plot_rank_tornado
)
from nhra_game_theory.visualization.interactive import (
    plot_risk_pressure,
    plot_share_drift,
    plot_ghost_overlay,
    plot_stability_heatmap
)

@pytest.fixture
def sample_trajectory_data():
    return pd.DataFrame({
        "year": [2025, 2026, 2027],
        "metric": [0.5, 0.6, 0.7],
        "q_low": [0.4, 0.5, 0.6],
        "q_high": [0.6, 0.7, 0.8]
    })

@pytest.fixture
def sample_strategy_data():
    return pd.DataFrame({
        "year": [2025, 2025, 2026, 2026],
        "game": ["BARG", "BARG", "BARG", "BARG"],
        "strategy": ["Invest", "Shift", "Invest", "Shift"],
        "share": [0.8, 0.2, 0.7, 0.3]
    })

@pytest.fixture
def sample_sobol_data():
    return {
        "names": ["alpha", "beta"],
        "S1": [0.4, 0.5],
        "ST": [0.6, 0.7],
        "S1_conf": [0.05, 0.05],
        "ST_conf": [0.05, 0.05],
        "S2": np.array([[0, 0.1], [0.1, 0]])
    }

def test_plot_trajectory_smoke(sample_trajectory_data):
    fig = plot_trajectory(sample_trajectory_data, "metric", "Value", q_low_col="q_low", q_high_col="q_high")
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

def test_plot_sobol_indices_smoke(sample_sobol_data):
    fig = plot_sobol_indices(sample_sobol_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_sobol_heatmap_smoke(sample_sobol_data):
    fig = plot_sobol_heatmap(sample_sobol_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_morris_tornado_smoke():
    df = pd.DataFrame({
        "mu_star": [0.5, 0.8],
        "mu_star_conf": [0.1, 0.1]
    }, index=["p1", "p2"])
    fig = plot_morris_tornado(df)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_rank_tornado_smoke(sample_trajectory_data):
    sample_trajectory_data["p1"] = [1, 2, 3]
    fig = plot_rank_tornado(sample_trajectory_data, "metric", ["p1"])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_risk_pressure_smoke(sample_trajectory_data):
    sample_trajectory_data["Scenario"] = "Baseline"
    fig = plot_risk_pressure(sample_trajectory_data, "metric", "Title", "YLabel")
    assert isinstance(fig, go.Figure)

def test_plot_share_drift_smoke():
    df = pd.DataFrame({
        "year": [2025, 2026],
        "cth_nominal_mean": [0.45, 0.45],
        "cth_effective_mean": [0.42, 0.41]
    })
    fig = plot_share_drift(df, 0.4)
    assert isinstance(fig, go.Figure)

def test_plot_ghost_overlay_smoke():
    df = pd.DataFrame({
        "year": [2020, 2021],
        "value": [0.5, 0.52],
        "type": ["Historical", "Historical"]
    })
    fig = plot_ghost_overlay(df, "Metric")
    assert isinstance(fig, go.Figure)

def test_plot_stability_heatmap_smoke():
    df = pd.DataFrame([[0, 1], [1, 0]], columns=[0.1, 0.2], index=[0.8, 0.9])
    fig = plot_stability_heatmap(df)
    assert isinstance(fig, go.Figure)
