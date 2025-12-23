# Track Plan: Global Sensitivity Analysis (GSA) Suite

## Phase 1: Foundation & Tooling
- [x] **Task 1: Define GSA Problem Spec** 8878f9d
  - Create a utility in `src/nhra_game_theory/sensitivity.py` to define the SALib problem dictionary (param names, bounds) dynamically from the `Params` dataclass.
  - Write unit tests to verify problem definition accuracy.
- [x] **Task 2: Implement Parallel Evaluation Engine** ad6d2a2
  - Build the parallel execution wrapper in `scripts/run_gsa.py` using `multiprocessing`.
  - Implement a "mock" mode to test parallelism without running the full heavy simulation.
- [x] **Task: Conductor - User Manual Verification 'Foundation & Tooling' (Protocol in workflow.md)** [checkpoint: 1c90395]

## Phase 2: Morris Method (Screening)
- [x] **Task 3: Implement Morris Analysis** 4ab9b1a
  - Add Morris sampling and analysis logic to `scripts/run_gsa.py`.
  - Implement generation of "Tornado Plots" (mu_star vs sigma) using `matplotlib`/`seaborn`.
- [x] **Task 4: Morris Validation Run** 4ab9b1a
  - Execute a Morris screening run (e.g., 100 trajectories) to identify non-influential parameters.
  - Verify output CSVs and plots are generated correctly.
- [x] **Task: Conductor - User Manual Verification 'Morris Method (Screening)' (Protocol in workflow.md)** [checkpoint: 911ca53]

## Phase 3: Sobol Analysis (Variance Decomposition)
- [x] **Task 5: Implement Sobol Analysis** 87af234
  - Add Sobol sampling (Saltelli) and analysis logic to `scripts/run_gsa.py`.
  - Implement "Interaction Heatmaps" and "Convergence Diagnostics" plotting.
- [x] **Task 6: High-Fidelity GSA Run** 87af234
  - Execute a larger Sobol run (e.g., 1000+ samples) using the parallel engine.
  - Generate full suite of publication-quality plots (PNG/SVG/PDF).
- [x] **Task: Conductor - User Manual Verification 'Sobol Analysis (Variance Decomposition)' (Protocol in workflow.md)** [checkpoint: e6f08c9]

## Phase 4: Reporting & Integration
- [x] **Task 7: Generate Sensitivity Summary Report** 8d81409
  - Create a module to synthesize Morris and Sobol results into a markdown summary (`data/gsa_v21/sensitivity_summary.md`).
- [~] **Task 8: Snakemake Integration**
  - Add a `rule gsa` to `Snakefile` to automate the sensitivity workflow.
- [ ] **Task: Conductor - User Manual Verification 'Reporting & Integration' (Protocol in workflow.md)**
