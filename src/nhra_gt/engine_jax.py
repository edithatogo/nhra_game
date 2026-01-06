"""Compatibility layer for historical `engine_jax` imports.

The core JAX implementation lives in `nhra_gt.engine`. Older code and tests
expect `nhra_gt.engine_jax` to exist and to expose `*_jax` entry points.
"""

from __future__ import annotations

from nhra_gt.domain.state import ParamsJax, StateJax
from nhra_gt.engine import baseline_state, lhn_step_jax, run_simulation_jax, step_jax


def baseline_state_jax(start_year: int = 2025, p: ParamsJax | None = None) -> StateJax:
    """Return the JAX baseline state for simulation initialization."""
    return baseline_state(start_year=start_year, p=p)


__all__ = [
    "ParamsJax",
    "StateJax",
    "baseline_state_jax",
    "lhn_step_jax",
    "run_simulation_jax",
    "step_jax",
]
