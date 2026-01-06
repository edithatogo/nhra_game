# Track Plan: Equilibrium Stability Telemetry (P3)

**Goal:** Implement telemetry for the game-theoretic solvers to track "Strategic Volatility" (multiple equilibria) and "Solver Stability" (convergence residuals). This improves model transparency and validates solver robustness.

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Solver Enhancements (Metadata)

- [ ] Task: Update `NashEquilibrium` and solver functions in `src/nhra_gt/subgames/nash.py` to track the number of equilibria found.
- [ ] Task: Update `qre_solver_jax` in `src/nhra_gt/solvers_jax.py` to return the final convergence residual (max delta).
- [ ] Task: Update `regret_min_solver_jax` to return the final regret value.
- [ ] Phase Gate: Recheck Phase 1 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for solver changes; fix failures before Phase 2.

## Phase 2: State & Agent Infrastructure

- [ ] Task: Add `solver_n_equilibria` and `solver_residual` to `StateJax` and `State`.
- [ ] Task: Update `HeuristicAgent` to capture and store these values during the `decide()` loop.
- [ ] Task: Aggregate stability metrics in `MetricsJax` (e.g., mean residual, max equilibria count).
- [ ] Phase Gate: Recheck Phase 2 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for state/agent changes; fix failures before Phase 3.

## Phase 3: Dashboard & Visualization

- [ ] Task: Add a "Strategic Stability" time-series plot to the dashboard.
- [ ] Task: Visualise "Strategic Volatility" (Number of Nash Equilibria found over time).
- [ ] Task: Visualise "Convergence Residuals" for iterative solvers.
- [ ] Phase Gate: Recheck Phase 3 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for dashboard changes; fix failures before Phase 4.

## Phase 4: Validation

- [ ] Task: Create `tests/test_solver_telemetry.py`.
- [ ] Task: Verify that "Strategic Volatility" spikes during system transitions (e.g., from Normal to Crisis).
- [ ] Phase Gate: Recheck Phase 4 deliverables against tasks before testing.
- [ ] Track Gate: Run full CI; monitor GitHub Actions with `gh` until green; fix any failures.
- [ ] Track Gate: Verify Streamlit Cloud deployment health and key flows after CI passes.
- [ ] Track Gate: Reconcile completed work against `spec.md` and record any deviations.
- [ ] Track Gate: Evaluate the `spec.md` acceptance checklist and record pass/fail.

---
**Track Status:** PENDING 2025-12-28
Track initialized to track solver performance and strategic ambiguity.
