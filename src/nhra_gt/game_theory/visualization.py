"""Visualization logic for game theoretic structures (payoff matrices)."""

from __future__ import annotations

import plotly.graph_objects as go

from nhra_gt.game_theory.registry import GameDefinition


def generate_payoff_matrix_figure(game: GameDefinition) -> go.Figure:
    """Generates a Plotly figure representing the 2x2 payoff matrix of the game.

    Expects game.payoffs to have 'p1_strategies', 'p2_strategies', and 'matrix'.
    """
    payoffs = game.payoffs

    if "matrix" not in payoffs:
        return _generate_fallback_figure(game)

    p1_strats = payoffs.get("p1_strategies", ["Strategy 1", "Strategy 2"])
    p2_strats = payoffs.get("p2_strategies", ["Strategy A", "Strategy B"])
    matrix = payoffs["matrix"]

    fig = go.Figure()

    # Helper to format cell text in a cleaner (P1, P2) format to avoid overlap
    def fmt_cell(row: int, col: int) -> str:
        try:
            val = matrix[row][col]
            if isinstance(val, (list, tuple)) and len(val) == 2:
                # Use a cleaner (X, Y) notation which is standard for game theory matrices
                return f"({val[0]}, {val[1]})"
            return str(val)
        except IndexError:
            return "N/A"

    # Add a heatmap trace to provide the grid background
    fig.add_trace(
        go.Heatmap(
            z=[[0, 0], [0, 0]],
            x=p2_strats,
            y=p1_strats,
            colorscale=[[0, "#f8f9fa"], [1, "#f8f9fa"]],
            showscale=False,
            ygap=2,
            xgap=2,
        )
    )

    # Add text annotations
    for r, p1_s in enumerate(p1_strats):
        for c, p2_s in enumerate(p2_strats):
            text = fmt_cell(r, c)
            fig.add_annotation(
                x=p2_s, y=p1_s, text=text, showarrow=False, font={"size": 12, "color": "#212529"}
            )

    fig.update_layout(
        title=f"Payoff Matrix: {game.title}",
        xaxis_title=f"{game.players[1]} Strategies",
        yaxis_title=f"{game.players[0]} Strategies",
        yaxis={"autorange": "reversed"},
        margin={"l": 50, "r": 50, "t": 80, "b": 50},
        height=400,
        width=500,
        template="simple_white",
    )

    return fig


def _generate_fallback_figure(game: GameDefinition) -> go.Figure:
    """Fallback for simple key-value payoffs."""
    fig = go.Figure()
    fig.add_annotation(text="Detailed matrix data not available.", showarrow=False)
    fig.update_layout(title=game.title)
    return fig
