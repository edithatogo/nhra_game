"""
Central Registry for Game-Theoretic Mechanism Definitions.

Stores metadata, strategies, and qualitative insights for all NHRA subgames.
"""

from typing import Any

from pydantic import BaseModel


class GameDefinition(BaseModel):
    """
    Complete definition of a subgame, including qualitative insights.
    """

    id: str
    title: str
    players: list[str]
    strategies: list[str]
    # Flexible dict to accommodate various payoff structures (simple dict or complex matrix)
    payoffs: dict[str, Any]
    nash_equilibrium: str
    strategic_insight: str
    evidence_link: str
    key_parameter: str


class GameRegistry:
    """
    In-memory store for game definitions.
    """

    def __init__(self) -> None:
        self._games: dict[str, GameDefinition] = {}

    def register(self, game: GameDefinition) -> None:
        self._games[game.id] = game

    def get(self, game_id: str) -> GameDefinition:
        if game_id not in self._games:
            raise KeyError(f"Game {game_id} not found")
        return self._games[game_id]

    def list_all(self) -> list[GameDefinition]:
        return list(self._games.values())
