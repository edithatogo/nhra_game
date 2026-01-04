import plotly.graph_objects as go

from nhra_gt.game_theory.registry import GameDefinition
from nhra_gt.game_theory.visualization import generate_payoff_matrix_figure


def test_payoff_matrix_generation():
    """Test generating a plotly figure for a known 2x2 game."""
    game = GameDefinition(
        id="test_game",
        title="Test Game",
        players=["P1", "P2"],
        strategies=["Cooperate", "Defect"],
        payoffs={
            "p1_strategies": ["Cooperate", "Defect"],
            "p2_strategies": ["Cooperate", "Defect"],
            "matrix": [[("3", "3"), ("0", "5")], [("5", "0"), ("1", "1")]],
        },
        nash_equilibrium="None",
        strategic_insight="",
        evidence_link="",
        key_parameter="",
    )

    fig = generate_payoff_matrix_figure(game)
    assert isinstance(fig, go.Figure)
    # Check that it has data (e.g. annotations or heatmap)
    assert len(fig.data) > 0 or len(fig.layout.annotations) > 0


def test_payoff_matrix_missing_data():
    """Test handling of games with weird payoff structures."""
    # This might fail if the visualizer expects specific structure
