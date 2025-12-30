from __future__ import annotations

import jax.numpy as jnp
from beartype import beartype
from flax import struct
from jaxtyping import Array, Float


@struct.dataclass
class AgentWeights:
    # LHN Weights
    ramping_penalty: float = 10.0
    nwau_utility: float = 1.0
    cost_disutility: float = 1.0
    shifting_penalty: float = 2.0
    capacity_inertia_weight: float = 5.0

    # State Weights
    vfi_disutility: float = 5.0
    kpi_satisfaction: float = 2.0


@beartype
def lhn_utility(
    pressure: Float[Array, ""],
    revenue: Float[Array, ""],
    cost: Float[Array, ""],
    is_shifting: bool,
    delta_target_capacity: Float[Array, ""],
    weights: AgentWeights,
) -> Float[Array, ""]:
    """
    Utility for the LHN Agent.
    Prioritizes minimizing ramping (pressure) and maximizing net revenue.
    Ramping penalty is non-linear (squared) to reflect political sensitivity.
    Inertia penalty discourages rapid target oscillations.
    """
    ramping_cost = weights.ramping_penalty * jnp.square(jnp.maximum(0, pressure - 1.0))
    net_revenue = weights.nwau_utility * revenue - weights.cost_disutility * cost
    shift_cost = jnp.where(is_shifting, weights.shifting_penalty, 0.0)
    inertia_cost = weights.capacity_inertia_weight * jnp.square(delta_target_capacity)
    return net_revenue - ramping_cost - shift_cost - inertia_cost


@beartype
def state_utility(
    fiscal_gap: Float[Array, ""],
    lhn_performance: Float[Array, ""],  # Mean LHN utility or KPI satisfaction
    weights: AgentWeights,
) -> Float[Array, ""]:
    """
    Utility for the State Agent.
    Focuses on minimizing fiscal gaps (VFI) and maintaining LHN performance.
    """
    vfi_cost = weights.vfi_disutility * jnp.square(jnp.maximum(0, fiscal_gap))
    return weights.kpi_satisfaction * lhn_performance - vfi_cost
