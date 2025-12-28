# Specification: Auditor Agent & Strategic Inspection

## 1. Overview
Currently, `audit_pressure` is a static parameter. This track replaces it with a **Strategic Auditor Agent** (NHFB/Arbitrator proxy) that adaptively scales inspection intensity based on anomalies in the reported NWAU data.

## 2. Functional Requirements

### FR1: Signal Detection (Anomalies)
- The Auditor monitors the `efficiency_gap` and `reported_nwau` trends.
- Implement a "Signal Quality" check where sudden deviations from historical costs trigger a "Suspicion Index".

### FR2: Adaptive Inspection Intensity
- Implement a JAX-compatible `auditor_move` function.
- If Suspicion Index > threshold, `audit_pressure` increases for the next time step.
- Higher audit pressure leads to higher "Audit Clawbacks" (VFI Leakage).

### FR3: Stochastic Resource Allocation
- The Auditor has a finite inspection budget.
- It must choose which jurisdictions (States) to prioritize based on the magnitude of the anomaly.

## 3. Technical Constraints
- **Differentiability:** The Auditor's response function should be differentiable (using soft-thresholds) to support NumPyro calibration.
- **JAX Core:** Must be implemented using `jax.lax.cond` or `jax.nn.sigmoid` for branching logic.

## 4. Acceptance Criteria
- Verified "Cat and Mouse" dynamics: As States increase efficiency gaps, Auditor pressure rises.
- The dashboard "Forensic Audit" tab shows real-time `Auditor_Suspicion` levels.
