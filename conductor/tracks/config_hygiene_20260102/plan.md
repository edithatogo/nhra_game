# Implementation Plan: Configuration Hygiene

## Phase 1: Modernization & Cleanup
Goal: Fix configuration warnings and structure.

- [x] **Task: Conductor - Auto-Verification 'Phase 1 Initial State'**
- [x] **Task: Freeze Lockfile**
    - [x] Run `poetry lock` to establish a clean baseline before structural refactoring.
- [x] **Task: PEP 621 Migration**
    - [x] Rename `[tool.poetry]` sections to `[project]`.
    - [x] Move dependencies to `[project.dependencies]`.
    - [x] Update build-backend requirements if needed.
- [x] **Task: Prune Dependencies**
    - [x] Remove `vulture` and other unused dev-deps.
    - [x] Ensure `kaleido` is properly optional.
- [x] **Task: Verify Build**
    - [x] Run `poetry lock` and `poetry install`.
    - [x] Run `poetry check`.
- [x] **Task: Conductor - Auto-Verification 'Phase 1 Completion'**

## Phase Final: Cleanup & Transition
- [ ] **Task: Archive Track**
    - [ ] Move to `conductor/archive/`.
    - [ ] Update `conductor/tracks.md`.
- [ ] **Task: Trigger Next Track**
    - [ ] Identify next pending track.