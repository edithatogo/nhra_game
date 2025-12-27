# Performance Modernization Report
Date: 2025-12-27

| Engine | Method | Time (s) | Speedup |
| :--- | :--- | :--- | :--- |
| NumPy | Sequential | 17.2666 | 1.0x |
| JAX | Single Rollout (jit) | 0.0003 | 59132.1x |
| JAX | Parallel (jit + vmap) | 0.0001 | 240790.1x |

**Benchmark configuration:**
- MC Samples: 1000
- Years: 6
- Platform: cpu
