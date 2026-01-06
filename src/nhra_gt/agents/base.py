"""Base classes and orchestrators for NHRA strategic agents.

This module defines the interfaces for strategic actors in the simulation,
including heuristic models and LLM-driven agents. It also provides utilities
for generating narratives and validating strategic traces.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from nhra_gt.engine import Params, State


def logistic(x: float) -> float:
    """Standard sigmoid function."""
    return 1.0 / (1.0 + math.exp(-x))


def softmax(u: np.ndarray, tau: float = 0.25) -> np.ndarray:
    """Numpy implementation of tau-tempered softmax."""
    u = np.asarray(u, dtype=float)
    u = u - u.max()
    z = np.exp(u / max(1e-9, tau))
    return np.asarray(z / z.sum(), dtype=float)


class Agent(ABC):
    """Abstract base class for all NHRA strategic agents."""

    @abstractmethod
    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Choose strategies based on current system state."""


class BriefGenerator:
    """Converts simulation state into a textual narrative for LLM consumption."""

    @staticmethod
    def generate(state: State, _params: Params, role: str) -> str:
        """Generate a policy brief for a specific role (Commonwealth/State/Provider)."""
        mode_desc = {
            "normal": "The system is currently stable.",
            "stress": "The system is under significant pressure.",
            "crisis": "CRITICAL: The system is in a state of failure (Code Red).",
            "recovery": "The system is recovering from a crisis.",
        }

        # Get values from first jurisdiction if available, fallback to defaults
        eff_gap = state.reported_efficiency_gap
        eff_share = (
            state.jurisdictions[0].effective_cth_share
            if hasattr(state, "jurisdictions") and state.jurisdictions
            else 0.38
        )
        pol_cap = (
            state.jurisdictions[0].political_capital
            if hasattr(state, "jurisdictions") and state.jurisdictions
            else 1.0
        )
        eq_idx = (
            state.jurisdictions[0].equity_index
            if hasattr(state, "jurisdictions") and state.jurisdictions
            else 1.0
        )

        brief = f"""
### NHRA POLICY BRIEF - {role.upper()}
**Current Year:** {state.year}, Month {state.month}
**System Mode:** {state.system_mode.value.upper()} - {mode_desc.get(state.system_mode.value, "")}

**Key Metrics:**
- System Pressure: {state.pressure:.2f} (Base: 1.0)
- ED Wait Time: {state.within4 * 100:.1f}% within 4h
- Efficiency Gap: {eff_gap * 100:.1f}% (Cost vs NEP)
- Effective Cth Share: {eff_share * 100:.1f}%
- Political Capital: {pol_cap:.2f}
- Equity Index: {eq_idx:.2f}

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
    """Evaluates agent strategic traces from an 'Auditor' perspective.

    Scores realism and detects unlikely gaming behavior.
    """

    def validate(self, _trace: list[dict[str, Any]]) -> dict[str, Any]:
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
    """An agent that uses a Large Language Model to make strategic decisions."""

    def __init__(self, role: str, model_name: str = "gemini-pro"):
        """Initialize the LLM agent with a specific role and model."""
        self.role = role
        self.model_name = model_name
        self.brief_gen = BriefGenerator()

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Generates a brief, calls the LLM, and parses the strategic response.

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
    """The Principal (Federal Govt) setting price and compliance rules.

    Focuses on fiscal sustainability, compliance targets, and framing the NEP.
    """

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Chooses framing (DEF) and compliance (COMP) strategies."""
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = state.reported_efficiency_gap

        # Commonwealth moves: DEF, COMP, BARG(offer)
        results = {}

        # 1. Compliance Strategy (COMP)
        comp_prob = logistic(
            params.behavior.h_comp_audit_weight * params.audit_pressure
            - params.behavior.h_comp_eff_gap_weight * obs_efficiency_gap
        )
        results["COMP"] = "T" if rng.random() < comp_prob else "L"

        # 2. Framing Strategy (DEF)
        def_prob = logistic(
            params.behavior.h_def_eff_gap_weight
            * (obs_efficiency_gap - params.behavior.h_def_eff_gap_offset)
            + params.behavior.h_def_pressure_weight
            * (obs_pressure - params.behavior.h_def_pressure_offset)
        )
        results["DEF"] = "R" if rng.random() < def_prob else "E"

        return results


