from __future__ import annotations

import jax
import jax.numpy as jnp
from flax import struct
from jaxtyping import Float
from beartype import beartype

@struct.dataclass
class AgentWeights:
    # LHN Weights
    ramping_penalty: float = 10.0
    nwau_utility: float = 1.0
    cost_disutility: float = 1.0
    
    # State Weights
    vfi_disutility: float = 5.0
    kpi_satisfaction: float = 2.0

@beartype
def lhn_utility(
    pressure: Float[jnp.ndarray, ""],
    revenue: Float[jnp.ndarray, ""],
    cost: Float[jnp.ndarray, ""],
    weights: AgentWeights
) -> Float[jnp.ndarray, ""]:
    """
    Utility for the LHN Agent.
    Prioritizes minimizing ramping (pressure) and maximizing net revenue.
    Ramping penalty is non-linear (squared) to reflect political sensitivity.
    """
    ramping_cost = weights.ramping_penalty * jnp.square(jnp.maximum(0, pressure - 1.0))
    net_revenue = weights.nwau_utility * revenue - weights.cost_disutility * cost
    return net_revenue - ramping_cost

@beartype
def state_utility(
    fiscal_gap: Float[jnp.ndarray, ""],
    lhn_performance: Float[jnp.ndarray, ""], # Mean LHN utility or KPI satisfaction
    weights: AgentWeights
) -> Float[jnp.ndarray, ""]:
    """
    Utility for the State Agent.
    Focuses on minimizing fiscal gaps (VFI) and maintaining LHN performance.
    """
    vfi_cost = weights.vfi_disutility * jnp.square(jnp.maximum(0, fiscal_gap))
    return weights.kpi_satisfaction * lhn_performance - vfi_cost
