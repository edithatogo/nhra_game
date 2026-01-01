import plotly.graph_objects as go

from nhra_gt.game_theory.registry import GameDefinition


def generate_payoff_matrix_figure(game: GameDefinition) -> go.Figure:
    """
    Generates a Plotly figure representing the 2x2 payoff matrix of the game.
    Expects game.payoffs to have 'p1_strategies', 'p2_strategies', and 'matrix'.
    """
    payoffs = game.payoffs

    # Fallback for simple structure (if legacy data exists)
    if "matrix" not in payoffs:
        return _generate_fallback_figure(game)

    p1_strats = payoffs.get("p1_strategies", ["Strategy 1", "Strategy 2"])
    p2_strats = payoffs.get("p2_strategies", ["Strategy A", "Strategy B"])
    matrix = payoffs["matrix"]

    # cell texts
    # Matrix is [[(r1c1_1, r1c1_2), (r1c2_1, r1c2_2)], ...]

    # We want to display a 2x2 grid.
    # Plotly Heatmap or Table?
    # Heatmap is good for coloring, but we have text tuples.
    # Annotations on a blank heatmap is standard for game theory docs.

    fig = go.Figure()

    # Create a 2x2 grid using shapes or heatmap
    # Z values for coloring? Maybe uniform or based on nash?
    # Let's just use a light grey background.

    # We can use a Table for strict layout, but a "Matrix" look is usually a square.

    # Helper to format cell text
    def fmt_cell(row: int, col: int) -> str:
        try:
            val = matrix[row][col]
            if isinstance(val, (list, tuple)) and len(val) == 2:
                return f"<b>{game.players[0]}:</b> {val[0]}<br><b>{game.players[1]}:</b> {val[1]}"
            return str(val)
        except IndexError:
            return "N/A"

    # Coordinates: x=0 (Col 1), x=1 (Col 2). y=1 (Row 1), y=0 (Row 2) (Plotly y is bottom-up usually, but we can reverse)

    # Let's use x=[0.5, 1.5], y=[1.5, 0.5] mapped to cells.

    fig.add_trace(
        go.Heatmap(
            z=[[0, 0], [0, 0]],
            x=p2_strats,
            y=p1_strats,  # Note: y order matters
            colorscale="Greys",
            showscale=False,
            ygap=2,
            xgap=2,
        )
    )

    # Add text annotations
    for r, p1_s in enumerate(p1_strats):
        for c, p2_s in enumerate(p2_strats):
            # Plotly Heatmap y-axis is bottom-to-top by default unless reversed?
            # Actually standard heatmap: y[0] is bottom.
            # We want matrix style: Row 0 is Top.
            # So we should reverse y-axis.

            text = fmt_cell(r, c)
            fig.add_annotation(x=p2_s, y=p1_s, text=text, showarrow=False, font={"size": 14})

    fig.update_layout(
        title=f"Payoff Matrix: {game.title}",
        xaxis_title=f"{game.players[1]} Strategies",
        yaxis_title=f"{game.players[0]} Strategies",
        yaxis={"autorange": "reversed"},  # Top row is first
    )

    return fig


def _generate_fallback_figure(game: GameDefinition) -> go.Figure:
    """Fallback for simple key-value payoffs."""
    fig = go.Figure()
    fig.add_annotation(text="Detailed matrix data not available.", showarrow=False)
    fig.update_layout(title=game.title)
    return fig
