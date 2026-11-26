"""JAX-native Heuristic and Strategic Agents.

Optimized implementations of agent logic for use inside JIT-compiled loops.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
from jax import Array

from nhra_gt._pytree import PytreeRecord, pytree_dataclass
from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.solvers_jax import QreDiagnostics, solve_qualified_two_player_qre
from nhra_gt.subgames.games_jax import (
    GameParamsJax,
    bargaining_game_jax,
    cost_shifting_game_jax,
    definition_game_jax,
)

STRATEGIC_QRE_GAMES = ("definition", "bargaining", "cost shifting")


@pytree_dataclass
class HeuristicAgentJax(PytreeRecord):
    """JAX-compatible agent that produces a strategy vector.

    Can operate in 'Heuristic' mode (smooth logistic rules) or 'Strategic' mode
    (Nash/QRE solving for key subgames).
    """

    solve_nash: bool = False
    lambda_qre: float = 5.0

    def decide(self, state: StateJax, params: ParamsJax) -> Array:
        """Return the strategy vector, using NaN when a required QRE is unqualified."""
        return self.decide_with_diagnostics(state, params)[0]

    def decide_with_diagnostics(
        self, state: StateJax, params: ParamsJax
    ) -> tuple[Array, QreDiagnostics | None]:
        """Return the strategy vector and each required strategic QRE diagnostic.

        Diagnostics follow STRATEGIC_QRE_GAMES order. Heuristic mode returns no
        QRE diagnostics.
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
                discharge_delay=getattr(state, "reported_discharge_delay", 1.0),
                political_salience=params.political_salience,
                audit_pressure=params.audit_pressure,
                cost_shifting_intensity=params.cost_shifting_intensity,
                political_capital=state.political_capital,
                behavior=params.behavior,
            )

            decisions = [
                solve_qualified_two_player_qre(*game(gp), lam=self.lambda_qre)
                for game in (definition_game_jax, bargaining_game_jax, cost_shifting_game_jax)
            ]
            diagnostics = jax.tree.map(
                lambda *values: jnp.stack(values), *(d for _, _, d in decisions)
            )
            h_vector = h_vector.at[1:4].set(jnp.stack([row[0] for row, _, _ in decisions]))
            return jnp.where(jnp.all(diagnostics.qualified), h_vector, jnp.nan), diagnostics

        return h_vector, None
