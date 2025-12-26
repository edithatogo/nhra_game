from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, cast

import numpy as np

if TYPE_CHECKING:
    from nhra_game_theory.engine import Params, State


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def softmax(u: np.ndarray, tau: float = 0.25) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    u = u - u.max()
    z = np.exp(u / max(1e-9, tau))
    return cast(np.ndarray, np.asarray(z / z.sum(), dtype=float))


class Agent(ABC):
    """Abstract base class for all NHRA strategic agents."""

    @abstractmethod
    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """Choose strategies based on current system state."""
        pass


class BriefGenerator:
    """Converts simulation state into a textual narrative for LLM consumption."""

    @staticmethod
    def generate(state: State, params: Params, role: str) -> str:
        """Generate a policy brief for a specific role (Commonwealth/State/Provider)."""
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
        """
        Takes a list of (state, strategy, rationale) and returns a realism score.
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
        brief = self.brief_gen.generate(state, params, self.role)

        # In a real implementation, we would call the LLM here.
        # For the simulation engine, we can use a callback or a mock
        # that uses the HeuristicAgent as a 'smart fallback'.

        # MOCK/STUB logic for now:
        heuristic_response = HeuristicAgent().decide(state, params, rng)

        # Add 'Rationale' for Cognitive Trace
        heuristic_response["RATIONALE"] = (
            f"Decided based on heuristic fallback for {self.role}. Pressure is {state.pressure:.2f}."
        )

        return heuristic_response


class HeuristicAgent(Agent):
    """
    An agent that implements the original heuristic and Nash-equilibrium
    selection logic from the v9 engine.
    Supports simultaneous, sequential, and isolation modes.
    """

    def decide(self, state: State, params: Params, rng: np.random.Generator) -> dict[str, Any]:
        """
        Choose strategies based on current system state and orchestration mode.
        """
        noise = float(rng.normal(0.0, params.noise_sd))

        # Default Baseline Actions (Neutral)
        results = {
            "SIGNAL": "L",
            "DEF": "E",
            "BARG": "D",
            "SHIFT": "I",
            "AGED": "C",
            "NDIS": "C",
            "CODING": "H",
            "GOV": "S",
            "COMP": "L",
            "SIGNAL_QUALITY": 1.0,
        }

        # Determine which games to play based on orchestration mode
        games_to_play = list(results.keys())
        if params.orchestration_mode == "isolation" and params.isolated_game:
            games_to_play = [params.isolated_game]

        # Order of play for sequential mode
        play_order = [
            "SIGNAL",
            "BARG",
            "DEF",
            "SHIFT",
            "AGED",
            "NDIS",
            "CODING",
            "GOV",
            "COMP",
            "SIGNAL_QUALITY",
        ]

        for g in play_order:
            if g not in games_to_play:
                continue

            # --- Game Logic Implementation ---
            if params.use_stage_game_equilibria and g != "SIGNAL" and g != "SIGNAL_QUALITY":
                # Equilibrium solver path
                from nhra_game_theory.subgames.games import (
                    GameParams,
                    aged_care_interface_game,
                    bargaining_game,
                    coding_audit_game,
                    compliance_game,
                    cost_shifting_game,
                    definition_game,
                    governance_integration_game,
                    ndis_interface_game,
                )
                from nhra_game_theory.subgames.nash import all_nash, select_equilibrium

                gp = GameParams(
                    pressure=float(state.pressure),
                    efficiency_gap=float(state.efficiency_gap),
                    discharge_delay=float(state.discharge_delay),
                    political_salience=float(params.political_salience),
                    audit_pressure=float(params.audit_pressure),
                    cost_shifting_intensity=float(params.cost_shifting_intensity),
                    political_capital=float(state.political_capital),
                )

                def _solve(game: Any) -> tuple[str, str]:
                    if params.use_quantal_response:
                        u_row_expected = np.mean(game.u_row, axis=1)
                        u_col_expected = np.mean(game.u_col, axis=0)
                        prob_row = softmax(u_row_expected, tau=1.0 / max(1e-9, params.qre_lambda))
                        prob_col = softmax(u_col_expected, tau=1.0 / max(1e-9, params.qre_lambda))
                        row_a = (
                            game.row_actions[1]
                            if rng.random() < prob_row[1]
                            else game.row_actions[0]
                        )
                        col_a = (
                            game.col_actions[1]
                            if rng.random() < prob_col[1]
                            else game.col_actions[0]
                        )
                        return row_a, col_a
                    else:
                        eqs = all_nash(game)
                        sel = select_equilibrium(
                            eqs,
                            rule=params.equilibrium_selection_rule,
                            u_row=game.u_row,
                            u_col=game.u_col,
                        )
                        row_a = game.row_actions[int(np.argmax(sel.row))]
                        col_a = game.col_actions[int(np.argmax(sel.col))]
                        return row_a, col_a

                if g == "DEF":
                    r_def, _ = _solve(definition_game(gp))
                    results["DEF"] = r_def
                elif g == "BARG":
                    r_barg, c_barg = _solve(bargaining_game(gp))
                    results["BARG"] = "A" if (r_barg == "A" and c_barg == "A") else "D"
                elif g == "SHIFT":
                    r_shift, c_shift = _solve(cost_shifting_game(gp))
                    results["SHIFT"] = "S" if (r_shift == "S" or c_shift == "S") else "I"
                elif g == "AGED":
                    r_aged, c_aged = _solve(aged_care_interface_game(gp))
                    results["AGED"] = "C" if (r_aged == "C" and c_aged == "C") else "F"
                elif g == "NDIS":
                    r_ndis, c_ndis = _solve(ndis_interface_game(gp))
                    results["NDIS"] = "C" if (r_ndis == "C" and c_ndis == "C") else "F"
                elif g == "CODING":
                    r_coding, c_audit = _solve(coding_audit_game(gp))
                    results["CODING"] = r_coding
                    results["COMP"] = "T" if c_audit == "T" else "L"
                elif g == "GOV":
                    r_gov, c_gov = _solve(governance_integration_game(gp))
                    results["GOV"] = "I" if (r_gov == "I" and c_gov == "I") else "S"
                elif g == "COMP":
                    r_comp, _ = _solve(compliance_game(gp))
                    results["COMP"] = r_comp

            else:
                # Heuristic fallback path
                if g == "SIGNAL":
                    u_H = +0.10 + 0.30 * (state.pressure - 1.0) + noise
                    u_L = +0.05 - 0.10 * (state.pressure - 1.0) - noise
                    prob_sig = softmax(np.array([u_L, u_H]), tau=params.tau)
                    results["SIGNAL"] = "H" if rng.random() < prob_sig[1] else "L"

                elif g == "BARG":
                    sig_bonus = 0.1 if results.get("SIGNAL") == "H" else 0.0
                    BARG_prob = logistic(
                        0.6 * (1.2 - state.pressure)
                        - 0.4 * params.political_salience
                        + state.bailout_expectation
                        + sig_bonus
                    )
                    results["BARG"] = "A" if rng.random() < BARG_prob else "D"

                elif g == "DEF":
                    barg_multiplier = 1.2 if results.get("BARG") == "A" else 0.8
                    DEF_prob = (
                        logistic(1.3 * (state.efficiency_gap - 0.25) + 0.9 * (state.pressure - 1.0))
                        * barg_multiplier
                    )
                    results["DEF"] = "R" if rng.random() < DEF_prob else "E"

                elif g == "SHIFT":
                    SHIFT_prob = logistic(
                        -1.1 * (state.pressure - 1.0) - 1.0 * state.efficiency_gap
                    )
                    results["SHIFT"] = "I" if rng.random() < SHIFT_prob else "S"

                elif g == "AGED":
                    AGED_prob = logistic(
                        -0.9 * (state.discharge_delay - 1.0) - 0.5 * (state.pressure - 1.0)
                    )
                    results["AGED"] = "C" if rng.random() < AGED_prob else "F"

                elif g == "NDIS":
                    NDIS_prob = logistic(
                        -0.7 * (state.discharge_delay - 1.0) - 0.6 * (state.pressure - 1.0)
                    )
                    results["NDIS"] = "C" if rng.random() < NDIS_prob else "F"

                elif g == "CODING":
                    CODING_prob = logistic(
                        1.5 * (state.pressure - 1.1) + 1.2 * state.efficiency_gap
                    )
                    results["CODING"] = "U" if rng.random() < CODING_prob else "H"

                elif g == "GOV":
                    GOV_prob = logistic(
                        -0.8 * (state.pressure - 1.0) - 0.7 * params.political_salience
                    )
                    results["GOV"] = "I" if rng.random() < GOV_prob else "S"

                elif g == "COMP":
                    COMP_prob = logistic(0.9 * params.audit_pressure - 0.7 * state.efficiency_gap)
                    results["COMP"] = "T" if rng.random() < COMP_prob else "L"

                elif g == "SIGNAL_QUALITY":
                    sig_quality = (
                        0.7 - 0.2 * (state.pressure - 1.0) if results.get("BARG") == "D" else 0.9
                    )
                    results["SIGNAL_QUALITY"] = float(
                        np.clip(sig_quality + rng.normal(0, 0.05), 0.3, 1.0)
                    )

        results["RATIONALE"] = (
            f"Decided using {params.orchestration_mode} mode. Pressure: {state.pressure:.2f}"
        )
        return results
