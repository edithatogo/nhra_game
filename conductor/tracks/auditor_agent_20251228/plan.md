# Implementation Plan: Auditor Agent & Strategic Inspection

## Phase 1: Signal & Suspicion Logic [checkpoint: 209b40b]
- [x] Task: Update `StateJax` to include `auditor_suspicion` and `audit_pressure_active`.
- [x] Task: Implement `calculate_suspicion_index` in `src/nhra_gt/engine_jax.py`.

## Phase 2: Auditor Strategic Move [checkpoint: 209b40b]
- [x] Task: Implement `auditor_step_jax` in JAX.
- [x] Task: Link Auditor move to the `calculate_vfi_waterfall` logic (increasing clawbacks).

## Phase 3: Integration & Dashboard [checkpoint: 209b40b]
- [x] Task: Add Auditor telemetry to simulation outputs.
- [x] Task: Update dashboard with Auditor suspicion indicators.
- [x] Task: Final verification with new test suite `tests/test_auditor_behavior.py`.
