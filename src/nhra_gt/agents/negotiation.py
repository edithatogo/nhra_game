from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nhra_game_theory.agents.base import Agent
    from nhra_game_theory.engine import Params, State


class DebateLoop:
    """
    Manages a structured negotiation between two agents.
    """

    def __init__(self, agent_a: Agent, agent_b: Agent, max_rounds: int = 3):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.max_rounds = max_rounds

    def negotiate(self, state: State, params: Params, rng: Any) -> tuple[dict[str, Any], list[str]]:
        """
        Runs the debate loop and returns final strategies and the transcript.
        """
        transcript = []
        transcript.append("--- BEGIN NEGOTIATION ---")

        # Round 1: Initial Positions
        move_a = self.agent_a.decide(state, params, rng)
        move_b = self.agent_b.decide(state, params, rng)

        transcript.append(f"Agent A ({move_a.get('RATIONALE', 'No rationale')})")
        transcript.append(f"Agent B ({move_b.get('RATIONALE', 'No rationale')})")

        # Subsequent rounds would involve 'persuasion' if we had a full LLM loop
        # For now, we resolve the joint move using the standard combination rules

        final_strategies = {}
        # Simple merging (State usually takes precedence on internal ops, Cth on funding terms)
        final_strategies.update(move_a)
        final_strategies.update(move_b)

        transcript.append("--- END NEGOTIATION ---")
        return final_strategies, transcript
