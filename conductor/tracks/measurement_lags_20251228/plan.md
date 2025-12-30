# Track Plan: Measurement Lags (P3)

**Goal:** Implement information asymmetry and reporting delays ("Measurement Lags") to improve simulation realism, reflecting how policy and strategic decisions are often based on stale data.

## Phase 1: State & Parameter Infrastructure
- [x] Task: Add `signal_lag_months` and `claims_lag_months` to `ParamsJax`.
- [x] Task: Add `lag_buffer_pressure` and `lag_buffer_occupancy` (fixed-size JAX arrays) to `StateJax`.
- [x] Task: Implement `update_lag_buffers` utility in `engine_jax.py`.

## Phase 2: Lagged Decision Logic
- [x] Task: Update `HeuristicAgent` (or its JAX equivalent) to use lagged metrics from the buffers for move selection.
- [x] Task: Update the `Auditor` agent to operate on lagged anomaly signals.
- [x] Task: Implement "Public Signal" release logic where some metrics are only updated in the global state after the lag period.

## Phase 3: Dashboard & Reporting
- [x] Task: Expose lag parameters in the Sidebar.
- [x] Task: Add a "Data Freshness" indicator to the intra-state variance tab. (Implemented via Side-bar and Snapshot)
- [x] Task: Verify that lags increase system oscillations (bullwhip effect) in high-friction scenarios.

## Phase 4: Validation
- [x] Task: Create `tests/test_measurement_lags.py`.
- [x] Task: Ensure parity between JAX and Legacy engines for basic lag logic.

---
**Track Status:** COMPLETED 2025-12-28
Measurement lags implemented across both engines. Agents now make decisions based on reported (lagged) metrics. Verified with unit tests.
