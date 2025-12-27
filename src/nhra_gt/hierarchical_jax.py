from __future__ import annotations

import jax
import jax.numpy as jnp
from beartype import beartype
from jaxtyping import Float, Int32, PyTree
from typing import Any

from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.solvers_jax import qre_solver_jax, solve_hierarchical_game_jax
from nhra_gt.engine_jax import step_jax

@beartype
def hierarchical_step_jax(
    commonwealth_state: StateJax,
    jurisdiction_states: StateJax, # Batch of 8 states
    params: ParamsJax,
    macro_strategies: Float[jnp.ndarray, "2"], # e.g. DEF and BARG
    prng_key: Any
) -> tuple[StateJax, StateJax]:
    """
    Executes a single step in a hierarchical (Macro-Micro) simulation.
    
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
    
    # Each jurisdiction picks its own micro-strategies (Heuristic or QRE)
    # For now, we'll assume micro-strategies are determined inside a vectorized step
    
    def single_jurisdiction_step(s, k):
        # Merge macro and micro strategies into the 10-vector
        # 0: SIGNAL, 1: DEF (Macro), 2: BARG (Macro), 3: SHIFT (Micro), 
        # 4: DISC (Micro), 5: AGED (Micro), 6: NDIS (Micro), 7: CODING (Micro), 
        # 8: COMP (Micro), 9: SIGNAL_QUALITY (Macro)
        
        # Mocking micro-choice for now (can use qre_solver_jax here)
        # In a full implementation, we'd solve the subgames here.
        micro_strats = jnp.zeros(10)
        micro_strats = micro_strats.at[1].set(macro_strategies[0]) # DEF
        micro_strats = micro_strats.at[2].set(macro_strategies[1]) # BARG
        # Default others to 0 (Cooperative/Honest)
        
        return step_jax(s, params, micro_strats, k)

    new_jurisdiction_states = jax.vmap(single_jurisdiction_step)(jurisdiction_states, keys)
    
    # 3. Update Commonwealth State (Average of jurisdictions or specific logic)
    # For now, just sync year/month
    new_commonwealth_state = commonwealth_state.replace(
        year = new_jurisdiction_states.year[0],
        month = new_jurisdiction_states.month[0],
        pressure = jnp.mean(new_jurisdiction_states.pressure)
    )
    
    return new_commonwealth_state, new_jurisdiction_states

@beartype
def solve_constitutional_game_jax(
    u_cth: Float[jnp.ndarray, "m n"],
    u_state_macro: Float[jnp.ndarray, "m n"],
    micro_game_factory: Any, # (m, n) -> (u_state_micro, u_lhn)
    lam: float = 5.0
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """
    Solves the nested Constitutional game:
    1. Commonwealth vs State (Macro)
    2. State vs LHN (Micro)
    
    The State's macro payoff is its own payoff from (1) PLUS its equilibrium payoff from (2).
    """
    m, n = u_cth.shape
    
    def get_micro_equilibria(i, j):
        u_state_micro, u_lhn = micro_game_factory(i, j)
        p_micro, q_micro = qre_solver_jax(u_state_micro, u_lhn, lam=lam)
        # Return State and LHN utilities from micro game
        return p_micro @ u_state_micro @ q_micro, p_micro @ u_lhn @ q_micro

    # Vmap over all possible macro outcomes
    row_indices = jnp.repeat(jnp.arange(m), n)
    col_indices = jnp.tile(jnp.arange(n), m)
    
    state_micro_utils, lhn_micro_utils = jax.vmap(get_micro_equilibria)(row_indices, col_indices)
    
    # Effective State payoffs for the macro game
    effective_u_state = u_state_macro + state_micro_utils.reshape(m, n)
    
    # Solve Macro Game
    p_cth, q_state = qre_solver_jax(u_cth, effective_u_state, lam=lam)
    
    return p_cth, q_state, state_micro_utils.reshape(m, n), lhn_micro_utils.reshape(m, n)
