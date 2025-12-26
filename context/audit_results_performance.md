# Audit Report: Performance Bottlenecks

**Date:** 2025-12-26

## 1. Summary

Profiling was performed using `pyinstrument` on the `scripts/run_baseline.py` simulation. The primary bottleneck is the Nash Equilibrium solver used in every simulation step.

## 2. Bottleneck Analysis

### A. Nash Equilibrium Solver (`all_nash`)

* **Impact:** ~74% of total execution time.
* **Location:** `nhra_gt/subgames/nash.py`
* **Internal Drivers:**
  * `pure_nash` (~49%): Spends most of its time in `_best_responses_row/col`.
  * `mixed_nash_2x2` (~13%).
* **Root Cause:** Heavy reliance on **`numpy.isclose`** for scalar comparisons. `numpy.isclose` is highly flexible but significantly slower than simple scalar comparisons (`abs(a-b) < tol`) when called millions of times in a loop.

### B. Agent Decision Logic (`HeuristicAgent.decide`)

* **Impact:** ~83% of `run_hybrid` (which includes the Nash solver overhead).
* **Observation:** The simulation spends nearly all its time "thinking" (solving games) rather than "moving" (the `engine.py::step` transition logic is only ~2.6%).

## 3. Recommendations

1. **Optimise `isclose`:** Replace `np.isclose` with a simple scalar tolerance check in `nash.py` since the matrices are small (2x2).
2. **Memoization:** Implement caching (memoization) for the Nash solver. Since many simulation steps involve similar parameter inputs (and thus similar payoff matrices), caching the results of `all_nash(u_row, u_col)` for discretized matrix values could yield a 10x speedup.
3. **Vectorization:** If memoization is insufficient, consider vectorizing the Nash solver to process multiple Monte Carlo rollouts or timesteps simultaneously using JAX or NumPy broadcasting.
