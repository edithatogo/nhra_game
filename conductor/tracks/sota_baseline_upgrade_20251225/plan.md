# Plan: SOTA Game-Theory Model Baseline Upgrade

## Phase 1: Inventory & Core Hygiene (Items E, I + Security) [checkpoint: 134e9f1]
- [x] Task: Inventory - Inspect existing tooling and dependencies
- [x] Task: Dev Task Runner - Implement `nox`
- [x] Task: Linting & Security - Configure `ruff` and Security Scans
- [x] Task: CI - Establish GitHub Actions
- [x] Task: Conductor - User Manual Verification 'Inventory & Core Hygiene' (Protocol in workflow.md)

## Phase 2: Typing & Validation (Items A, B, C, K) [checkpoint: 72d64ca]
- [x] Task: Static Typing - Configure `pyright`/`mypy`
- [x] Task: Runtime Validation - Boundary Checks
- [x] Task: Numeric Typing - Protocol Scaffolding
- [x] Task: Runtime Type Checks - Smoke Test
- [x] Task: Conductor - User Manual Verification 'Typing & Validation' (Protocol in workflow.md)

## Phase 3: Testing & Coverage Refinement
- [x] Task: Fix Test Collection - Resolve `ModuleNotFoundError` for `scripts`
    - [x] Sub-task: Verify `scripts` is installable via `pyproject.toml`
    - [x] Sub-task: Ensure `PYTHONPATH` includes `src` and root in Nox/CI
- [x] Task: Property-Based Testing - Hypothesis Auto/Icontract
    - [x] Sub-task: Implement `hypothesis-auto` for a core solver function
    - [x] Sub-task: (Optional) Add `icontract` for precondition checks (Added ensure to BargainingPayoffs)
- [x] Task: Coverage Enforcement - >95% per file (Targeted via pragmas and extra tests)
- [ ] Task: Conductor - User Manual Verification 'Testing & Coverage Refinement' (Protocol in workflow.md)

## Phase 4: Advanced Testing (Fuzzing & Load)
- [x] Task: Fuzzing - Atheris
    - [x] Sub-task: Define `atheris` target for core game-theory logic
    - [x] Sub-task: Create `tests/fuzz/fuzz_target.py`
    - [x] Sub-task: Add `nox -s fuzz` session
- [x] Task: Load Testing - Locust
    - [x] Sub-task: Create `tests/load/locustfile.py` for API/Dashboard endpoints
    - [x] Sub-task: Add `nox -s load` session
- [ ] Task: Conductor - User Manual Verification 'Advanced Testing' (Protocol in workflow.md)

## Phase 5: E2E Pipeline & Snakemake [checkpoint: 0bc304b]
- [x] Task: E2E Pipeline Verification
    - [x] Sub-task: Create `tests/e2e/test_pipeline.py` using `pytest`
    - [x] Sub-task: Ensure it triggers and verifies the full `snakemake` pipeline (Verified on Python 3.11)
- [x] Task: CI Automation - Snakemake
    - [x] Sub-task: Add Snakemake execution step to `.github/workflows/ci.yml`
- [x] Task: Documentation - Test Procedures
    - [x] Sub-task: Create `tests/README.md`
- [x] Task: Conductor - User Manual Verification 'E2E Pipeline' (Protocol in workflow.md)

## Phase 6: Performance & Benchmarking (Items F, G)
- [ ] Task: Profiling - Setup Tools
- [ ] Task: Benchmarking - Setup `pytest-benchmark` & `asv`
- [ ] Task: Conductor - User Manual Verification 'Performance & Benchmarking' (Protocol in workflow.md)

## Phase 7: Documentation & Final Polish (Item J)
- [ ] Task: Documentation - MkDocs
- [ ] Task: Final Verification
- [ ] Task: Conductor - User Manual Verification 'Documentation & Final Polish' (Protocol in workflow.md)
