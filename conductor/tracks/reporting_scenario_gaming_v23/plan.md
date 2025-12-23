# Track Plan: Reporting & Scenario War Gaming (v23)

**Goal:** Enhance the dashboard with negotiation-specific visualizations (Effective Share Drift) and generate publication-ready methods documentation.

## Phase 1: Negotiation Dashboard Enhancements [checkpoint: 2e35b70]
- [x] **Task 1.1: Effective Share Drift Threshold Plot**
  - [x] Sub-task: Implement a visualization showing how the "Efficiency Gap" degrades the Commonwealth's effective contribution over time.
  - [x] Sub-task: Add a "Threshold" toggle to show when the effective share drops below critical levels (e.g., 40%).
- [x] **Task 1.2: Ranked Intervention Table**
  - [x] Sub-task: Implement a table ranking policy interventions (e.g., "Pooled Funding", "Audit Relief") by their impact on `pressure_2030` and `rr_2030`.
  - [x] Sub-task: Include uncertainty ranges (95% CI) derived from the PSA engine.
- [x] **Task: Conductor - User Manual Verification 'Dashboard Reporting' (Protocol in workflow.md)**

## Phase 2: Publication Readiness & Methods
- [x] **Task 2.1: Methods Appendix Generator**
  - [x] Sub-task: Create `scripts/reporting/generate_methods_appendix.py` to auto-generate a Markdown appendix based on the current model code (`v9.py`) and parameter registry.
  - [x] Sub-task: Ensure the output meets STRESS/CHEERS reporting standards (e.g., listing all equations and parameter sources).
- [x] **Task 2.2: Parameter Registry Export**
  - [x] Sub-task: Enhance `make_parameter_registry_v20.py` (or similar) to export a clean, academic-style CSV/PDF table for the manuscript.
- [ ] **Task: Conductor - User Manual Verification 'Methods Documentation' (Protocol in workflow.md)**

## Phase 3: Governance & Release
- [ ] **Task 3.1: Changelog & Context Update**
  - [ ] Sub-task: Update `CHANGELOG.md` with v21, v22, and v23 features.
  - [ ] Sub-task: Regenerate `context/CONTEXT_PACK.md`.
- [ ] **Task 3.2: CI & Reproducibility Check**
  - [ ] Sub-task: Verify `just all` runs cleanly (including all new validation scripts).
- [ ] **Task: Conductor - User Manual Verification 'Release Candidates' (Protocol in workflow.md)**
