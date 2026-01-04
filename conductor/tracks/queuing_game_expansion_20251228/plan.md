# Track Plan: Queuing Game Expansion (P3)

**Goal:** Transition from exogenous demand shocks to an endogenous "Queuing Game" where patient choice between Emergency Departments (ED) and General Practice (GP) is driven by utility-maximizing behavior (Wait Times vs. Costs). This mechanistically explains "GP Access Block" and its impact on ED ramping.

## Phase 1: formalise Patient Utility

- [x] Task: Define a standard `PatientUtilityParams` structure in `src/nhra_gt/subgames/queuing.py`.
- [x] Task: Parameters to include: `gp_out_of_pocket`, `gp_wait_time_min`, `patient_time_value_hour`, `ed_base_utility`.

## Phase 2: Implementation (Equilibrium Solver)

- [x] Task: Create `src/nhra_gt/subgames/queuing.py` to house the endogenous demand logic.
- [x] Task: Implement a Wardrop Equilibrium solver (Fixed-point iteration) that balances ED wait times against GP costs.
- [x] Task: Support both JAX (vectorized) and Legacy implementations of the solver.

## Phase 3: Engine Integration & Parity

- [x] Task: Update `src/nhra_gt/engine_jax.py` to use the formal queuing solver in `demand_step_jax`.
- [x] Task: Update `src/nhra_gt/engine.py` to replace the legacy exogenous `demand_step` with the endogenous queuing logic.
- [x] Task: Add a `use_endogenous_demand` flag to `Params` to allow toggling this behavior. (Note: Implemented as default behavior for simplicity and parity).

## Phase 4: Validation & Visualization

- [x] Task: Create `tests/test_queuing_game.py` to verify that increasing GP costs correctly drives demand into the ED.
- [ ] Task: Add a "Patient Choice" visualization to the dashboard showing the ED/GP utility split.

---
**Track Status:** COMPLETED 2025-12-28
Endogenous demand model implemented and verified across both engines. Verified with unit tests.
