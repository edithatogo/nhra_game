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
- [x] **Task 4: Robust PDF Table Extraction & Hashing** ebd8444
  - [ ] Sub-task: Implement SHA-256 document hashing for source archival and reproducibility.
  - [ ] Sub-task: Implement `scripts/extract_tables.py` using `PyMuPDF` or `Camelot`.
- [x] **Task 5: Schema-Constrained LLM Parsing** 8e0aaaf
  - [ ] Sub-task: Implement LLM prompt engineering to map raw table text to the Registry schema.
  - [ ] Sub-task: Write tests to verify extraction of Confidence Intervals and NHMRC grades.
- [x] **Task: Conductor - User Manual Verification 'Literature Extraction' (Protocol in workflow.md)** [checkpoint: d5315fa]

## Phase 3: Evidence Manager Dashboard & Stochastic Tuning
- [x] **Task 6: Audit, Promotion & Stochastic Mapping** d87baec
  - [x] Sub-task: Implement the "Evidence Manager" tab in `scripts/dashboard_v21.py`.
  - [x] Sub-task: Map extracted 95% CIs to parameter-specific simulation noise (replacing global `noise_sd`).
- [x] **Task 7: Conflict Resolution & Consensus UI** 6b8c72d
  - [x] Sub-task: Implement side-by-side comparison for conflicting parameters.
  - [x] Sub-task: Implement \"Select Source\" or \"Weighted Average\" logic.
- [x] **Task: Conductor - User Manual Verification 'Dashboard UI' (Protocol in workflow.md)** [checkpoint: 6b8c72d]

## Phase 4: Publication Reporting & Calibration Loop Closure
- [x] **Task 8: Automated Evidence Grounding Report** 6bdd683
  - [x] Sub-task: Implement Markdown generator for the MJA appendix (including NHMRC grades and hashes).
- [x] **Task 9: Registry-to-Model Synchronization & Calibration Closure** d2dec49
  - [x] Sub-task: Implement logic to automatically update `data/raw/calibration_targets.csv` from promoted evidence.
  - [x] Sub-task: Final regression run to verify model stability with newly grounded data.
- [ ] **Task: Conductor - User Manual Verification 'Reporting & Synchronization' (Protocol in workflow.md)**
