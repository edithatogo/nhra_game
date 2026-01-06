"""JAX-native Heuristic and Strategic Agents.

Optimized implementations of agent logic for use inside JIT-compiled loops.
"""

from __future__ import annotations

import jax.numpy as jnp
from flax import struct

from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.solvers_jax import qre_solver_jax
from nhra_gt.subgames.games_jax import (
    GameParamsJax,
    bargaining_game_jax,
    cost_shifting_game_jax,
    definition_game_jax,
)


@struct.dataclass
class HeuristicAgentJax:
    """JAX-compatible agent that produces a strategy vector.

    Can operate in 'Heuristic' mode (smooth logistic rules) or 'Strategic' mode
    (Nash/QRE solving for key subgames).
    """

    solve_nash: bool = False
    lambda_qre: float = 5.0

    def decide(self, state: StateJax, params: ParamsJax) -> jnp.ndarray:
        """Choose strategy vector based on current state.

        Output: jnp.ndarray of shape (13,).
        """
        obs_pressure = state.reported_pressure
        obs_eff_gap = state.reported_efficiency_gap

        # 1. Base Heuristic Logic
        def prob(x):
            return 1.0 / (1.0 + jnp.exp(-x))

        comp = prob(
            params.behavior.h_comp_audit_weight * params.audit_pressure
            - params.behavior.h_comp_eff_gap_weight * obs_eff_gap
        )

        def_framing = prob(
            params.behavior.h_def_eff_gap_weight
            * (obs_eff_gap - params.behavior.h_def_eff_gap_offset)
            + params.behavior.h_def_pressure_weight
            * (obs_pressure - params.behavior.h_def_pressure_offset)
        )

        barg = prob(
            params.behavior.h_barg_pressure_weight
            * (params.behavior.h_barg_pressure_offset - obs_pressure)
            + state.bailout_expectation
        )

        shift = prob(
            -params.behavior.h_shift_pressure_weight
            * (obs_pressure - params.behavior.h_shift_pressure_offset)
            - params.behavior.h_shift_eff_gap_weight * obs_eff_gap
        )

        # Static/Base heuristics
        disc = params.behavior.h_disc_base
        aged = params.behavior.h_aged_base
        ndis = params.behavior.h_ndis_base
        coding = prob(
            params.behavior.h_coding_pressure_weight
            * (obs_pressure - params.behavior.h_coding_pressure_offset)
            + params.behavior.h_coding_eff_gap_weight * obs_eff_gap
        )
        wf = params.behavior.h_wf_base + params.behavior.h_wf_pressure_weight * (
            obs_pressure - params.behavior.h_wf_pressure_offset
        )
        signal = params.behavior.h_signal_base
        venue = prob(
            params.behavior.h_venue_pressure_weight
            * (obs_pressure - params.behavior.h_venue_pressure_offset)
            + params.behavior.h_venue_eff_gap_weight * obs_eff_gap
        )
        cap = params.behavior.h_cap_pressure_weight * (
            obs_pressure - params.behavior.h_cap_pressure_offset
        )
        comp_mode = prob(
            params.behavior.h_comp_mode_pressure_weight
            * (obs_pressure - params.behavior.h_comp_mode_pressure_offset)
            + params.behavior.h_comp_mode_cannibal_weight * params.cannibalization_beta
        )

        h_vector = jnp.array(
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

        # 2. Strategic Overrides (if enabled)
        if self.solve_nash:
            gp = GameParamsJax(
                pressure=obs_pressure,
                efficiency_gap=obs_eff_gap,
                discharge_delay=state.reported_discharge_delay
                if hasattr(state, "reported_discharge_delay")
                else 1.0,
                political_salience=params.political_salience,
                audit_pressure=params.audit_pressure,
                cost_shifting_intensity=params.cost_shifting_intensity,
                political_capital=state.political_capital,
                behavior=params.behavior,
            )

            # --- Definition Game ---
            u_row_def, u_col_def = definition_game_jax(gp)
            p_def, _q_def, _ = qre_solver_jax(u_row_def, u_col_def, lam=self.lambda_qre)
            # Use probability of action 0 (Realism) as the continuous strategy
            h_vector = h_vector.at[1].set(p_def[0])

            # --- Bargaining Game ---
            u_row_barg, u_col_barg = bargaining_game_jax(gp)
            p_barg, _q_barg, _ = qre_solver_jax(u_row_barg, u_col_barg, lam=self.lambda_qre)
            h_vector = h_vector.at[2].set(p_barg[0])

            # --- Cost Shifting Game ---
            u_row_shift, u_col_shift = cost_shifting_game_jax(gp)
            p_shift, _q_shift, _ = qre_solver_jax(u_row_shift, u_col_shift, lam=self.lambda_qre)
            h_vector = h_vector.at[3].set(p_shift[0])

        return h_vector
