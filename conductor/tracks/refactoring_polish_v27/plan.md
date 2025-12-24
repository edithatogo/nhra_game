# Track Plan: Refactoring, Visualization & Forensic Polish (v27)

**Goal:** Polish the codebase for publication, recover lost features via forensic audit, and create high-impact visualizations (animations).

## Phase 1: Core Refactoring & JAX Foundation
- [x] **Task 1.0: Benchmark Baseline**
  - [x] Sub-task: Create `scripts/benchmarks/benchmark_engine.py` to record current simulation speed (samples/second). (Result: ~1047 steps/sec)
- [x] **Task 1.1: Intuitive Renaming**
  - [x] Sub-task: Rename `v9.py` -> `engine.py`.
  - [x] Sub-task: Rename `v8.py` -> `legacy_engine.py`.
  - [x] Sub-task: Update all imports in tests and scripts.
- [x] **Task 1.2: Artifact Versioning**
  - [x] Sub-task: Update `Recorder` to enforcing timestamped output paths (`outputs/experiments/YYYY-MM-DD/`).
- [x] **Task 1.3: NumPyro Definition**
  - [x] Sub-task: Create `src/nhra_game_theory/calibration/bayesian.py` defining the model as a NumPyro probabilistic program (preparation for calibration track).
- [x] **Task: Conductor - User Manual Verification 'Refactoring' (Protocol in workflow.md)**

## Phase 2: Forensic Deep Dive (Code Investigator)
- [x] **Task 2.1: Automated Legacy Audit**
  - [x] Sub-task: Deploy `codebase_investigator` to map every function in `archive/legacy_versions`.
  - [x] Sub-task: Generate a "Feature Gap Report". (Finding: Identified missing 'Political Capital' stateful variable and detailed Audit-Burden feedback loop.)
- [x] **Task 2.2: Library Evaluation**
  - [x] Sub-task: Review `nash.py` vs `pygambit` suitability. (Verdict: Use PyGambit for Validation Oracle; keep custom logic for JAX simulation).
  - [x] Sub-task: Review custom loop vs `mesa` suitability. (Verdict: Keep custom loop for JAX speed; adopt Agent-based classes for structure).
- [ ] **Task: Conductor - User Manual Verification 'Forensic Audit' (Protocol in workflow.md)**

## Phase 3: Visualization & Polish
- [x] **Task 3.0: Mechanism Re-integration (from Forensic Audit)**
  - [x] Sub-task: Restore 'Political Capital' state variable to `State` and `engine.py` logic.
  - [x] Sub-task: Re-implement 'Best Response Iteration' logic for visualization.
- [x] **Task 3.1: Dynamic Animations**
  - [x] Sub-task: Create `scripts/visualize/animate_trajectories.py` using `matplotlib.animation` or `plotly.express` to show MC swarms evolving. (Result: outputs/animations/pressure_swarm.gif)
- [x] **Task 3.2: Publication Polish**
  - [x] Sub-task: Update dashboard theme to be strictly academic (clean, vector-friendly).
  - [x] Sub-task: Ensure all plots output SVG/PDF. (Note: Toolbar buttons enabled; Teal/Tealrose themes applied).
- [x] **Task 3.3: End-to-End Integrity**
  - [x] Sub-task: Run the full `snakemake` pipeline.
  - [x] Sub-task: Fix any broken links or deprecated calls.
- [ ] **Task: Conductor - User Manual Verification 'Gold Master Polish' (Protocol in workflow.md)**
