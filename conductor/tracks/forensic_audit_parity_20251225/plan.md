# Plan: Forensic Parity Audit & Feature Recovery

## Phase 1: Automated Parity Baseline [checkpoint: 50314e5]
- [x] Task: Create Parity Regression Utility
    - [x] Sub-task: Develop `tests/test_dashboard_parity.py` to compare trajectories between `engine.py` and `dashboard_v21.py` logic.
    - [x] Sub-task: Audit statistical divergence between "Lite" (50 MC) and "Full" (1000 MC) modes.
- [x] Task: Conductor - User Manual Verification 'Automated Parity Baseline' (Protocol in workflow.md)

## Phase 2: Feature & Logic Audit
- [x] Task: Audit Strategic Games & Network
    - [x] Sub-task: Map `games.py` logic to dashboard selection menus. (Found: Dashboard uses indirect policy interventions instead of game selection)
    - [x] Sub-task: Verify Graphviz/Mermaid network consistency in the UI. (Found: Interactive network visualization is missing from the dashboard)
- [x] Task: Audit Sensitivity & Calibration
    - [x] Sub-task: Verify Sobol/Morris data ingestion in the dashboard. (Found: Morris is present, Sobol/Heatmaps are missing)
    - [x] Sub-task: Confirm validation metrics visibility. (Found: Error metrics and Ghost overlays are functional)
- [ ] Task: Conductor - User Manual Verification 'Feature & Logic Audit' (Protocol in workflow.md)

## Phase 3: Dashboard Hardening & Forensic UI
- [ ] Task: Implement Forensic Debug Mode
    - [ ] Sub-task: Add a "Developer/Forensic" tab to the Streamlit dashboard.
    - [ ] Sub-task: Display raw `State` dictionary and seed information.
- [ ] Task: Redundancy Cleanup
    - [ ] Sub-task: Remove legacy components and dead links.
- [ ] Task: Conductor - User Manual Verification 'Dashboard Hardening & Forensic UI' (Protocol in workflow.md)

## Phase 4: Final Reporting & Roadmap Update
- [ ] Task: Generate Audit Report
    - [ ] Sub-task: Compile findings into `reports/parity_audit_20251225.md`.
- [ ] Task: Update Roadmap
    - [ ] Sub-task: Propose recovery tasks for any "Deep" features found missing.
- [ ] Task: Conductor - User Manual Verification 'Final Reporting & Roadmap Update' (Protocol in workflow.md)