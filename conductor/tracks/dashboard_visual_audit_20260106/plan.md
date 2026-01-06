# Plan: Dashboard Visual Integrity & Analytics Deep-Dive

**Goal:** Address user feedback regarding visual clutter (Game Tree), missing functionality, and perceived "linearity" of the dashboard responses. Ensure the frontend fully leverages the backend's complexity.

## Phase 1: Diagnostics & Visual Fixes
- [ ] **Task 1.1: Investigate Game Tree Layout**
  - Analyze `src/nhra_gt/visualization/game_trees.py`.
  - Fix overlapping text in Graphviz/Dot output (adjust `nodesep`, `ranksep`, font sizes).
  - Reproduce locally with a test script.
- [ ] **Task 1.2: Audit Validation Scorecard**
  - Review Tab 4 in `scripts/dashboard.py`.
  - Check `plot_ghost_overlay` in `src/nhra_gt/visualization/interactive.py`.
  - Ensure metric aggregation is robust.

## Phase 2: Analytics & Complexity Audit
- [ ] **Task 2.1: Map Backend to Frontend**
  - List all advanced analytics in `src/nhra_gt/analysis/` and `src/nhra_gt/visualization/`.
  - Check `scripts/dashboard.py` for usage coverage.
  - Identify gaps (e.g., is Hysteresis actually dynamic? Is Sensitivity live?).
- [ ] **Task 2.2: Linearity Check**
  - Verify `run_hybrid` usage in `dashboard.py`.
  - Check if `n_mc=50` (Lite Mode) is smoothing out non-linear tipping points too much.
  - Investigate if caching (`@st.cache_data`) is preventing parameter updates from triggering deep logic changes.

## Phase 3: Enhancements
- [ ] **Task 3.1: Implement High-Fidelity Toggles**
  - Make "Boost to SOTA" more prominent or automatic for critical charts.
- [ ] **Task 3.2: Expose Missing Analytics**
  - Wire up unused visualizations identified in Phase 2.
