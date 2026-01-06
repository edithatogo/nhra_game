# Track Plan: Empirical Spine & Mechanism Refinement (v22)

**Goal:** Ground the model in real IHACPA/ABS time series, resolve mechanism validation failures, and implement robust stability analysis.

## CI-Relevant Commands

- `just lint`
- `just type`
- `just test`
- `just docs`

## Phase 1: Automated Empirical Data Integration [checkpoint: 5b260fb]

- [x] **Task 1.1: Automated Economic Data Ingestion (TDD)**
  - [x] Sub-task: Create `scripts/data/ingest_economic_spine.py` to ingest historical NEP ($/NWAU) and ABS WPI.
  - [x] Sub-task: Write tests to verify data normalization and schema compliance.
- [x] **Task 1.2: Dynamic Efficiency Gap Calculation**
  - [x] Sub-task: Update `src/nhra_game_theory/v9.py` to consume the new economic series for drift calculations.
  - [x] Sub-task: Verify that the "Efficiency Gap" now reflects the divergence between NEP and WPI.
- [x] **Task 1.3: Data Consistency & Alignment Check**
  - [x] Sub-task: Create a validation script to ensure the new economic series aligns temporally with existing activity data (2011–2024).
- [x] **Task: Conductor - User Manual Verification 'Empirical Integration' (Protocol in workflow.md)**

## Phase 2: Mechanism Logic & Stability Analysis [checkpoint: 3880b41]

- [x] **Task 2.1: Subgame Stability Audit**
  - [x] Sub-task: Analyze payoff matrices to identify why Cost Shifting is inert (zero sensitivity).
  - [x] Sub-task: Map stability regions to find "Tipping Points" where strategies should flip. (Finding: Game is "stuck" in 'Invest' strategy for all tested pressures. `cost_shifting_intensity` parameter is unused in game logic.)
- [x] **Task 2.2: Mechanism Refinement (Cost Shifting & Discharge)**
  - [x] Sub-task: Refine `cost_shifting_intensity` logic to influence game tipping points.
  - [x] Sub-task: Re-calibrate `discharge_delay` vs. `pressure` coupling to restore its Rank #1 driver status.
- [x] **Task 2.3: Verification with Mechanism Suite**
  - [x] Sub-task: Run `scripts/validation/validate_mechanism.py` to confirm fixes (Expect PASS).
- [x] **Task: Conductor - User Manual Verification 'Mechanism Refinement' (Protocol in workflow.md)**

## Phase 3: Robustness, Reporting & Governance [checkpoint: edcda2b]

- [x] **Task 3.1: Tipping Point Analysis & Dashboard**
  - [x] Sub-task: Implement a dashboard tab to visualize stability regions and tipping points.
- [x] **Task 3.2: Probabilistic Sensitivity Analysis (PSA)**
  - [x] Sub-task: Implement PSA with evidence-based distributions for key parameters.
- [x] **Task 3.3: Governance & Decision Logging**
  - [x] Sub-task: Document mechanism changes and stability findings in `context/decisions/`.
- [x] **Task: Conductor - User Manual Verification 'Robustness & Reporting' (Protocol in workflow.md)**

---
**Track Status:** COMPLETED 2025-12-24
Model grounded in empirical NEP/WPI series. Mechanism logic refined and validated (Discharge Delay #1). Robustness tools (PSA, Stability Heatmap) implemented.
