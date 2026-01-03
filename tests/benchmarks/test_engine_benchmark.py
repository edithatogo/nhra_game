import jax
import jax.numpy as jnp
from nhra_gt.engine import run_simulation_jax, baseline_state, ParamsJax


def test_simulation_performance(benchmark):
    """Benchmark the JAX-native simulation engine."""
    params = ParamsJax()
    init_state = baseline_state(2025, params)
    num_steps = 120  # 10 years
    strategies = jnp.zeros((num_steps, 13))
    key = jax.random.PRNGKey(42)

    # Pre-compile to ensure we benchmark execution time, not compilation
    _ = run_simulation_jax(init_state, params, strategies, key, num_steps)

    # Benchmark
    # We use a lambda to ensure the function is called exactly as expected
    def run():
        f, t = run_simulation_jax(init_state, params, strategies, key, num_steps)
        f.pressure.block_until_ready()
        return f

    benchmark(run)
