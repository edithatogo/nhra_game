# Track Plan: Pipeline Refactoring & Robustness (20251230)

**Goal:** Modularize the simulation pipeline and ensure robust integration testing. (Process Mining phase cancelled).

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Pipeline Modularization [checkpoint: 106f600]

- [x] **Task 1.1: Refactor Snakemake Logic** (106f600)
- [x] **Task 1.2: NLP Standardization (SpaCy)** (106f600)
- [x] Phase Gate: Recheck Phase 1 deliverables against tasks before testing.
- [x] Phase Gate: Run CI-relevant tests for pipeline refactor; fix failures before Phase 3.

## Phase 2: Process Mining (Cancelled)

- [ ] Task: Visualization Mapping (Cancelled)
- [ ] Task: Drift Analysis (Cancelled)

## Phase 3: Robustness & Integration

- [x] **Task 3.1: Integration Testing**
  - [x] Sub-task: Create end-to-end tests for the refactored pipeline.
  - [x] Sub-task: Verify data integrity across all stages.
- [x] Phase Gate: Recheck Phase 3 deliverables against tasks before testing.
- [x] Phase Gate: Run CI-relevant tests for integration; fix failures before track closeout.
- [x] Track Gate: Run full CI; monitor GitHub Actions with `gh` until green; fix any failures.
- [x] Track Gate: Verify Streamlit Cloud deployment health and key flows after CI passes.
- [x] Track Gate: Reconcile completed work against `spec.md` and record any deviations.
- [x] Track Gate: Evaluate the `spec.md` acceptance checklist and record pass/fail.

## Phase 4: Error Reconciliation & Deprecation Analysis

- [x] **Task 4.1: Review commented code for dropped functionality.**
    - [x] Subtask 4.1.1: Identify all commented-out code blocks.
    - [x] Subtask 4.1.2: Analyze context for potential re-integration.
    - [x] Subtask 4.1.3: Document findings and proposed actions.
- [x] **Task 4.2: Refine Vulture & Deptry usage.**
    - [x] Subtask 4.2.1: Configure Vulture for "report-only" mode.
    - [x] Subtask 4.2.2: Configure Deptry for "deprecations" focus.
    - [x] Subtask 4.2.3: Implement manual review workflow for findings.
- [x] **Task 4.3: Update documentation.**
    - [x] Subtask 4.3.1: Document new phase and review process.
    - [x] Subtask 4.3.2: Update Vulture/Deptry configuration guidelines.
