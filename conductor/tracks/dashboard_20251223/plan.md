# Track Plan: Interactive Web Dashboard (Streamlit)

## Phase 1: Scaffolding, Custom UI & Sidebar
- [x] **Task 1: Dashboard Infrastructure & Polished Theme (TDD)** 9e38b47
  - [x] Sub-task: Write initialization tests for the Streamlit runner.
  - [x] Sub-task: Implement base layout and custom CSS (Teal/Minimalist Academic theme).
- [x] **Task 2: Interactive War Gaming Sidebar** 4b8c57f
  - [x] Sub-task: Write tests for parameter-to-slider mapping logic.
  - [x] Sub-task: Implement categorized sliders (Funding, Operational, Policy, Clinical) with mechanism tooltips.
- [x] **Task: Conductor - User Manual Verification 'Scaffolding & Sidebar' (Protocol in workflow.md)** [checkpoint: 93b6d08]

## Phase 2: Cached Model Engine & Comparison Visuals
- [x] **Task 3: Computational Caching & Hybrid-Fidelity Engine** 15eb83b
  - [x] Sub-task: Implement `st.cache_data` for model rollouts to ensure UI responsiveness.
  - [x] Sub-task: Write tests for the "Low-Latency" rollout interface.
- [x] **Task 4: Scenario Comparison Engine** 967cd4a
  - [x] Sub-task: Write tests for Plotly data frame generation (Baseline vs. War Game).
  - [x] Sub-task: Implement interactive charts meeting MJA academic standards.
- [x] **Task: Conductor - User Manual Verification 'Execution Engine & Plots' (Protocol in workflow.md)** [checkpoint: cfc0c6a]

## Phase 3: Explainability, Lineage & GSA Integration (SOTA)
- [x] **Task 5: Data Provenance Mapping** 376875b
  - [x] Sub-task: Write tests for the lineage lookup logic (mapping parameters back to `context/`).
  - [x] Sub-task: Implement the "Lineage View" in the dashboard.
- [x] **Task 6: Narrative Generator & GSA Integration** cef5bd6
  - [x] Sub-task: Implement rule-based automated prose summary.
  - [x] Sub-task: Integrate Sobol Interaction Heatmaps from previous GSA runs into the \"Analytics\" tab.
- [x] **Task: Conductor - User Manual Verification 'Explainability & Lineage' (Protocol in workflow.md)** [checkpoint: 19f9607]

## Phase 4: Snapshotting & Export
- [~] **Task 7: Scenario Snapshot Suite**
  - [ ] Sub-task: Write tests for JSON serialization of war-game states.
  - [ ] Sub-task: Implement Save/Load functionality.
- [ ] **Task 8: Final Report Export**
  - [ ] Sub-task: Implement academic-standard PDF/PNG download suite.
- [x] **Task: Conductor - User Manual Verification 'Snapshotting & Export' (Protocol in workflow.md)** [checkpoint: 05a961c]
