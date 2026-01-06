# Track Specification: Queuing Game Expansion (P3)

## 1. Overview

**Goal**: Transition from exogenous demand shocks to an endogenous "Queuing Game" where patient choice between Emergency Departments (ED) and General Practice (GP) is driven by utility-maximizing behavior (Wait Times vs. Costs). This mechanistically explains "GP Access Block" and its impact on ED ramping.
**Context**: Derived from plan phases for queuing_game_expansion_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Define a standard `PatientUtilityParams` structure in `src/nhra_gt/subgames/queuing.py`.
- Parameters to include: `gp_out_of_pocket`, `gp_wait_time_min`, `patient_time_value_hour`, `ed_base_utility`.
- Create `src/nhra_gt/subgames/queuing.py` to house the endogenous demand logic.
- Implement a Wardrop Equilibrium solver (Fixed-point iteration) that balances ED wait times against GP costs.
- Support both JAX (vectorized) and Legacy implementations of the solver.
- Update `src/nhra_gt/engine_jax.py` to use the formal queuing solver in `demand_step_jax`.

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Dashboard updates reflect new outputs.
- Legacy and JAX implementations remain in parity.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Define a standard `PatientUtilityParams` structure in `src/nhra_gt/subgames/queuing.py`.
- [ ] Parameters to include: `gp_out_of_pocket`, `gp_wait_time_min`, `patient_time_value_hour`, `ed_base_utility`.
- [ ] Create `src/nhra_gt/subgames/queuing.py` to house the endogenous demand logic.
- [ ] Implement a Wardrop Equilibrium solver (Fixed-point iteration) that balances ED wait times against GP costs.
- [ ] Relevant tests pass for track changes.
- [ ] Dashboard reflects the new outputs or views.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
