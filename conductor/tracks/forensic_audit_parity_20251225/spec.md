# Specification: Forensic Parity Audit & Feature Recovery

## 1. Overview
This track is a comprehensive audit to determine the extent of alignment between the underlying simulation codebase (`src/`, `scripts/`) and the user-facing Streamlit dashboard (`scripts/dashboard_v21.py`). The goal is to identify lost or missing features, ensure functional parity, and verify visual consistency across all model outputs.

## 2. Functional Requirements

### A) Strategic Games Audit
- Verify that all games defined in `src/nhra_game_theory/subgames/games.py` (Bargaining, Compliance, Cost Shifting, Definition, Discharge, Governance) are selectable and correctly parameterized in the dashboard.
- Ensure the "Strategic Map" visualization in the dashboard matches the logic and connectivity of the codebase's strategic network.

### B) Simulation Trajectories Audit
- Confirm that the dashboard's Monte Carlo rollout logic matches `src/nhra_game_theory/engine.py`.
- Verify that quantile ribbons and mean trajectories in dashboard plots are consistent with the static publication figures.
- **MC Convergence Audit:** Audit whether the dashboard's "lite" interactive results (e.g., 50 samples) significantly diverge from production results (e.g., 1000 samples).

### C) Sensitivity Analysis Audit
- Audit the integration of Sobol indices, Morris tornado plots, and interaction heatmaps into the dashboard.
- Ensure that the dashboard correctly consumes the outputs of the GSA pipeline (`data/gsa_v21/`).

### D) Calibration & Validation Audit
- Verify that calibration outputs (Objective function surfaces, posterior distributions) are visible and accurate in the dashboard.
- Ensure backtesting metrics (Theil U, etc.) from `scripts/validation/` are reflected in the UI.

### E) Documentation & Provenance Audit
- Check that the Parameter Registry and evidence grounding links are accessible via the dashboard.
- Verify the integration of the "Context Pack" (`context/CONTEXT_PACK.md`) into the UI for user reference.

### F) Redundancy Cleanup
- Identify and document dashboard components that reference legacy or deleted files.
- Remove or update "dead" UI elements that no longer have underlying logic support.

### G) Forensic Tools
- **Forensic Debug Mode:** Implement a mode in the dashboard that displays the raw `State` dictionary at each step for direct comparison with CLI logs.
- **Automated Parity Verification:** Implement a regression script (`tests/test_dashboard_parity.py`) that compares outputs between the core engine and dashboard logic.

## 3. Non-Functional Requirements
- **Surgical Fixes:** If missing features are found that can be recovered with minimal effort, perform surgical implementation.
- **Reporting:** Generate a detailed audit report (`reports/parity_audit_20251225.md`) documenting all gaps found.
- **Style Consistency:** Dashboard visualizations must adhere to the project's color palette and formatting rules.

## 4. Acceptance Criteria
- [ ] A comprehensive audit report is generated.
- [ ] All "Quick Fix" parity gaps (e.g., missing labels, broken links) are resolved.
- [ ] Functional parity is verified for the core simulation loop.
- [ ] Automated parity verification script is passing.
- [ ] A prioritized plan for "Deep" feature recovery is added to the main roadmap.

## 5. Out of Scope
- Implementing large-scale new features not previously present in the codebase.
- Migrating the dashboard to a different framework (e.g., from Streamlit to Dash).