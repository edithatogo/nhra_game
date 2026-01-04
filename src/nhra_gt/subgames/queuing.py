"""
Patient Queuing Game and Wardrop Equilibrium Solver.

This module models the choice patients make between attending an Emergency
Department (ED) or a General Practitioner (GP), based on expected wait times
and out-of-pocket costs. It uses fixed-point iteration to find the equilibrium
demand levels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

try:
    import jax
    import jax.numpy as jnp
except ImportError:  # pragma: no cover
    jax = None  # type: ignore[assignment]
    jnp = np  # type: ignore[assignment]

try:
    from beartype import beartype as _beartype
    from jaxtyping import Array, Float
except ImportError:  # pragma: no cover
    Array = Any  # type: ignore[assignment]
    Float = Any  # type: ignore[assignment]
    _beartype = None


def beartype(fn):  # type: ignore[no-untyped-def]
    """Conditional beartype decorator."""
    if _beartype is None:
        return fn
    return _beartype(fn)


@dataclass(frozen=True)
class PatientUtilityParams:
    """
    Parameters defining patient choice utility.

    Attributes:
        gp_out_of_pocket: Financial cost of GP visit ($).
        gp_wait_time_min: Expected wait time for GP (minutes).
        patient_time_value_hour: Shadow price of patient time ($/hr).
        ed_base_utility: Intrinsic utility of ED (e.g. equipment access).
        logit_sensitivity: Rationality parameter for logit choice.
    """

    gp_out_of_pocket: float = 40.0
    gp_wait_time_min: float = 15.0
    patient_time_value_hour: float = 25.0
    ed_base_utility: float = 0.0  # ED is "free" but has other disutilities (travel, etc.)
    logit_sensitivity: float = 0.1


@beartype
def calculate_patient_utilities(ed_wait_min: Any, p: PatientUtilityParams) -> tuple[Any, Any]:
    """
    Calculates utilities for choosing ED vs GP.

    Returns:
        Tuple of (utility_ed, utility_gp).
    """
    u_ed = p.ed_base_utility - (ed_wait_min / 60.0 * p.patient_time_value_hour)
    u_gp = jnp.array(-(p.gp_wait_time_min / 60.0 * p.patient_time_value_hour) - p.gp_out_of_pocket)
    return u_ed, u_gp


@beartype
def solve_queuing_equilibrium_jax(
    total_base_demand: Any,
    capacity: Any,
    discharge_delay: Any,
    params: PatientUtilityParams,
    max_iter: int = 5,
) -> tuple[Any, Any]:
    """
    Finds the Wardrop Equilibrium for patient demand using fixed-point iteration.
    Returns (demand_ed, prob_ed).
    """
    if jax is None:  # pragma: no cover
        raise ImportError("`solve_queuing_equilibrium_jax` requires `jax` to be installed.")
    from jax import lax

    from nhra_gt.engine import mm_s_queue_wait_jax

    def body_fun(i, state):
        d_curr, _ = state
        # 1. Calculate resulting wait time at current demand
        wait_min = mm_s_queue_wait_jax(
            d_curr, 1.0 / jnp.maximum(1e-9, discharge_delay), jnp.array(capacity * 10.0)
        )

        # 2. Calculate utilities
        u_ed, u_gp = calculate_patient_utilities(wait_min, params)

        # 3. Logit choice (ED vs GP vs Outside Option)
        u_outside = -100.0  # Unattractive outside option
        logits = jnp.array([u_ed, u_gp, u_outside])
        prob_ed = jax.nn.softmax(logits * params.logit_sensitivity)[0]

        # 4. Resulting demand
        return total_base_demand * prob_ed, prob_ed

    # JIT-friendly loop
    d_final, p_final = lax.fori_loop(
        0, max_iter, body_fun, (jnp.array(total_base_demand), jnp.array(0.5))
    )

    return d_final, p_final


def solve_queuing_equilibrium_legacy(
    total_base_demand: float,
    capacity: float,
    discharge_delay: float,
    params: PatientUtilityParams,
    max_iter: int = 5,
) -> tuple[float, float]:
    """Legacy version of the queuing solver. Returns (demand_ed, prob_ed)."""
    from nhra_gt.engine import mm_s_queue_wait

    p_final = 0.5
    d_final = total_base_demand
    for _ in range(max_iter):
        wait_min = mm_s_queue_wait(d_final, 1.0 / max(1e-9, discharge_delay), capacity * 10.0)

        # Utilities
        u_ed = params.ed_base_utility - (wait_min / 60.0 * params.patient_time_value_hour)
        u_gp = (
            -(params.gp_wait_time_min / 60.0 * params.patient_time_value_hour)
            - params.gp_out_of_pocket
        )
        u_outside = -100.0

        # Logit
        e_ed = np.exp(u_ed * params.logit_sensitivity)
        e_gp = np.exp(u_gp * params.logit_sensitivity)
        e_out = np.exp(u_outside * params.logit_sensitivity)

        prob_ed = e_ed / (e_ed + e_gp + e_out)
        d_final = total_base_demand * float(prob_ed)
        p_final = float(prob_ed)

    return d_final, p_final
