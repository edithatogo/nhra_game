# Track Plan: Re-integrate v2 Calibration Logic into v21

## Phase 1: Foundation & Data Formalization
- [x] **Task 1: Formalize Calibration Target Suite**
  - Extract ground-truth data points from `archive/legacy_versions/v2` context.
  - Create `data/raw/calibration_targets.csv` following the v21 schema.
- [~] **Task 2: Establish Regression Baseline**
  - Execute current `v21` baseline simulation and Optuna runs.
  - Document baseline residuals and equilibrium stability metrics.
- [ ] **Task: Conductor - User Manual Verification 'Foundation & Data Formalization' (Protocol in workflow.md)**

## Phase 2: Logic Porting & Model Enhancement
- [ ] **Task 3: Implement Bargaining Constraints (TDD)**
  - Write unit tests in `tests/test_subgames_games.py` for new parameter bounds.
  - Port constraints from `v2` into the model definition in `src/nhra_game_theory/`.
- [ ] **Task 4: Update Optuna Objective Function (TDD)**
  - Write tests for the stochastic objective (variance penalization) logic.
  - Integrate historical matching terms and stochastic penalties into the `Optuna` objective function.
- [ ] **Task: Conductor - User Manual Verification 'Logic Porting & Model Enhancement' (Protocol in workflow.md)**

## Phase 3: Advanced Optimization Features
- [ ] **Task 5: Implement Posterior Sampling**
  - Update the optimization script to support saving and sampling from the posterior distribution.
  - Write tests to verify the integrity of the generated parameter distributions.
- [ ] **Task 6: Snakemake Integration**
  - Update `Snakefile` to include the new calibration workflow as a distinct rule.
- [ ] **Task: Conductor - User Manual Verification 'Advanced Optimization Features' (Protocol in workflow.md)**

## Phase 4: Validation & Reporting
- [ ] **Task 7: Generate Sensitivity & Performance Reports**
  - Execute the full calibration pipeline.
  - Generate the "Parameter Sensitivity Report" ranking importance from posteriors.
- [ ] **Task 8: Update Manuscript Methods**
  - Revise methodology sections in `manuscripts/` to reflect stochastic calibration and v2 behavior re-integration.
- [ ] **Task 9: Final Regression & Compliance Check**
  - Compare new residuals against Phase 1 baseline.
  - Complete the CHEERS 2022 and STRESS checklists for the calibration track.
- [ ] **Task: Conductor - User Manual Verification 'Validation & Reporting' (Protocol in workflow.md)**
