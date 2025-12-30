from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from nhra_gt.engine import Params, State


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def softmax(u: np.ndarray, tau: float = 0.25) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    u = u - u.max()
    z = np.exp(u / max(1e-9, tau))
    return np.asarray(z / z.sum(), dtype=float)


class Agent(ABC):
    """Abstract base class for all NHRA strategic agents."""

    @abstractmethod
    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Choose strategies based on current system state.

        Args:
            state: The current simulation state (pressure, funds, etc.).
            params: The simulation parameters and configuration.
            rng: A random number generator seeded for this rollout.

        Returns:
            A dictionary of strategic choices (e.g., {"DEF": "E", "BARG": "A"}).
        """
        pass


class BriefGenerator:
    """Converts simulation state into a textual narrative for LLM consumption."""

    @staticmethod
    def generate(state: State, params: Params, role: str) -> str:
        """Generate a policy brief for a specific role (Commonwealth/State/Provider).

        Converts quantitative state metrics into a qualitative textual narrative
        suitable for LLM consumption.

        Args:
            state: Current simulation state.
            params: System parameters.
            role: The role to generate the brief for (e.g., "State Health Dept").

        Returns:
            A formatted markdown string containing the policy brief.
        """
        mode_desc = {
            "normal": "The system is currently stable.",
            "stress": "The system is under significant pressure.",
            "crisis": "CRITICAL: The system is in a state of failure (Code Red).",
            "recovery": "The system is recovering from a crisis.",
        }

        brief = f"""
### NHRA POLICY BRIEF - {role.upper()}
**Current Year:** {state.year}, Month {state.month}
**System Mode:** {state.system_mode.value.upper()} - {mode_desc.get(state.system_mode.value, "")}

**Key Metrics:**
- System Pressure: {state.pressure:.2f} (Base: 1.0)
- ED Wait Time: {state.within4 * 100:.1f}% within 4h
- Efficiency Gap: {state.efficiency_gap * 100:.1f}% (Cost vs NEP)
- Effective Cth Share: {state.effective_cth_share * 100:.1f}%
- Political Capital: {state.political_capital:.2f}
- Equity Index: {state.equity_index:.2f}

**Strategic Context:**
- Your goal is to maximize your utility while maintaining system stability.
- Agreement (A) restores trust but may increase bailout expectations.
- Upcoding (U) increases revenue but risks Auditor detection and penalties.
- Fragmentation (F) in Aged Care/NDIS reduces your immediate load but worsens downstream pressure.

