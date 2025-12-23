# Track Plan: Model Validation & Backtesting (SOTA)

## Phase 0: Infrastructure Rigor (Quality Baseline)
- [x] **Task 0.1: Pydantic V2 Refactor (TDD)** 8e0aaaf
  - [x] Sub-task: Refactor `Params` dataclass to a Pydantic Model with field validators (e.g., probability bounds).
  - [x] Sub-task: Refactor `EvidenceEntry` and `EvidenceRegistry` to Pydantic for robust JSON/CSV serialization.
- [x] **Task 0.2: Pandera Data Schema Enforcement (TDD)** d1daf0f
  - [x] Sub-task: Define Pandera `DataFrameSchema` for AIHW and ABS historical data.
  - [x] Sub-task: Integrate schema validation into the `preprocess_historical.py` pipeline.
- [x] **Task 0.3: Nox Environment Orchestration** 126765d
  - [x] Sub-task: Create `noxfile.py` to replace `tox.ini`.
  - [x] Sub-task: Configure sessions for testing, linting, and reproducibility (dependency matrix).
- [x] **Task 0.4: Environment Management (Migrated to Pydantic Settings)** d2dec49
  - [x] Sub-task: Implement `Settings` class using `pydantic-settings` for environment-agnostic configuration.
- [x] **Task: Conductor - User Manual Verification 'Infrastructure Rigor' (Protocol in workflow.md)** [checkpoint: f48928f]

## Phase 1: Historical Data Ingestion & Pre-processing
- [x] **Task 1: Ingest and Align Historical NHRA Datasets (TDD)**
  - [x] Sub-task: Write tests for data alignment utility (matching historical years to model steps).
  - [x] Sub-task: Implement `scripts/data/preprocess_historical.py` to normalize 2011–2025 data from AIHW and ABS.
- [x] **Task: Turing Way Checklist Verification**
  - [x] Sub-task: Audit Phase 1 against `conductor/checklists/turing_way_testing.md`.
- [~] **Task: Conductor - User Manual Verification 'Historical Data Ingestion' (Protocol in workflow.md)**

## Phase 2: Recursive Backtesting & Metric Engine
- [ ] **Task 2: Recursive Rolling Horizon Validation Engine (TDD)**
  - [ ] Sub-task: Write tests for the rolling horizon "Train-Test" loop.
  - [ ] Sub-task: Integrate `optimize_calibration_v21.py` into the recursive loop logic.
  - [ ] Sub-task: Implement the recursive loop logic in `scripts/validation/recursive_backtest.py`.
- [ ] **Task 3: Multi-Metric Calculation Engine (TDD)**
  - [ ] Sub-task: Write tests for RMSE, MAPE, Theil's Coefficient, and HIT Rate logic.
  - [ ] Sub-task: Implement calculation utilities in `src/nhra_game_theory/domain/validation.py`.
- [ ] **Task: Performance Profiling Infrastructure (Scalene)**
  - [ ] Sub-task: Configure Scalene profiling for the recursive backtest loop.
  - [ ] Sub-task: Document profiling workflow in `docs/dev.md`.
- [ ] **Task: Conductor - User Manual Verification 'Backtesting Engine' (Protocol in workflow.md)**

## Phase 3: Mechanism Validation & Holdout Reveal
- [ ] **Task 4: Structural Integrity & Mechanism Consistency Checks (TDD)**
  - [ ] Sub-task: Write tests for driver-matching logic (comparing GSA results to historical narratives).
  - [ ] Sub-task: Implement the mechanism validation suite.
- [ ] **Task 5: Blind Out-of-Sample Holdout Test**
  - [ ] Sub-task: Implement strict 2024–2025 data isolation and "Blind Reveal" test script.
- [ ] **Task: Conductor - User Manual Verification 'Mechanism Validation' (Protocol in workflow.md)**

## Phase 4: Dashboard Integration & Reporting
- [ ] **Task 6: Interactive Validation Dashboard (TDD)**
  - [ ] Sub-task: Write tests for Plotly overlay data generation (History vs. Prediction).
  - [ ] Sub-task: Implement "Validation Scorecard" and "Ghost Overlay" tabs in Streamlit.
- [ ] **Task 7: Automated Technical Validation Report & Automation**
  - [ ] Sub-task: Implement Theil Inequality Decomposition visualization (Bias/Variance/Covariance plots).
  - [ ] Sub-task: Implement Markdown/PDF report generator meeting STRESS/CHEERS guidelines.
  - [ ] Sub-task: Add `rule validate` to `Snakefile` for full reproduction.
- [ ] **Task: Conductor - User Manual Verification 'Dashboard & Reporting' (Protocol in workflow.md)**
