from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Any

from .config import PlotConfig


def plot_risk_pressure(
    combined_data: pd.DataFrame,
    y_col: str,
    title: str,
    ylabel: str,
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Plots a dual-line comparison (usually Baseline vs Scenario) for risk or pressure.
    """
    if config is None:
        config = PlotConfig()

    fig = px.line(
        combined_data,
        x="year",
        y=y_col,
        color="Scenario",
        title=title,
        labels={y_col: ylabel, "year": "Year"},
        color_discrete_map={
            "Baseline": "#A9A9A9",
            "Strategic Scenario Analysis": config.primary_color,
        },
    )
    fig.update_layout(template="simple_white", hovermode="x unified")
    return fig


def plot_share_drift(
    drift_df: pd.DataFrame,
    threshold: float,
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Plots Nominal vs Effective Commonwealth Share with a threshold line.
    """
    if config is None:
        config = PlotConfig()

    fig = px.line(
        drift_df,
        x="year",
        y=["cth_nominal_mean", "cth_effective_mean"],
        title="Nominal vs Effective Commonwealth Share",
        labels={"value": "Share", "year": "Year", "variable": "Type"},
        color_discrete_map={
            "cth_nominal_mean": "blue",
            "cth_effective_mean": "red",
        },
    )
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Threshold {threshold:.0%}",
    )
    fig.update_layout(template="simple_white")
    return fig


def plot_ghost_overlay(
    overlay_df: pd.DataFrame,
    metric_name: str,
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Plots historical data vs model backtest predictions.
    """
    if config is None:
        config = PlotConfig()

    fig = px.line(
        overlay_df,
        x="year",
        y="value",
        color="type",
        title=f"Forecasting Check: {metric_name} (Ghost Overlay)",
        color_discrete_map={
            "Historical": config.primary_color,
            "Backtest Prediction": "#FF7F50",
        },
    )
    fig.update_layout(template="simple_white", hovermode="x unified")
    return fig


def plot_stability_heatmap(
    pivot_table: pd.DataFrame,
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Plots a heatmap of Nash Equilibrium stability regions.
    """
    if config is None:
        config = PlotConfig()

    fig = px.imshow(
        pivot_table,
        labels={
            "x": "Cost Shifting Intensity",
            "y": "Pressure Index",
            "color": "Strategy",
        },
        x=pivot_table.columns,
        y=pivot_table.index,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        title="Stability Landscape: 0=Invest (Teal), 1=Shift (Rose)",
        template="simple_white"
    )
    return fig
