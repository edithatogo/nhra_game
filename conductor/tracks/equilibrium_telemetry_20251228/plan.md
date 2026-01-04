# Track Plan: Equilibrium Stability Telemetry (P3)

**Goal:** Implement telemetry for the game-theoretic solvers to track "Strategic Volatility" (multiple equilibria) and "Solver Stability" (convergence residuals). This improves model transparency and validates solver robustness.

## Phase 1: Solver Enhancements (Metadata)

- [ ] Task: Update `NashEquilibrium` and solver functions in `src/nhra_gt/subgames/nash.py` to track the number of equilibria found.
- [ ] Task: Update `qre_solver_jax` in `src/nhra_gt/solvers_jax.py` to return the final convergence residual (max delta).
- [ ] Task: Update `regret_min_solver_jax` to return the final regret value.

## Phase 2: State & Agent Infrastructure

- [ ] Task: Add `solver_n_equilibria` and `solver_residual` to `StateJax` and `State`.
- [ ] Task: Update `HeuristicAgent` to capture and store these values during the `decide()` loop.
- [ ] Task: Aggregate stability metrics in `MetricsJax` (e.g., mean residual, max equilibria count).

## Phase 3: Dashboard & Visualization

- [ ] Task: Add a "Strategic Stability" time-series plot to the dashboard.
- [ ] Task: Visualise "Strategic Volatility" (Number of Nash Equilibria found over time).
- [ ] Task: Visualise "Convergence Residuals" for iterative solvers.

## Phase 4: Validation

- [ ] Task: Create `tests/test_solver_telemetry.py`.
- [ ] Task: Verify that "Strategic Volatility" spikes during system transitions (e.g., from Normal to Crisis).

---
**Track Status:** PENDING 2025-12-28
Track initialized to track solver performance and strategic ambiguity.
