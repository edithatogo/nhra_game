# Plan: SOTA Game-Theory Model Baseline Upgrade

## Phase 1: Inventory & Core Hygiene (Items E, I + Security) [checkpoint: 134e9f1]
- [x] Task: Inventory - Inspect existing tooling and dependencies
    - [x] Sub-task: Analyze `pyproject.toml`, `setup.cfg`, `requirements.txt`
    - [x] Sub-task: Detect existing linters, formatters, and CI workflows
    - [x] Sub-task: Generate inventory summary report
    <!-- Summary: Project uses Poetry. Ruff, Mypy (strict), Pytest, Nox, Pre-commit, and CI are present. Missing: Ruff security rules, Benchmarking tools, Profiling tools, aligned Nox sessions. -->
- [x] Task: Dev Task Runner - Implement `nox`
    - [x] Sub-task: Create `noxfile.py` with sessions: `lint`, `tests`, `docs`
    - [x] Sub-task: Ensure idempotency (check if file exists)
- [x] Task: Linting & Security - Configure `ruff` and Security Scans
    - [x] Sub-task: Add `ruff` to dev-dependencies
    - [x] Sub-task: Configure `ruff` defaults in `pyproject.toml` (enable `S` rules for security)
    - [x] Sub-task: Create/Update `.pre-commit-config.yaml`
- [x] Task: CI - Establish GitHub Actions
    - [x] Sub-task: Create `.github/workflows/ci.yml` (lint + test + type)
    - [x] Sub-task: Verify CI runs on push/PR
- [x] Task: Conductor - User Manual Verification 'Inventory & Core Hygiene' (Protocol in workflow.md)

## Phase 2: Typing & Validation (Items A, B, C, K)
- [x] Task: Static Typing - Configure `pyright`/`mypy`
    - [x] Sub-task: Add type checker to dev-dependencies
    - [x] Sub-task: Generate strict config (baseline existing errors if needed)
    - [x] Sub-task: Add `typing_extensions` if needed (Skipped - not yet needed)
- [x] Task: Runtime Validation - Boundary Checks
    - [x] Sub-task: Check for existing boundary inputs (CLI/Config)
    - [x] Sub-task: Add `pydantic` only if applicable boundaries exist (Already used in config.py)
- [x] Task: Numeric Typing - Protocol Scaffolding
    - [x] Sub-task: Create `src/nhra_game_theory/interfaces/` (or equivalent)
    - [x] Sub-task: Add `numpy.typing.NDArray` support
    - [x] Sub-task: Add `jaxtyping` if JAX is detected (Support added via try-except in protocols.py)
    - [x] Sub-task: Create `protocols.py` (Strategy, NormalFormGame)
- [x] Task: Runtime Type Checks - Smoke Test
    - [x] Sub-task: Add `beartype`, `typeguard` to dev-deps
    - [x] Sub-task: Create `tests/test_runtime_typecheck_smoke.py`
    - [x] Sub-task: Add `nox -s type_runtime` session
- [ ] Task: Conductor - User Manual Verification 'Typing & Validation' (Protocol in workflow.md)

## Phase 3: Testing & Coverage (Items D, H)
- [ ] Task: Testing - Property-Based Tests
    - [ ] Sub-task: Add `hypothesis` to dev-dependencies
    - [ ] Sub-task: Create `tests/properties/test_invariants.py` skeleton
- [ ] Task: Coverage - Configuration
    - [ ] Sub-task: Add `pytest-cov` to dev-dependencies
    - [ ] Sub-task: Configure coverage in `pyproject.toml`
    - [ ] Sub-task: Update `nox session to produce coverage reports
    - [ ] Sub-task: Update `.gitignore` (`htmlcov/`, `.coverage`)
- [ ] Task: Conductor - User Manual Verification 'Testing & Coverage' (Protocol in workflow.md)

## Phase 4: Performance & Benchmarking (Items F, G)
- [ ] Task: Profiling - Setup Tools
    - [ ] Sub-task: Add `scalene`, `pyinstrument`, `py-spy`, `memray` to dev-deps
    - [ ] Sub-task: Create `scripts/profile_target.py`
    - [ ] Sub-task: Create `docs/profiling.md`
    - [ ] Sub-task: Update `.gitignore` (`profiles/`)
- [ ] Task: Benchmarking - Setup `pytest-benchmark` & `asv`
    - [ ] Sub-task: Add tools to dev-dependencies
    - [ ] Sub-task: Create `benchmarks/` directory and skeleton
    - [ ] Sub-task: Create `asv.conf.json`
    - [ ] Sub-task: Update `.gitignore` (`.asv/`)
- [ ] Task: Conductor - User Manual Verification 'Performance & Benchmarking' (Protocol in workflow.md)

## Phase 5: Documentation & Final Polish (Item J)
- [ ] Task: Documentation - MkDocs
    - [ ] Sub-task: Add `mkdocstrings` to dev-dependencies
    - [ ] Sub-task: Ensure `docs/index.md` exists and is up to date
- [ ] Task: Final Verification
    - [ ] Sub-task: Run full `nox` suite
    - [ ] Sub-task: Verify strict baseline compliance
- [ ] Task: Conductor - User Manual Verification 'Documentation & Final Polish' (Protocol in workflow.md)
