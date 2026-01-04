# Implementation Plan: Legacy Engine Retirement

## Phase 1: Infrastructure Preparation
- [ ] **Task 1.1: Migrate Params Schema**
  - [ ] Create `src/nhra_gt/domain/params.py` (or update `schemas.py`) with the Pydantic `Params` model from `legacy_engine.py`.
  - [ ] Ensure it has a `to_jax()` method.
- [ ] **Task 1.2: Migrate Helpers**
  - [ ] Move `relative_risk` and other pure helpers to `src/nhra_gt/metrics.py` or similar.

## Phase 2: Refactoring Consumers
- [ ] **Task 2.1: Refactor Sensitivity Analysis**
  - [ ] Update `src/nhra_gt/sensitivity.py` to use the new `Params` schema.
- [ ] **Task 2.2: Refactor Dashboard Scripts**
  - [ ] Check `scripts/dashboard.py` and `scripts/regenerate_manuscript_figures.py`.
  - [ ] Update imports.

## Phase 3: Cleanup & Verification
- [ ] **Task 3.1: Update Tests**
  - [ ] Refactor `tests/test_legacy_smoke.py` to use new paths.
- [ ] **Task 3.2: Delete Legacy Engine**
  - [ ] Remove `src/nhra_gt/legacy_engine.py`.
- [ ] **Task 3.3: Verification**
  - [ ] Run `just test` and `just dashboard` (smoke test).
