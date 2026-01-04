# Specification: Legacy Engine Retirement & JAX Consolidation

## 1. Overview
The codebase currently maintains a `legacy_engine.py` module primarily for its Pydantic `Params` model and helper functions (`run_hybrid`, `scenario_summary`) which are consumed by sensitivity analysis scripts (`sensitivity.py`) and some tests. The core simulation logic has migrated to JAX (`engine.py`). This track aims to fully retire `legacy_engine.py` by porting its remaining utility to the modern JAX infrastructure.

## 2. Functional Requirements

### 2.1 Pydantic Model Migration
-   **Goal:** Replace `legacy_engine.Params` (Pydantic) with a robust Pydantic model in `src/nhra_gt/domain/schemas.py` or `params.py`.
-   **Requirement:** This model must be able to:
    -   Validate input from YAML/CLI.
    -   Convert cleanly to `ParamsJax` (Flax struct) for the engine.
    -   Support the `to_params_jax()` method or equivalent.

### 2.2 Sensitivity Analysis Refactor
-   **Target:** `src/nhra_gt/sensitivity.py`.
-   **Change:** Remove dependency on `legacy_engine.Params`. Use the new Pydantic model for validation and `ParamsJax` for execution.
-   **Verification:** Ensure `run_gsa.py` (Morris/Sobol) continues to function correctly.

### 2.3 Test Suite Updates
-   **Target:** `tests/test_legacy_smoke.py`, `tests/test_sensitivity.py`, etc.
-   **Change:** Update imports to point to the new location of `Params` and helper functions.
-   **Cleanup:** Delete `tests/test_legacy_smoke.py` if it covers logic that is no longer relevant, or migrate it to `test_engine_smoke.py`.

### 2.4 Deletion
-   **Action:** Delete `src/nhra_gt/legacy_engine.py`.
-   **Check:** Grep codebase to ensure no imports remain.

## 3. Acceptance Criteria
-   [ ] `src/nhra_gt/legacy_engine.py` does not exist.
-   [ ] `src/nhra_gt/sensitivity.py` imports parameters from `domain`.
-   [ ] All tests pass without `legacy_engine`.
-   [ ] Dashboard (`streamlit_app.py`) functions correctly (sanity check).
