from unittest.mock import MagicMock, patch

from nhra_gt.game_theory.registry import GameDefinition, GameRegistry
from nhra_gt.game_theory.ui import render_mechanism_explainer


def test_explainer_rendering():
    """Test mechanism explainer rendering."""
    mock_registry = MagicMock(spec=GameRegistry)
    mock_game = GameDefinition(
        id="test_game",
        title="Test Game",
        players=["A"],
        strategies=["S"],
        payoffs={},
        nash_equilibrium="None",
        strategic_insight="Insight",
        evidence_link="",
        key_parameter="",
    )
    mock_registry.get.return_value = mock_game

    with patch("streamlit.expander") as mock_expander:
        render_mechanism_explainer("test_game", mock_registry)
        mock_registry.get.assert_called_with("test_game")
        mock_expander.assert_called()
