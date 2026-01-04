# Track Plan: Automated Evidence & API Integration (v24)

**Goal:** Transition to API-driven data ingestion and establish a professional academic bibliography management system.

## Phase 1: AIHW MyHospitals API Ingestion [checkpoint: 6e45873]

- [x] **Task 1.1: AIHW API Client Implementation (TDD)**
  - [x] Sub-task: Develop `src/nhra_game_theory/domain/aihw_api.py` to interface with the MyHospitals API.
  - [x] Sub-task: Implement facility-level and quarterly metric fetching (ED within 4h, Admitted Occupancy).
- [x] **Task 1.2: API Data Schema Alignment**
  - [x] Sub-task: Update `EconomicSpineSchema` or create `ActivityAPISchema` to handle granular API data.
  - [x] Sub-task: Implement `scripts/data/ingest_aihw_api.py` to refresh `data/raw/` via API calls.
- [x] **Task: Conductor - User Manual Verification 'API Integration' (Protocol in workflow.md)**

## Phase 2: Bibliography & Citation Engine [checkpoint: ee33c12]

- [x] **Task 2.1: Bibliography Domain Model (TDD)**
  - [x] Sub-task: Implement `Reference` Pydantic model in `src/nhra_game_theory/domain/bibliography.py`.
  - [x] Sub-task: Add parsing for Endnote style `{Author, YYYY @Label #RecordNumber}` tokens.
- [x] **Task 2.2: Academic Export Suite**
  - [x] Sub-task: Implement generators for `.ris`, `.enw`, and `.bib` formats.
  - [x] Sub-task: Integrate citations into `generate_methods_appendix.py` and the Dashboard 'Data Lineage' tab.
- [x] **Task: Conductor - User Manual Verification 'Bibliography System' (Protocol in workflow.md)**

## Phase 3: Experiment Audit & Provenance [checkpoint: 1ff2060]

- [x] **Task 3.1: Structured Experiment Recording**
  - [x] Sub-task: Implement a `Recorder` class to log Monte Carlo rollout metadata (seed, git-hash, timing).
  - [x] Sub-task: Integrate logging into `run_hybrid` and save to `outputs/audit/`.
- [x] **Task 3.2: Publication-Ready Methods Update**
  - [x] Sub-task: Regenerate `methods_appendix.md` with full academic citations and API provenance notes.
- [x] **Task: Conductor - User Manual Verification 'Audit & Metadata' (Protocol in workflow.md)**

---
**Track Status:** COMPLETED 2025-12-24
Automated ingestion from AIHW MyHospitals API established. Academic bibliography engine implemented with Endnote-style citations and RIS/ENW/BIB exports. Experiment audit trails active.
