"""NHRA Game Theory Simulation Library."""

try:
    import logfire
    logfire.configure(send_to_logfire='if-token-present')
except ImportError:
    pass

from nhra_gt.engine import run_simulation, step
from nhra_gt.hierarchical_jax import solve_constitutional_game_jax

__all__ = ["run_simulation", "step", "solve_constitutional_game_jax"]
