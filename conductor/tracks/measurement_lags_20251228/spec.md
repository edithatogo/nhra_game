# Track Specification: Measurement Lags (P3)

## 1. Overview

**Goal**: Implement information asymmetry and reporting delays ("Measurement Lags") to improve simulation realism, reflecting how policy and strategic decisions are often based on stale data.
**Context**: Derived from plan phases for measurement_lags_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Add `signal_lag_months` and `claims_lag_months` to `ParamsJax`.
- Add `lag_buffer_pressure` and `lag_buffer_occupancy` (fixed-size JAX arrays) to `StateJax`.
- Implement `update_lag_buffers` utility in `engine_jax.py`.
- Update `HeuristicAgent` (or its JAX equivalent) to use lagged metrics from the buffers for move selection.
- Update the `Auditor` agent to operate on lagged anomaly signals.
- Implement "Public Signal" release logic where some metrics are only updated in the global state after the lag period.

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Dashboard updates reflect new outputs.
- Legacy and JAX implementations remain in parity.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Add `signal_lag_months` and `claims_lag_months` to `ParamsJax`.
- [ ] Add `lag_buffer_pressure` and `lag_buffer_occupancy` (fixed-size JAX arrays) to `StateJax`.
- [ ] Implement `update_lag_buffers` utility in `engine_jax.py`.
- [ ] Update `HeuristicAgent` (or its JAX equivalent) to use lagged metrics from the buffers for move selection.
- [ ] Relevant tests pass for track changes.
- [ ] Dashboard reflects the new outputs or views.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
