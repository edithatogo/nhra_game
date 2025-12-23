# Track Plan: Empirical Spine & Mechanism Refinement (v22)

**Goal:** Ground the model in real IHACPA/ABS time series, resolve mechanism validation failures, and implement robust stability analysis.

## Phase 1: Automated Empirical Data Integration
- [ ] **Task 1.1: Automated Economic Data Ingestion (TDD)**
  - [ ] Sub-task: Create `scripts/data/ingest_economic_spine.py` to ingest historical NEP ($/NWAU) and ABS WPI.
  - [ ] Sub-task: Write tests to verify data normalization and schema compliance.
- [ ] **Task 1.2: Dynamic Efficiency Gap Calculation**
  - [ ] Sub-task: Update `src/nhra_game_theory/v9.py` to consume the new economic series for drift calculations.
  - [ ] Sub-task: Verify that the "Efficiency Gap" now reflects the divergence between NEP and WPI.
- [ ] **Task 1.3: Data Consistency & Alignment Check**
  - [ ] Sub-task: Create a validation script to ensure the new economic series aligns temporally with existing activity data (2011–2024).
- [ ] **Task: Conductor - User Manual Verification 'Empirical Integration' (Protocol in workflow.md)**

## Phase 2: Mechanism Logic & Stability Analysis
- [ ] **Task 2.1: Subgame Stability Audit**
  - [ ] Sub-task: Analyze payoff matrices to identify why Cost Shifting is inert (zero sensitivity).
  - [ ] Sub-task: Map stability regions to find "Tipping Points" where strategies should flip.
- [ ] **Task 2.2: Mechanism Refinement (Cost Shifting & Discharge)**
  - [ ] Sub-task: Refine `cost_shifting_intensity` logic to influence game tipping points.
  - [ ] Sub-task: Re-calibrate `discharge_delay` vs. `pressure` coupling to restore its Rank #1 driver status.
- [ ] **Task 2.3: Verification with Mechanism Suite**
  - [ ] Sub-task: Run `scripts/validation/validate_mechanism.py` to confirm fixes (Expect PASS).
- [ ] **Task: Conductor - User Manual Verification 'Mechanism Refinement' (Protocol in workflow.md)**

## Phase 3: Robustness, Reporting & Governance
- [ ] **Task 3.1: Tipping Point Analysis & Dashboard**
  - [ ] Sub-task: Implement a dashboard tab to visualize stability regions and tipping points.
- [ ] **Task 3.2: Probabilistic Sensitivity Analysis (PSA)**
  - [ ] Sub-task: Implement PSA with evidence-based distributions for key parameters.
- [ ] **Task 3.3: Governance & Decision Logging**
  - [ ] Sub-task: Document mechanism changes and stability findings in `context/decisions/`.
- [ ] **Task: Conductor - User Manual Verification 'Robustness & Reporting' (Protocol in workflow.md)**
