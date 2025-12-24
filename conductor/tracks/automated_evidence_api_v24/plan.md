# Track Plan: Automated Evidence & API Integration (v24)

**Goal:** Transition to API-driven data ingestion and establish a professional academic bibliography management system.

## Phase 1: AIHW MyHospitals API Ingestion
- [ ] **Task 1.1: AIHW API Client Implementation (TDD)**
  - [ ] Sub-task: Develop `src/nhra_game_theory/domain/aihw_api.py` to interface with the MyHospitals API.
  - [ ] Sub-task: Implement facility-level and quarterly metric fetching (ED within 4h, Admitted Occupancy).
- [ ] **Task 1.2: API Data Schema Alignment**
  - [ ] Sub-task: Update `EconomicSpineSchema` or create `ActivityAPISchema` to handle granular API data.
  - [ ] Sub-task: Implement `scripts/data/ingest_aihw_api.py` to refresh `data/raw/` via API calls.
- [ ] **Task: Conductor - User Manual Verification 'API Integration' (Protocol in workflow.md)**

## Phase 2: Bibliography & Citation Engine
- [ ] **Task 2.1: Bibliography Domain Model (TDD)**
  - [ ] Sub-task: Implement `Reference` Pydantic model in `src/nhra_game_theory/domain/bibliography.py`.
  - [ ] Sub-task: Add parsing for Endnote style `{Author, YYYY @Label #RecordNumber}` tokens.
- [ ] **Task 2.2: Academic Export Suite**
  - [ ] Sub-task: Implement generators for `.ris`, `.enw`, and `.bib` formats.
  - [ ] Sub-task: Integrate citations into `generate_methods_appendix.py` and the Dashboard 'Data Lineage' tab.
- [ ] **Task: Conductor - User Manual Verification 'Bibliography System' (Protocol in workflow.md)**

## Phase 3: Experiment Audit & Provenance
- [ ] **Task 3.1: Structured Experiment Recording**
  - [ ] Sub-task: Implement a `Recorder` class to log Monte Carlo rollout metadata (seed, git-hash, timing).
  - [ ] Sub-task: Integrate logging into `run_hybrid` and save to `outputs/audit/`.
- [ ] **Task 3.2: Publication-Ready Methods Update**
  - [ ] Sub-task: Regenerate `methods_appendix.md` with full academic citations and API provenance notes.
- [ ] **Task: Conductor - User Manual Verification 'Audit & Metadata' (Protocol in workflow.md)**
