from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    fig.update_layout(
        template="simple_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    fig.update_traces(line=dict(width=3))
    return fig


def plot_what_if_overlay(
    baseline: pd.DataFrame,
    scenario: pd.DataFrame,
    metric: str,
    title: str,
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Standardizes what-if overlays with shaded confidence intervals if available.
    """
    if config is None:
        config = PlotConfig()

    fig = go.Figure()

    # Baseline line
    fig.add_trace(
        go.Scatter(
            x=baseline["year"],
            y=baseline[f"{metric}_mean"],
            name="Baseline",
            line=dict(color="#A9A9A9", width=2, dash="dash"),
        )
    )

    # Scenario line
    fig.add_trace(
        go.Scatter(
            x=scenario["year"],
            y=scenario[f"{metric}_mean"],
            name="Scenario",
            line=dict(color=config.primary_color, width=4),
        )
    )

    # Shaded ribbon for scenario p10-p90
    if f"{metric}_p10" in scenario.columns and f"{metric}_p90" in scenario.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([scenario["year"], scenario["year"][::-1]]),
                y=pd.concat([scenario[f"{metric}_p90"], scenario[f"{metric}_p10"][::-1]]),
                fill="toself",
                fillcolor=config.primary_color,
                opacity=0.2,
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=False,
                name="Scenario 90% CI",
            )
        )

    fig.update_layout(
        title=title,
        template="simple_white",
        hovermode="x unified",
        xaxis_title="Year",
        yaxis_title=metric.replace("_", " ").title(),
    )
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
        title="Stability Landscape: 0=Invest (Teal), 1=Shift (Rose)", template="simple_white"
    )
    return fig


def plot_vfi_waterfall(
    nominal_share: float,
    indexation_loss: float,
    cap_loss: float,
    audit_loss: float,
    effective_share: float,
    title: str = "VFI Funding Leakage (Waterfall)",
    config: PlotConfig | None = None,
) -> go.Figure:
    """
    Visualises the 'leakage' from nominal funding to effective share.
    """
    if config is None:
        config = PlotConfig()

    fig = go.Figure(
        go.Waterfall(
            name="Funding",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Nominal Share", "Indexation Gap", "Cap Limit", "Audit Clawback", "Effective Share"],
            textposition="outside",
            text=[
                f"{nominal_share*100:.1f}%",
                f"-{indexation_loss*100:.1f}%",
                f"-{cap_loss*100:.1f}%",
                f"-{audit_loss*100:.1f}%",
                f"{effective_share*100:.1f}%",
            ],
            y=[nominal_share, -indexation_loss, -cap_loss, -audit_loss, effective_share],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#FF4B4B"}},
            increasing={"marker": {"color": "#00CC96"}},
            totals={"marker": {"color": config.primary_color}},
        )
    )

    fig.update_layout(title=title, template="simple_white", showlegend=False)
    return fig


def plot_phase_space(
    traj: pd.DataFrame,
    x_col: str = "pressure_mean",
    y_col: str = "occupancy_mean",
    title: str = "System Phase-Space (Hysteresis Loop)",
) -> go.Figure:
    """
    Plots a 2D phase-space trajectory of the system state.
    """
    fig = px.line(
        traj,
        x=x_col,
        y=y_col,
        title=title,
        labels={x_col: "Pressure Index", y_col: "Occupancy"},
        hover_data=["year"],
    )

    # Add markers for start and end
    fig.add_trace(
        go.Scatter(
            x=[traj[x_col].iloc[0]],
            y=[traj[y_col].iloc[0]],
            mode="markers+text",
            name="Start",
            text=["Start"],
            textposition="top center",
            marker=dict(color="green", size=12),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[traj[x_col].iloc[-1]],
            y=[traj[y_col].iloc[-1]],
            mode="markers+text",
            name="End",
            text=["End"],
            textposition="top center",
            marker=dict(color="red", size=12),
        )
    )

    fig.update_layout(template="simple_white")
    return fig
