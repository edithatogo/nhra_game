# Implementation Plan: Auditor Agent & Strategic Inspection

## Phase 1: Signal & Suspicion Logic
- [ ] Task: Update `StateJax` to include `auditor_suspicion` and `audit_pressure_active`.
- [ ] Task: Implement `calculate_suspicion_index` in `src/nhra_gt/engine_jax.py`.

## Phase 2: Auditor Strategic Move
- [ ] Task: Implement `auditor_step` in JAX.
- [ ] Task: Link Auditor move to the `calculate_vfi_waterfall` logic (increasing clawbacks).

## Phase 3: Integration & Dashboard
- [ ] Task: Add Auditor telemetry to simulation outputs.
- [ ] Task: Update dashboard with Auditor suspicion indicators.
- [ ] Task: Final verification with new test suite `tests/test_auditor_behavior.py`.
