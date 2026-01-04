"""NHRA Game Theory Simulation Library."""

try:
    import logfire

    logfire.configure(send_to_logfire="if-token-present")
except ImportError:
    pass

from nhra_gt.engine import run_simulation, step
from nhra_gt.hierarchical_jax import solve_constitutional_game_jax

__version__ = "26.0.1"
__all__ = ["__version__", "run_simulation", "solve_constitutional_game_jax", "step"]
