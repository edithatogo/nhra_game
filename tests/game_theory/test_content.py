from nhra_gt.game_theory.content import get_populated_registry


def test_core_games_existence():
    """Verify all 6 core games are populated."""
    registry = get_populated_registry()

    expected_ids = [
        "definition_game",
        "bargaining_game",
        "cost_shifting_game",
        "discharge_game",
        "governance_game",
        "compliance_game",
        "internal_lhn_competition",
        "electoral_game",
    ]

    for game_id in expected_ids:
        game = registry.get(game_id)
        assert game is not None
        assert game.id == game_id
        assert len(game.players) >= 2
        assert len(game.strategies) >= 2
        assert game.payoffs is not None
        assert game.nash_equilibrium != ""
        assert game.evidence_link != ""
        assert game.key_parameter != ""


def test_game_specific_content():
    """Spot check content for accuracy."""
    registry = get_populated_registry()

    # Check Definition Game details
    def_game = registry.get("definition_game")
    assert "Realism" in def_game.strategies or "Strictness" in def_game.strategies
    assert "Commonwealth" in def_game.players
    assert "State" in def_game.players
