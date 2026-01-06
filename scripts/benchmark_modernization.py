"""Benchmarks performance of the JAX simulation engine."""

import time

import jax
import jax.numpy as jnp

from nhra_gt.domain.state import ParamsJax
from nhra_gt.engine import (
    baseline_state,
    run_hybrid,
    run_simulation_jax,
)


def benchmark() -> None:
    """Execute performance benchmarks comparing NumPy and JAX."""
    years = list(range(2025, 2031))
    num_months = len(years) * 12
    n_mc = 1000

    print(f"🚀 Benchmarking NHRA Engine (Years={len(years)}, MC Samples={n_mc})")
    print("-" * 50)

    # 1. NumPy Baseline
    from nhra_gt.domain.params import Params as ParamsNP

    p_np = ParamsNP()
    start = time.perf_counter()
    run_hybrid(years, p_np, n_mc=n_mc, seed=42)
    duration_np = time.perf_counter() - start
    print(f"NumPy (Baseline): {duration_np:.4f}s")

    # 2. JAX CPU (Single Rollout)
    pj = ParamsJax()
    sj = baseline_state(2025, pj)
    strat = jnp.zeros((num_months, 13))
    key = jax.random.PRNGKey(42)

    # Warmup
    jax.jit(run_simulation_jax, static_argnums=(4,))(sj, pj, strat, key, num_months)

    start = time.perf_counter()
    jax.jit(run_simulation_jax, static_argnums=(4,))(sj, pj, strat, key, num_months)
    duration_jax_single = time.perf_counter() - start
    print(f"JAX CPU (Single Rollout): {duration_jax_single:.4f}s")

    # 3. JAX CPU (Parallelized vmap)
    keys = jax.random.split(key, n_mc)

    @jax.jit
    def vmap_run(ks):
        def _one(k):
            return run_simulation_jax(sj, pj, strat, k, num_months)

        return jax.vmap(_one)(ks)

    # Warmup
    vmap_run(keys)

    start = time.perf_counter()
    vmap_run(keys)
    duration_jax_vmap = time.perf_counter() - start
    print(f"JAX CPU (vmap {n_mc} samples): {duration_jax_vmap:.4f}s")

    # Summary
    speedup = duration_np / duration_jax_vmap
    print("-" * 50)
    print(f"✅ Total Speedup: {speedup:.1f}x")

    # Save results
    report = f"""# Performance Modernization Report
Date: 2025-12-27

| Engine | Mode | Duration (s) | Speedup |
| :--- | :--- | :--- | :--- |
| NumPy | Sequential | {duration_np:.4f} | 1.0x |
| JAX | Single Rollout (jit) | {duration_jax_single:.4f} | {duration_np / duration_jax_single:.1f}x |
| JAX | Parallel (jit + vmap) | {duration_jax_vmap:.4f} | {speedup:.1f}x |
"""
    with open("reports/performance_modernization.md", "w") as f:
        f.write(report)


if __name__ == "__main__":
    benchmark()
