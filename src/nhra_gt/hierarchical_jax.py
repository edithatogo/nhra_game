"""Hierarchical Simulation and Constitutional Game Solvers.

This module handles the interaction between different levels of the health
system (Commonwealth, Jurisdiction, LHN) using vectorized JAX operations.
It includes solvers for "Constitutional" games where macro-level choices
affect micro-level incentives.
"""

from __future__ import annotations

from typing import Any, NamedTuple

import jax
import jax.numpy as jnp
from beartype import beartype
from jax import Array

from nhra_gt.domain.state import Params, StateJax
from nhra_gt.engine import step_jax
from nhra_gt.solvers_jax import QreDiagnostics, QreStatus, solve_qualified_two_player_qre


@beartype
def hierarchical_step_jax(
    commonwealth_state: StateJax,
    jurisdiction_states: StateJax,  # Batch of 8 states
    params: Params,
    macro_strategies: Any,  # e.g. DEF and BARG
    prng_key: Any,
) -> tuple[StateJax, StateJax]:
    """Executes a single step in a hierarchical (Macro-Micro) simulation.

    Args:
        commonwealth_state: The global/macro state.
        jurisdiction_states: A batch of states (one per jurisdiction).
        params: Global parameters.
        macro_strategies: Chosen actions for macro games.
        prng_key: Random key.

    Returns:
        A tuple of (new_commonwealth_state, new_jurisdiction_states).
    """
    # 1. Macro outcomes affect global indices (NEP, WPI) - already handled in step_jax

    # 2. Vectorized Step over jurisdictions
    # We vmap over the jurisdiction_states batch

    num_jurisdictions = jurisdiction_states.year.shape[0]
    keys = jax.random.split(prng_key, num_jurisdictions)

    def _in_axes_for_batch(tree: Any) -> Any:
        """Determines vmap in_axes for a state PyTree batch."""

        def axis_for(x: Any) -> int | None:
            try:
                if hasattr(x, "ndim") and x.ndim > 0 and x.shape[0] == num_jurisdictions:
                    return 0
            except Exception:
                return None
            return None

        return jax.tree_util.tree_map(axis_for, tree)

    in_axes_state = _in_axes_for_batch(jurisdiction_states)

    # Each jurisdiction picks its own micro-strategies (Heuristic or QRE)
    # For now, we'll assume micro-strategies are determined inside a vectorized step

    def single_jurisdiction_step(s, k):
        """Performs a step for a single jurisdiction in the batch."""
        # Merge macro and micro strategies into the 12-vector
        # 0: SIGNAL, 1: DEF (Macro), 2: BARG (Macro), 3: SHIFT (Micro),
        # 4: DISC (Micro), 5: AGED (Micro), 6: NDIS (Micro), 7: CODING (Micro),
        # 8: COMP (Micro), 9: SIGNAL_QUALITY (Macro), 10: VENUE_SHIFT, 11: CAPACITY,
        # 12: COMPETITION

        # Mocking micro-choice for now (can use the QRE solver here)
        # In a full implementation, we'd solve the subgames here.
        micro_strats = jnp.zeros(13)
        micro_strats = micro_strats.at[1].set(macro_strategies[0])  # DEF
        micro_strats = micro_strats.at[2].set(macro_strategies[1])  # BARG
        # Default others to 0 (Cooperative/Honest)

        return step_jax(s, params, micro_strats, k)

    new_jurisdiction_states = jax.vmap(single_jurisdiction_step, in_axes=(in_axes_state, 0))(
        jurisdiction_states, keys
    )

    # 3. Update Commonwealth State (Average of jurisdictions or specific logic)
    # For now, just sync year/month
    new_commonwealth_state = commonwealth_state.replace(
        year=new_jurisdiction_states.year[0],
        month=new_jurisdiction_states.month[0],
        pressure=jnp.mean(new_jurisdiction_states.pressure),
    )

    return new_commonwealth_state, new_jurisdiction_states


class ConstitutionalQreResult(NamedTuple):
    """Constitutional solution and compiled macro and per-cell micro diagnostics."""

    row: Array
    column: Array
    state_micro_utils: Array
    lhn_micro_utils: Array
    micro: QreDiagnostics
    macro: QreDiagnostics

    @property
    def qualified(self) -> Array:
        """Tell whether every required QRE was qualified."""
        return self.macro.qualified

    @property
    def solution(self) -> tuple[Array, Array, Array, Array]:
        """Return the four-array solution used by the original compiled API."""
        return self.row, self.column, self.state_micro_utils, self.lhn_micro_utils


@beartype
def solve_constitutional_game_jax(
    u_cth: Any,
    u_state_macro: Any,
    micro_game_factory: Any,
    lam: float = 5.0,
) -> tuple[Array, Array, Array, Array]:
    """Return the qualified solution using the original four-array JAX tree."""
    return solve_constitutional_game_with_diagnostics_jax(
        u_cth, u_state_macro, micro_game_factory, lam=lam
    ).solution


@beartype
def solve_constitutional_game_with_diagnostics_jax(
    u_cth: Any,
    u_state_macro: Any,
    micro_game_factory: Any,  # (m, n) -> (u_state_micro, u_lhn)
    lam: float = 5.0,
) -> ConstitutionalQreResult:
    """Solves the nested Constitutional game using backward induction.

    1. Commonwealth vs State (Macro)
    2. State vs LHN (Micro)

    The State's macro payoff is its own payoff from (1) PLUS its equilibrium
    payoff from (2).

    The solution property returns the original four arrays. The micro and
    macro fields expose the original residuals. An unqualified microgame
    withholds the constitutional solution and skips the macro solve.
    """
    m, n = u_cth.shape

    def get_micro_equilibria(i, j):
        """Helper to resolve micro-game equilibria for each macro outcome."""
        u_state_micro, u_lhn = micro_game_factory(i, j)
        p_micro, q_micro, diagnostics = solve_qualified_two_player_qre(
            u_state_micro, u_lhn, lam=lam
        )
        # Return State and LHN utilities from micro game
        return p_micro @ u_state_micro @ q_micro, p_micro @ u_lhn @ q_micro, diagnostics

    # Vmap over all possible macro outcomes
    row_indices = jnp.repeat(jnp.arange(m), n)
    col_indices = jnp.tile(jnp.arange(n), m)

    state_utils, lhn_utils, micro = jax.vmap(get_micro_equilibria)(row_indices, col_indices)
    state_utils, lhn_utils = state_utils.reshape(m, n), lhn_utils.reshape(m, n)
    micro = jax.tree.map(lambda values: values.reshape(m, n), micro)

    def solve_macro():
        return solve_qualified_two_player_qre(u_cth, u_state_macro + state_utils, lam=lam)

    def skip_macro():
        missing = jnp.asarray(jnp.nan, dtype=state_utils.dtype)
        diagnostics = QreDiagnostics(missing, jnp.asarray(QreStatus.SKIPPED, dtype=jnp.int32))
        return jnp.broadcast_to(missing, (m,)), jnp.broadcast_to(missing, (n,)), diagnostics

    p_cth, q_state, macro = jax.lax.cond(jnp.all(micro.qualified), solve_macro, skip_macro)
    return ConstitutionalQreResult(
        p_cth,
        q_state,
        jnp.where(macro.qualified, state_utils, jnp.nan),
        jnp.where(macro.qualified, lhn_utils, jnp.nan),
        micro,
        macro,
    )
