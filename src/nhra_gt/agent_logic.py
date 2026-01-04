"""
Logical Utility Functions for NHRA Agents.

This module defines the utility functions used by LHNs and Jurisdictions to
evaluate their strategic choices. These functions are designed to be
JAX-compatible and differentiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import jax.numpy as jnp
    from jax import lax
except ImportError:  # pragma: no cover
    import numpy as jnp  # type: ignore[no-redef]

    lax = None

try:
    from flax import struct
except ImportError:  # pragma: no cover

    class _Struct:
        """Minimal replacement for flax.struct."""
        dataclass = staticmethod(dataclass)

    struct = _Struct()  # type: ignore[assignment]

try:
    from beartype import beartype as _beartype
except ImportError:  # pragma: no cover
    _beartype = None


def beartype(fn):  # type: ignore[no-untyped-def]
    """Conditional beartype decorator."""
    if _beartype is None:
        return fn
    return _beartype(fn)


@struct.dataclass
class AgentWeights:
    """
    Preference weights for agent utility functions.

    Attributes:
        ramping_penalty: Weight on ED pressure/ramping.
        nwau_utility: Weight on generated revenue.
        cost_disutility: Weight on operational costs.
        shifting_penalty: Friction for switching activity streams.
        capacity_inertia_weight: Cost of changing capacity targets.
        vfi_disutility: State-level penalty for fiscal imbalance.
        kpi_satisfaction: State-level benefit from LHN performance.
    """
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
    pressure: Any,
    revenue: Any,
    cost: Any,
    is_shifting: bool,
    delta_target_capacity: Any,
    weights: AgentWeights,
) -> Any:
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
    fiscal_gap: Any,
    lhn_performance: Any,  # Mean LHN utility or KPI satisfaction
    weights: AgentWeights,
) -> Any:
    """
    Utility for the State Agent.
    Focuses on minimizing fiscal gaps (VFI) and maintaining LHN performance.
    """
    vfi_cost = weights.vfi_disutility * jnp.square(jnp.maximum(0, fiscal_gap))
    return weights.kpi_satisfaction * lhn_performance - vfi_cost
