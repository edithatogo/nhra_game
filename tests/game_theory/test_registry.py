import pytest

from nhra_gt.game_theory.registry import GameDefinition, GameRegistry


def test_game_definition_structure():
    """Test that GameDefinition has all required fields."""
    game = GameDefinition(
        id="test_game",
        title="Test Game",
        players=["P1", "P2"],
        strategies=["Cooperate", "Defect"],
        payoffs={"P1": {"Cooperate": 1, "Defect": 0}},
        nash_equilibrium="Both Defect",
        strategic_insight="Classical Prisoner's Dilemma",
        evidence_link="Senate Inquiry 2024",
        key_parameter="Trust Factor",
    )

    assert game.id == "test_game"
    assert game.title == "Test Game"
    assert len(game.players) == 2
    assert game.evidence_link == "Senate Inquiry 2024"


def test_registry_storage_and_retrieval():
    """Test standard registry operations."""
    registry = GameRegistry()

    game = GameDefinition(
        id="bargaining",
        title="Bargaining Game",
        players=["Federal", "State"],
        strategies=["Agree", "Defer"],
        payoffs={},
        nash_equilibrium="Defer",
        strategic_insight="Wait for better deal",
        evidence_link="Report X",
        key_parameter="Discount Rate",
    )

    registry.register(game)

    retrieved = registry.get("bargaining")
    assert retrieved is not None
    assert retrieved.title == "Bargaining Game"

    with pytest.raises(KeyError):
        registry.get("non_existent")


def test_registry_get_all():
    """Test retrieving all games."""
    registry = GameRegistry()
    registry.register(
        GameDefinition(
            id="g1",
            title="G1",
            players=[],
            strategies=[],
            payoffs={},
            nash_equilibrium="",
            strategic_insight="",
            evidence_link="",
            key_parameter="",
        )
    )
    registry.register(
        GameDefinition(
            id="g2",
            title="G2",
            players=[],
            strategies=[],
            payoffs={},
            nash_equilibrium="",
            strategic_insight="",
            evidence_link="",
            key_parameter="",
        )
    )

    all_games = registry.list_all()
    assert len(all_games) == 2
    assert all_games[0].id == "g1"
