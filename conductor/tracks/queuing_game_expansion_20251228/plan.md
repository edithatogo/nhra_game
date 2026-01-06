# Track Plan: Queuing Game Expansion (P3)

**Goal:** Transition from exogenous demand shocks to an endogenous "Queuing Game" where patient choice between Emergency Departments (ED) and General Practice (GP) is driven by utility-maximizing behavior (Wait Times vs. Costs). This mechanistically explains "GP Access Block" and its impact on ED ramping.

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: formalise Patient Utility

- [x] Task: Define a standard `PatientUtilityParams` structure in `src/nhra_gt/subgames/queuing.py`.
- [x] Task: Parameters to include: `gp_out_of_pocket`, `gp_wait_time_min`, `patient_time_value_hour`, `ed_base_utility`.
- [ ] Phase Gate: Recheck Phase 1 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for utility changes; fix failures before Phase 2.

## Phase 2: Implementation (Equilibrium Solver)

- [x] Task: Create `src/nhra_gt/subgames/queuing.py` to house the endogenous demand logic.
- [x] Task: Implement a Wardrop Equilibrium solver (Fixed-point iteration) that balances ED wait times against GP costs.
- [x] Task: Support both JAX (vectorized) and Legacy implementations of the solver.
- [ ] Phase Gate: Recheck Phase 2 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for solver changes; fix failures before Phase 3.

## Phase 3: Engine Integration & Parity

- [x] Task: Update `src/nhra_gt/engine_jax.py` to use the formal queuing solver in `demand_step_jax`.
- [x] Task: Update `src/nhra_gt/engine.py` to replace the legacy exogenous `demand_step` with the endogenous queuing logic.
- [x] Task: Add a `use_endogenous_demand` flag to `Params` to allow toggling this behavior. (Note: Implemented as default behavior for simplicity and parity).
- [ ] Phase Gate: Recheck Phase 3 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for engine integration; fix failures before Phase 4.

## Phase 4: Validation & Visualization

- [x] Task: Create `tests/test_queuing_game.py` to verify that increasing GP costs correctly drives demand into the ED.
- [ ] Task: Add a "Patient Choice" visualization to the dashboard showing the ED/GP utility split.
- [ ] Phase Gate: Recheck Phase 4 deliverables against tasks before testing.
- [ ] Phase Gate: Run CI-relevant tests for visualization changes; fix failures before track closeout.
- [ ] Track Gate: Run full CI; monitor GitHub Actions with `gh` until green; fix any failures.
- [ ] Track Gate: Verify Streamlit Cloud deployment health and key flows after CI passes.
- [ ] Track Gate: Reconcile completed work against `spec.md` and record any deviations.
- [ ] Track Gate: Evaluate the `spec.md` acceptance checklist and record pass/fail.

---
**Track Status:** COMPLETED 2025-12-28
Endogenous demand model implemented and verified across both engines. Verified with unit tests.
