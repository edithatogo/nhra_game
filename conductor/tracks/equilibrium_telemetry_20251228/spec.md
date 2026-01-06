# Track Specification: Equilibrium Stability Telemetry (P3)

## 1. Overview

**Goal**: Implement telemetry for the game-theoretic solvers to track "Strategic Volatility" (multiple equilibria) and "Solver Stability" (convergence residuals). This improves model transparency and validates solver robustness.
**Context**: Derived from plan phases for equilibrium_telemetry_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Update `NashEquilibrium` and solver functions in `src/nhra_gt/subgames/nash.py` to track the number of equilibria found.
- Update `qre_solver_jax` in `src/nhra_gt/solvers_jax.py` to return the final convergence residual (max delta).
- Update `regret_min_solver_jax` to return the final regret value.
- Add `solver_n_equilibria` and `solver_residual` to `StateJax` and `State`.
- Update `HeuristicAgent` to capture and store these values during the `decide()` loop.
- Aggregate stability metrics in `MetricsJax` (e.g., mean residual, max equilibria count).

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Dashboard updates reflect new outputs.
- Performance/stability expectations are met.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Update `NashEquilibrium` and solver functions in `src/nhra_gt/subgames/nash.py` to track the number of equilibria found.
- [ ] Update `qre_solver_jax` in `src/nhra_gt/solvers_jax.py` to return the final convergence residual (max delta).
- [ ] Update `regret_min_solver_jax` to return the final regret value.
- [ ] Add `solver_n_equilibria` and `solver_residual` to `StateJax` and `State`.
- [ ] Relevant tests pass for track changes.
- [ ] Dashboard reflects the new outputs or views.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
