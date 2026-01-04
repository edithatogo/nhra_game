# Implementation Plan: Maturity Uplift & Modernization (v26)

## Phase 1: Package Management & Base Orchestration (uv)
- [x] **Task 1.1: Migrate to `uv`**
  - [x] Initialize `uv` project (`uv init`) and generate `uv.lock`.
  - [x] Convert `requirements.txt` and `poetry.lock` to `uv` compatible format.
  - [x] Update `Dockerfile` to use `uv` for installation (multi-stage build recommended).
- [x] **Task 1.2: Consolidate Task Running (`nox` & `just`)**
  - [x] Audit `noxfile.py` to ensure it uses `uv` for environment creation (via `nox-poetry` alternative or direct `uv` calls).
  - [x] Update `Justfile` to wrap common `uv` and `nox` commands (e.g., `just lint`, `just test`).
  - [x] Remove `tox.ini` or legacy workflow runners.
- [x] **Task 1.3: Centralize Configuration**
  - [x] Migrate `bandit`, `isort`, and `flake8` configs to `pyproject.toml`.
  - [x] Clean up redundant root configuration files (`.flake8`, `isort.cfg`).
- [x] Task: Conductor - User Manual Verification 'Phase 1: Package Management & Base Orchestration' (Protocol in workflow.md)

## Phase 2: Unified Linting & Strict Typing (Ruff & Basedpyright)
- [ ] **Task 2.1: Implement `Ruff`**
  - [ ] Configure `Ruff` in `pyproject.toml` to replace `flake8`, `isort`, `bandit`, and `pydocstyle`.
  - [ ] Run `ruff check --fix` and `ruff format` across the codebase.
  - [ ] Update `.pre-commit-config.yaml` with `ruff` hooks.
- [ ] **Task 2.2: Migrate to `Basedpyright`**
  - [ ] Install `basedpyright` and configure `pyrightconfig.json` (or `pyproject.toml` if supported).
  - [ ] Resolve typing errors to achieve a stable baseline (targeting strict mode).
  - [ ] Replace `mypy` hooks and nox sessions with `basedpyright`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Unified Linting & Strict Typing' (Protocol in workflow.md)

## Phase 3: Code Hardening & Documentation Coverage
- [ ] **Task 3.1: Docstring Coverage (`interrogate`)**
  - [ ] Configure `interrogate` in `pyproject.toml` with >80% coverage target.
  - [ ] Write missing docstrings for public interfaces (focus on `src/nhra_gt/engine.py` and `games.py`).
- [ ] **Task 3.2: Fuzz Testing & Edge Cases (`atheris`)**
  - [ ] Create fuzzer scripts for core Nash solver logic.
  - [ ] Integrate fuzzing into `nox` suite.
- [ ] **Task 3.3: Dead Code & Dependency Audit**
  - [ ] Run `vulture` to identify and remove unused functions/classes.
  - [ ] Run `deptry` to prune unused dependencies from `pyproject.toml`.
- [ ] **Task 3.4: Stub & Placeholder Resolution**
  - [ ] Scan for `pass`, `...`, and `NotImplementedError` in `src/`.
  - [ ] Implement pending logic or document explicit deprecation.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Code Hardening & Documentation Coverage' (Protocol in workflow.md)

## Phase 4: Release Automation & Pipeline Maturity
- [ ] **Task 4.1: Automated Release Management**
  - [ ] Configure `commitizen` for Conventional Commits enforcement in pre-commit.
  - [ ] Set up `python-semantic-release` GitHub Action for automated versioning.
- [ ] **Task 4.2: Snakemake Provenance & Maturity**
  - [ ] Enable `snakemake --provenance` in CI workflows.
  - [ ] Audit `Snakefile` rules for `container:` or `conda:` directives to ensure reproducibility.
- [ ] **Task 4.3: Security & License Compliance**
  - [ ] Add `osv-scanner` or `safety` to pre-commit/CI for dependency checks.
  - [ ] Add `pip-licenses` check to `nox` to verify license compatibility.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Release Automation & Pipeline Maturity' (Protocol in workflow.md)

## Phase 5: Dashboard Verification & Final Polish
- [ ] **Task 5.1: Functional Dashboard Testing (`AppTest`)**
  - [ ] Write `streamlit.testing` suite for all dashboard tabs (Overview, Scenarios, Sensitivity).
- [ ] **Task 5.2: E2E Dashboard Testing (Playwright)**
  - [ ] Refactor existing Playwright tests for reliability.
  - [ ] Verify deployment URL (gameofnhra.streamlit.app).
- [ ] **Task 5.3: Documentation Refresh**
  - [ ] Add `mkdocs-git-revision-date-localized-plugin` and `mkdocs-literate-nav` to `mkdocs.yml`.
  - [ ] Integrate `CHANGELOG.md` into the MkDocs build (e.g., via `mdx_include` or symlink).
  - [ ] Ensure dashboard links are prominent in `README.md` and MkDocs index.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Dashboard Verification & Final Polish' (Protocol in workflow.md)