**Decision Required:**
You must choose strategies for the current period.
"""
        return brief


class AuditorValidator:
    """
    Evaluates agent strategic traces from an 'Auditor' perspective.
    Scores realism and detects unlikely gaming behavior.
    """

    def validate(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        """Evaluates agent strategic traces from an 'Auditor' perspective.

        Scores realism and detects unlikely gaming behavior.

        Args:
            trace: A list of step dictionaries containing state, strategy, and rationale.

        Returns:
            A dictionary with keys `realism_score` (float) and `findings` (list of str).
        """
        # Logic would involve an LLM prompt: "Does this look like a real hospital administrator?"
        # For now, return a placeholder score.
        return {
            "realism_score": 0.85,
            "findings": ["Gaming behavior consistent with high pressure periods."],
        }


class LLMAgent(Agent):
    """
    An agent that uses a Large Language Model to make strategic decisions.
    """

    def __init__(self, role: str, model_name: str = "gemini-pro"):
        self.role = role
        self.model_name = model_name
        self.brief_gen = BriefGenerator()

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """
        Generates a brief, calls the LLM, and parses the strategic response.
        Note: Actual LLM call is stubbed/delegated to the environment.
        """
        self.brief_gen.generate(state, params, self.role)

        # In a real implementation, we would call the LLM here.
        # For the simulation engine, we can use a callback or a mock
        # that uses the HeuristicAgent as a 'smart fallback'.

        # MOCK/STUB logic for now:
        heuristic_response = CommonwealthAgent().decide(state, params, rng)
        heuristic_response.update(JurisdictionAgent().decide(state, params, rng))
        heuristic_response.update(LHNAgent().decide(state, params, rng))

        # Add 'Rationale' for Cognitive Trace
        heuristic_response["RATIONALE"] = (
            f"Decided based on multi-agent refactor for {self.role}. Pressure is {state.pressure:.2f}."
        )

        return heuristic_response


class CommonwealthAgent(Agent):
    """The Principal (Federal Govt) setting price and compliance rules."""

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = getattr(state, "reported_efficiency_gap", state.efficiency_gap)

        # Commonwealth moves: DEF, COMP, BARG(offer)
        results = {}

        # 1. Compliance Strategy (COMP)
        comp_prob = logistic(0.9 * params.audit_pressure - 0.7 * obs_efficiency_gap)
        results["COMP"] = "T" if rng.random() < comp_prob else "L"

        # 2. Framing Strategy (DEF)
        def_prob = logistic(1.3 * (obs_efficiency_gap - 0.25) + 0.9 * (obs_pressure - 1.0))
        results["DEF"] = "R" if rng.random() < def_prob else "E"

        return results


class JurisdictionAgent(Agent):
    """The Intermediary (State/Territory Govt) managing the Agreement."""

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = getattr(state, "reported_efficiency_gap", state.efficiency_gap)

        # State moves: BARG, SHIFT, GOV
        results = {}

        # 1. Bargaining Strategy (BARG)
        barg_prob = logistic(0.6 * (1.2 - obs_pressure) + state.bailout_expectation)
        results["BARG"] = "A" if rng.random() < barg_prob else "D"

        # 2. Cost Shifting (SHIFT)
        shift_prob = logistic(-1.1 * (obs_pressure - 1.0) - 1.0 * obs_efficiency_gap)
        results["SHIFT"] = "I" if rng.random() < shift_prob else "S"

        # 3. Governance (GOV)
        gov_prob = logistic(-0.8 * (obs_pressure - 1.0) - 0.7 * params.political_salience)
        results["GOV"] = "I" if rng.random() < gov_prob else "S"

        return results


class LHNAgent(Agent):
    """The Operator (Hospital/LHN) managing clinical demand and revenue."""

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = getattr(state, "reported_efficiency_gap", state.efficiency_gap)

        # LHN moves: CODING, VENUE_SHIFT, DISC, AGED, NDIS, COMPETITION
        results = {}

        # 1. Revenue Strategy (CODING)
        coding_prob = logistic(1.5 * (obs_pressure - 1.1) + 1.2 * obs_efficiency_gap)
        results["CODING"] = "U" if rng.random() < coding_prob else "H"

        # 2. Venue Selection (VENUE_SHIFT)
        venue_prob = logistic(1.2 * (obs_pressure - 1.1) + 0.8 * obs_efficiency_gap)
        results["VENUE_SHIFT"] = "B" if rng.random() < venue_prob else "A"

        # 3. Operations Coordination (DISC, AGED, NDIS)
        results["DISC"] = "C" if rng.random() < 0.7 else "F"
        results["AGED"] = "C" if rng.random() < 0.6 else "F"
        results["NDIS"] = "C" if rng.random() < 0.6 else "F"

        # 4. Competition Strategy
        comp_prob = logistic(1.1 * (obs_pressure - 1.0) + 0.5 * params.cannibalization_beta)
        results["COMPETITION"] = "A" if rng.random() < comp_prob else "M"

        return results


class HeuristicAgent(Agent):
    """
    Orchestrator that delegates to distinct Commonwealth, State, and LHN agents.
    """

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        cw = CommonwealthAgent()
        jr = JurisdictionAgent()
        lhn = LHNAgent()

        results = {
            "SIGNAL": "L",
            "SIGNAL_QUALITY": 0.9,
        }

        # Aggregate decisions from all levels
        results.update(cw.decide(state, params, rng))
        results.update(jr.decide(state, params, rng))
        results.update(lhn.decide(state, params, rng))

        results["RATIONALE"] = f"Multi-agent consensus reached in {params.orchestration_mode} mode."
        return results
