from __future__ import annotations

import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp

# Add src
sys.path.append("src")

from nhra_gt.engine import Params, baseline_state, run_simulation_jax
from nhra_gt.engine import Params as ParamsNp
from nhra_gt.engine import run_hybrid as run_hybrid_np


def benchmark():
    years = list(range(2025, 2031))
    num_months = len(years) * 12
    n_mc = 1000

    print(f"🚀 Benchmarking NHRA Engine (Years={len(years)}, MC Samples={n_mc})")
    print("-" * 50)

    # 1. NumPy Baseline
    p_np = ParamsNp()
    start = time.perf_counter()
    run_hybrid_np(years, p_np, n_mc=n_mc, seed=42)
    duration_np = time.perf_counter() - start
    print(f"NumPy (Baseline): {duration_np:.4f}s")

    # 2. JAX CPU (Single Rollout)
    pj = Params()
    sj = baseline_state(start_year=2025, p=pj)
    strat = jnp.zeros((num_months, 10))
    key = jax.random.PRNGKey(42)

    # Warmup
    jax.jit(run_simulation_jax, static_argnums=(4,))(sj, pj, strat, key, num_months)

    start = time.perf_counter()
    jax.jit(run_simulation_jax, static_argnums=(4,))(sj, pj, strat, key, num_months)
    duration_jax_single = time.perf_counter() - start
    print(f"JAX CPU (Single Rollout): {duration_jax_single:.4f}s")

    # 3. JAX CPU (Parallelized vmap)
    # vmap over keys for different rollouts
    keys = jax.random.split(key, n_mc)

    vmap_run = jax.jit(jax.vmap(lambda k: run_simulation_jax(sj, pj, strat, k, num_months)))

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
    report_path = Path("reports/performance_modernization.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        f"""# Performance Modernization Report
Date: 2025-12-27

| Engine | Method | Time (s) | Speedup |
| :--- | :--- | :--- | :--- |
| NumPy | Sequential | {duration_np:.4f} | 1.0x |
| JAX | Single Rollout (jit) | {duration_jax_single:.4f} | {duration_np / duration_jax_single:.1f}x |
| JAX | Parallel (jit + vmap) | {duration_jax_vmap:.4f} | {speedup:.1f}x |

**Benchmark configuration:**
- MC Samples: {n_mc}
- Years: {len(years)}
- Platform: {jax.devices()[0].platform}
"""
    )


if __name__ == "__main__":
    benchmark()