class JurisdictionAgent(Agent):
    """The Intermediary (State/Territory Govt) managing the Agreement.

    Focuses on budget reconciliation, political capital, and cost-shifting.
    """

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Chooses bargaining (BARG), cost-shifting (SHIFT), and governance (GOV) strategies."""
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = state.reported_efficiency_gap

        # Get bailout expectation from first jurisdiction
        bailout_exp = (
            state.jurisdictions[0].bailout_expectation
            if hasattr(state, "jurisdictions") and state.jurisdictions
            else 0.0
        )

        # State moves: BARG, SHIFT, GOV
        results = {}

        # 1. Bargaining Strategy (BARG)
        barg_prob = logistic(
            params.behavior.h_barg_pressure_weight
            * (params.behavior.h_barg_pressure_offset - obs_pressure)
            + bailout_exp
        )
        results["BARG"] = "A" if rng.random() < barg_prob else "D"

        # 2. Cost Shifting (SHIFT)
        shift_prob = logistic(
            -params.behavior.h_shift_pressure_weight
            * (obs_pressure - params.behavior.h_shift_pressure_offset)
            - params.behavior.h_shift_eff_gap_weight * obs_efficiency_gap
        )
        results["SHIFT"] = "I" if rng.random() < shift_prob else "S"

        # 3. Governance (GOV)
        gov_prob = logistic(
            -params.behavior.h_venue_pressure_weight
            * (obs_pressure - params.behavior.h_venue_pressure_offset)
            - params.behavior.h_venue_eff_gap_weight * params.political_salience
        )
        results["GOV"] = "I" if rng.random() < gov_prob else "S"

        return results


class LHNAgent(Agent):
    """The Operator (Hospital/LHN) managing clinical demand and revenue.

    Focuses on upcoding, venue shifting, and coordination with aged care/NDIS.
    """

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Chooses coding, venue, and clinical coordination strategies."""
        obs_pressure = getattr(state, "reported_pressure", state.pressure)
        obs_efficiency_gap = state.reported_efficiency_gap

        # LHN moves: CODING, VENUE_SHIFT, DISC, AGED, NDIS, COMPETITION
        results = {}

        # 1. Revenue Strategy (CODING)
        coding_prob = logistic(
            params.behavior.h_coding_pressure_weight
            * (obs_pressure - params.behavior.h_coding_pressure_offset)
            + params.behavior.h_coding_eff_gap_weight * obs_efficiency_gap
        )
        results["CODING"] = "U" if rng.random() < coding_prob else "H"

        # 2. Venue Selection (VENUE_SHIFT)
        venue_prob = logistic(
            params.behavior.h_venue_pressure_weight
            * (obs_pressure - params.behavior.h_venue_pressure_offset)
            + params.behavior.h_venue_eff_gap_weight * obs_efficiency_gap
        )
        results["VENUE_SHIFT"] = "B" if rng.random() < venue_prob else "A"

        # 3. Operations Coordination (DISC, AGED, NDIS)
        results["DISC"] = "C" if rng.random() < params.behavior.h_disc_base else "F"
        results["AGED"] = "C" if rng.random() < params.behavior.h_aged_base else "F"
        results["NDIS"] = "C" if rng.random() < params.behavior.h_ndis_base else "F"

        # 4. Competition Strategy
        comp_prob = logistic(
            params.behavior.h_comp_mode_pressure_weight
            * (obs_pressure - params.behavior.h_comp_mode_pressure_offset)
            + params.behavior.h_comp_mode_cannibal_weight * params.cannibalization_beta
        )
        results["COMPETITION"] = "A" if rng.random() < comp_prob else "M"

        return results


class HeuristicAgent(Agent):
    """Orchestrator that delegates to distinct Commonwealth, State, and LHN agents."""

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Delegate decision making to Commonwealth, State, and LHN sub-agents."""
        cw = CommonwealthAgent()
        jr = JurisdictionAgent()
        lhn = LHNAgent()

        results = {
            "SIGNAL": "L",
            "SIGNAL_QUALITY": params.behavior.h_signal_base,
        }

        # Aggregate decisions from all levels
        results.update(cw.decide(state, params, rng))
        results.update(jr.decide(state, params, rng))
        results.update(lhn.decide(state, params, rng))

        results["RATIONALE"] = f"Multi-agent consensus reached in {params.orchestration_mode} mode."
        return results
