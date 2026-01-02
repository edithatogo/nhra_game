# Implementation Plan: Dashboard & Engine Integration Audit

This plan focuses on deep forensic code analysis to validate feature integration.

## Phase 1: Codebase Investigation (Audit Phase)
Goal: Use the investigator agent to trace data paths and identify mocks.

- [x] **Task: Conductor - User Manual Verification 'Phase 1 Initial State' (Protocol in workflow.md)**
- [x] **Task: Investigate Evidence Manager Integration**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to check if `scripts/dashboard.py` reads/writes to `context/04_parameter_registry.csv` or uses `ParamsJax.replace`.
    - [x] **Save Output:** Ensure the agent's JSON output is saved to `reports/audit/evidence_manager_audit.json`.
- [x] **Task: Investigate LHN Variance Integration**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to trace the source of the "Variance" plot data. Does it come from `traj["lhn_pressure"]` (vector) or a helper function generating noise?
    - [x] **Save Output:** Save to `reports/audit/lhn_variance_audit.json`.
- [x] **Task: Investigate Sequential Bargaining UI**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to see if the `use_sequential_bargaining` parameter is exposed in the Sidebar or Scenario config.
    - [x] **Save Output:** Save to `reports/audit/sequential_ui_audit.json`.
- [x] **Task: Conductor - User Manual Verification 'Phase 1 Completion' (Protocol in workflow.md)**

## Phase 2: Reporting & Synthesis (Reporting Phase)
Goal: Consolidate findings into a decision-grade report.

- [ ] **Task: Compile Summary Report**
    - [ ] Write `reports/audit/dashboard_integration_summary.md`.
    - [ ] Categorize each feature (Green/Amber/Red).
- [ ] **Task: Conductor - User Manual Verification 'Phase 2 Completion' (Protocol in workflow.md)**
