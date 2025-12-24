# Track Plan: Refactoring, Visualization & Forensic Polish (v27)

**Goal:** Polish the codebase for publication, recover lost features via forensic audit, and create high-impact visualizations (animations).

## Phase 1: Core Refactoring & JAX Foundation
- [ ] **Task 1.1: Intuitive Renaming**
  - [ ] Sub-task: Rename `v9.py` -> `engine.py`.
  - [ ] Sub-task: Rename `v8.py` -> `legacy_engine.py` (or archive).
  - [ ] Sub-task: Update all imports in tests and scripts.
- [ ] **Task 1.2: Artifact Versioning**
  - [ ] Sub-task: Update `Recorder` to enforcing timestamped output paths (`outputs/experiments/YYYY-MM-DD/`).
- [ ] **Task 1.3: NumPyro Definition**
  - [ ] Sub-task: Create `src/nhra_game_theory/calibration/bayesian.py` defining the model as a NumPyro probabilistic program (preparation for calibration track).
- [ ] **Task: Conductor - User Manual Verification 'Refactoring' (Protocol in workflow.md)**

## Phase 2: Forensic Deep Dive (Code Investigator)
- [ ] **Task 2.1: Automated Legacy Audit**
  - [ ] Sub-task: Deploy `codebase_investigator` to map every function in `archive/legacy_versions`.
  - [ ] Sub-task: Generate a "Feature Gap Report" (e.g. "Did we lose the 'Political Capital' variable?").
- [ ] **Task 2.2: Library Evaluation**
  - [ ] Sub-task: Review `nash.py` vs `pygambit` suitability.
  - [ ] Sub-task: Review custom loop vs `mesa` suitability.
- [ ] **Task: Conductor - User Manual Verification 'Forensic Audit' (Protocol in workflow.md)**

## Phase 3: Visualization & Polish
- [ ] **Task 3.1: Dynamic Animations**
  - [ ] Sub-task: Create `scripts/visualize/animate_trajectories.py` using `matplotlib.animation` or `plotly.express` to show MC swarms evolving.
- [ ] **Task 3.2: Publication Polish**
  - [ ] Sub-task: Update dashboard theme to be strictly academic (clean, vector-friendly).
  - [ ] Sub-task: Ensure all plots output SVG/PDF.
- [ ] **Task 3.3: End-to-End Integrity**
  - [ ] Sub-task: Run the full `snakemake` pipeline.
  - [ ] Sub-task: Fix any broken links or deprecated calls.
- [ ] **Task: Conductor - User Manual Verification 'Gold Master Polish' (Protocol in workflow.md)**
