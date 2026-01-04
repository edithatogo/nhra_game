"""
JAX-native Heuristic Agents.

Optimized implementations of agent logic for use inside JIT-compiled loops.
"""

from __future__ import annotations

import jax.numpy as jnp
from flax import struct

from nhra_gt.domain.state import Params, StateJax


@struct.dataclass
class HeuristicAgentJax:
    """
    JAX-compatible heuristic agent that produces a continuous strategy vector.
    Mirrors the logic of HeuristicAgent but in a differentiable/vectorized form.
    """

    def decide(self, state: StateJax, params: Params) -> jnp.ndarray:
        """
        Choose strategy vector based on current state.
        Output: jnp.ndarray of shape (13,)
        """
        obs_pressure = state.reported_pressure
        obs_eff_gap = state.reported_efficiency_gap

        # Helper for logistic-like probability mapping
        def prob(x):
            return 1.0 / (1.0 + jnp.exp(-x))

        # 0: COMP (Compliance) - Tight vs Light
        comp = prob(0.9 * params.audit_pressure - 0.7 * obs_eff_gap)

        # 1: DEF (Framing) - Realism vs Strict
        def_framing = prob(1.3 * (obs_eff_gap - 0.25) + 0.9 * (obs_pressure - 1.0))

        # 2: BARG (Bargaining) - Agree vs Defer
        barg = prob(0.6 * (1.2 - obs_pressure) + state.bailout_expectation)

        # 3: SHIFT (Cost Shifting) - Invest vs Shift
        shift = prob(-1.1 * (obs_pressure - 1.0) - 1.0 * obs_eff_gap)

        # 4: DISC (Discharge Coordination) - Coordinate vs Fragment
        disc = 0.7  # Heuristic from legacy

        # 5: AGED (Aged Care) - Coordinate vs Fragment
        aged = 0.6

        # 6: NDIS (NDIS) - Coordinate vs Fragment
        ndis = 0.6

        # 7: CODING (Coding Intensity) - Upcode vs Honest
        coding = prob(1.5 * (obs_pressure - 1.1) + 1.2 * obs_eff_gap)

        # 8: WORKFORCE (Workforce Intensity)
        wf = 0.5 + 0.2 * (obs_pressure - 1.0)

        # 9: SIGNAL (Signalling)
        signal = 0.9

        # 10: VENUE_SHIFT (Venue Shift) - Block vs ABF
        venue = prob(1.2 * (obs_pressure - 1.1) + 0.8 * obs_eff_gap)

        # 11: CAP (Capacity Move)
        cap = 0.05 * (obs_pressure - 1.0)

        # 12: COMPETITION (Competition Mode)
        comp_mode = prob(1.1 * (obs_pressure - 1.0) + 0.5 * params.cannibalization_beta)

        return jnp.array(
            [
                comp,
                def_framing,
                barg,
                shift,
                disc,
                aged,
                ndis,
                coding,
                wf,
                signal,
                venue,
                cap,
                comp_mode,
            ]
        )
