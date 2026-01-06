"""Registry for tracking and retrieving strategic subgame definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GameDefinition(BaseModel):
    """Complete definition of a subgame, including qualitative insights."""

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
    """In-memory store for game definitions."""

    def __init__(self) -> None:
        """Initialize an empty game registry."""
        self._games: dict[str, GameDefinition] = {}

    def register(self, game: GameDefinition) -> None:
        """Add a game definition to the registry."""
        self._games[game.id] = game

    def get(self, game_id: str) -> GameDefinition:
        """Retrieve a game definition by its unique ID."""
        if game_id not in self._games:
            raise KeyError(f"Game {game_id} not found")
        return self._games[game_id]

    def list_all(self) -> list[GameDefinition]:
        """Return all registered game definitions."""
        return list(self._games.values())
