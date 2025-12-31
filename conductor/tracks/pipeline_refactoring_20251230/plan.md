# Track Plan: Pipeline Refactoring & Robustness (20251230)

**Goal:** Modularize the simulation pipeline, implement advanced drift analysis, and ensure robust integration testing.

## Phase 1: Pipeline Modularization
- [ ] **Task 1.1: Refactor Snakemake Logic**
  - [ ] Sub-task: Break down the monolithic `Snakefile` into modular includes.
  - [ ] Sub-task: Standardize input/output paths for all pipeline stages.
- [ ] **Task 1.2: NLP Standardization (SpaCy)**
  - [ ] Sub-task: Integrate SpaCy for systematic evidence extraction and parsing.
  - [ ] Sub-task: Verify NLP performance on sample clinical/policy documents.

## Phase 2: Advanced Process Mining (PM4PY)
- [ ] **Task 2.1: Visualization Mapping**
  - [ ] Sub-task: Systematically map all PM4PY visualizations to project data streams.
  - [ ] Sub-task: Implement core PM4PY visualizations (e.g., process maps, social networks).
- [ ] **Task 2.2: Drift Analysis**
  - [ ] Sub-task: Implement concept drift detection for policy-induced behavioral changes.
  - [ ] Sub-task: Integrate drift alerts into the dashboard.

## Phase 3: Robustness & Integration
- [ ] **Task 3.1: Integration Testing**
  - [ ] Sub-task: Create end-to-end tests for the refactored pipeline.
  - [ ] Sub-task: Verify data integrity across all stages.
- [ ] **Task 3.2: Tidy Up Visualizations**
  - [ ] Sub-task: Clean up and standardize existing visualizations.
  - [ ] Sub-task: Ensure publication-quality output for all new PM4PY plots.
