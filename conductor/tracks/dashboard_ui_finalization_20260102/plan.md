# Implementation Plan: Dashboard UI Finalization

This plan addresses specific UI/Backend integration gaps identified in the forensic audit.

## Phase 1: Sequential Bargaining UI
Goal: Expose the `use_sequential_bargaining` parameter.

- [x] **Task: Conductor - Auto-Verification 'Phase 1 Initial State'**
- [x] **Task: Update Sidebar**
    - [x] Modify `scripts/dashboard.py` to add `st.sidebar.toggle` for "Sequential Bargaining".
    - [x] Persist state in `st.session_state`.
    - [x] Add conflict detection: Warning if Sequential mode is active but a Scenario overrides bargaining outcomes.
- [x] **Task: Connect to Engine**
    - [x] Update `p_game = Params(...)` instantiation in `dashboard.py` to include `use_sequential_bargaining`.
- [x] **Task: Conductor - Auto-Verification 'Phase 1 Completion'**

## Phase 2: LHN Data Consistency
Goal: Remove random mocks from LHN visualizations.

- [x] **Task: Update Engine Snapshot Logic**
    - [x] Modify `src/nhra_gt/engine.py` to include "Block Revenue" (if available in state) or a deterministic proxy in `lhn_snapshot`.
    - [x] Ensure `lhn_snapshot` includes a stable index (0..4).
- [x] **Task: Update Dashboard Visualization**
    - [x] Modify `tab2_6` logic in `dashboard.py`.
    - [x] Map LHN IDs (0..4) to fixed Types (e.g. 0=Metro, 1=Regional) via a constant dictionary, removing `np.random.choice`.
- [x] **Task: Add Snapshot Regression Test**
    - [x] Create `tests/dashboard/test_lhn_snapshot.py`.
    - [x] Run `run_hybrid` and assert `traj_game.attrs['lhn_snapshot']` is present and valid.
- [x] **Task: Conductor - Auto-Verification 'Phase 2 Completion'**

## Phase Final: Cleanup & Transition
- [ ] **Task: Archive Track**
    - [ ] Move to `conductor/archive/`.
    - [ ] Update `conductor/tracks.md`.
- [ ] **Task: Trigger Next Track**
    - [ ] Identify next pending track.