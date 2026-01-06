"""JAX-native Heuristic Agents.

Optimized implementations of agent logic for use inside JIT-compiled loops.
"""

from __future__ import annotations

import jax.numpy as jnp
from flax import struct

from nhra_gt.domain.state import Params, StateJax


@struct.dataclass
class HeuristicAgentJax:
    """JAX-compatible heuristic agent that produces a continuous strategy vector.

    Mirrors the logic of HeuristicAgent but in a differentiable/vectorized form.
    """

    def decide(self, state: StateJax, params: Params) -> jnp.ndarray:
        """Choose strategy vector based on current state.

        Output: jnp.ndarray of shape (13,).
        """
        obs_pressure = state.reported_pressure
        obs_eff_gap = state.reported_efficiency_gap

        # Helper for logistic-like probability mapping
        def prob(x):
            return 1.0 / (1.0 + jnp.exp(-x))

        # 0: COMP (Compliance) - Tight vs Light
        comp = prob(
            params.behavior.h_comp_audit_weight * params.audit_pressure
            - params.behavior.h_comp_eff_gap_weight * obs_eff_gap
        )

        # 1: DEF (Framing) - Realism vs Strict
        def_framing = prob(
            params.behavior.h_def_eff_gap_weight
            * (obs_eff_gap - params.behavior.h_def_eff_gap_offset)
            + params.behavior.h_def_pressure_weight
            * (obs_pressure - params.behavior.h_def_pressure_offset)
        )

        # 2: BARG (Bargaining) - Agree vs Defer
        barg = prob(
            params.behavior.h_barg_pressure_weight
            * (params.behavior.h_barg_pressure_offset - obs_pressure)
            + state.bailout_expectation
        )

        # 3: SHIFT (Cost Shifting) - Invest vs Shift
        shift = prob(
            -params.behavior.h_shift_pressure_weight
            * (obs_pressure - params.behavior.h_shift_pressure_offset)
            - params.behavior.h_shift_eff_gap_weight * obs_eff_gap
        )

        # 4: DISC (Discharge Coordination) - Coordinate vs Fragment
        disc = params.behavior.h_disc_base

        # 5: AGED (Aged Care) - Coordinate vs Fragment
        aged = params.behavior.h_aged_base

        # 6: NDIS (NDIS) - Coordinate vs Fragment
        ndis = params.behavior.h_ndis_base

        # 7: CODING (Coding Intensity) - Upcode vs Honest
        coding = prob(
            params.behavior.h_coding_pressure_weight
            * (obs_pressure - params.behavior.h_coding_pressure_offset)
            + params.behavior.h_coding_eff_gap_weight * obs_eff_gap
        )

        # 8: WORKFORCE (Workforce Intensity)
        wf = params.behavior.h_wf_base + params.behavior.h_wf_pressure_weight * (
            obs_pressure - params.behavior.h_wf_pressure_offset
        )

        # 9: SIGNAL (Signalling)
        signal = params.behavior.h_signal_base

        # 10: VENUE_SHIFT (Venue Shift) - Block vs ABF
        venue = prob(
            params.behavior.h_venue_pressure_weight
            * (obs_pressure - params.behavior.h_venue_pressure_offset)
            + params.behavior.h_venue_eff_gap_weight * obs_eff_gap
        )

        # 11: CAP (Capacity Move)
        cap = params.behavior.h_cap_pressure_weight * (
            obs_pressure - params.behavior.h_cap_pressure_offset
        )

        # 12: COMPETITION (Competition Mode)
        comp_mode = prob(
            params.behavior.h_comp_mode_pressure_weight
            * (obs_pressure - params.behavior.h_comp_mode_pressure_offset)
            + params.behavior.h_comp_mode_cannibal_weight * params.cannibalization_beta
        )

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
