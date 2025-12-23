# Track Plan: Automated Data Pipelines & Evidence Manager

## Phase 1: Registry Core & Structured Ingestion
- [x] **Task 1: Evidence Registry Schema & Data Model (TDD)** cce3fe2
  - [ ] Sub-task: Write tests for the `Registry` class (CSV/JSON persistence, schema validation).
  - [ ] Sub-task: Implement uncertainty-aware schema (mean, 95% CI, NHMRC grading) in `src/nhra_game_theory/domain/registry.py`.
- [x] **Task 2: Structured Data Ingestors (AIHW/ABS/IHACPA)** 2ace7de
  - [ ] Sub-task: Write tests for deterministic scrapers/parsers.
  - [ ] Sub-task: Implement `scripts/ingest_structured.py` to fetch and stage metrics from primary Australian sources.
- [x] **Task 3: Unit Safety & Sanity Checks** 1684eb2
  - [ ] Sub-task: Implement automated variance flagging (e.g., alert if new data deviates >50% from baseline).
- [x] **Task: Conductor - User Manual Verification 'Registry Core' (Protocol in workflow.md)** [checkpoint: 50b7cde]

## Phase 2: Hybrid Literature Extraction & Document Integrity
- [ ] **Task 4: Robust PDF Table Extraction & Hashing**
  - [ ] Sub-task: Implement SHA-256 document hashing for source archival and reproducibility.
  - [ ] Sub-task: Implement `scripts/extract_tables.py` using `PyMuPDF` or `Camelot`.
- [ ] **Task 5: Schema-Constrained LLM Parsing**
  - [ ] Sub-task: Implement LLM prompt engineering to map raw table text to the Registry schema.
  - [ ] Sub-task: Write tests to verify extraction of Confidence Intervals and NHMRC grades.
- [ ] **Task: Conductor - User Manual Verification 'Literature Extraction' (Protocol in workflow.md)**

## Phase 3: Evidence Manager Dashboard & Stochastic Tuning
- [ ] **Task 6: Audit, Promotion & Stochastic Mapping**
  - [ ] Sub-task: Implement the "Evidence Manager" tab in `scripts/dashboard_v21.py`.
  - [ ] Sub-task: Map extracted 95% CIs to parameter-specific simulation noise (replacing global `noise_sd`).
- [ ] **Task 7: Conflict Resolution & Consensus UI**
  - [ ] Sub-task: Implement side-by-side comparison for conflicting parameters.
  - [ ] Sub-task: Implement "Select Source" or "Weighted Average" logic.
- [ ] **Task: Conductor - User Manual Verification 'Dashboard UI' (Protocol in workflow.md)**

## Phase 4: Publication Reporting & Calibration Loop Closure
- [ ] **Task 8: Automated Evidence Grounding Report**
  - [ ] Sub-task: Implement Markdown generator for the MJA appendix (including NHMRC grades and hashes).
- [ ] **Task 9: Registry-to-Model Synchronization & Calibration Closure**
  - [ ] Sub-task: Implement logic to automatically update `data/raw/calibration_targets.csv` from promoted evidence.
  - [ ] Sub-task: Final regression run to verify model stability with newly grounded data.
- [ ] **Task: Conductor - User Manual Verification 'Reporting & Synchronization' (Protocol in workflow.md)**
