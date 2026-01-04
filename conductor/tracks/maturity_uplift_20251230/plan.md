# Implementation Plan: Maturity Uplift & Modernization (v26)

## Phase 1: Package Management & Base Orchestration (uv)

- [x] **Task 1.1: Migrate to `uv`** (SHA: 5548208)
- [x] **Task 1.2: Consolidate Task Running (`nox` & `just`)**
- [x] **Task 1.3: Centralize Configuration**
- [x] **Task 1.4: Local Dependency Integrity**
  - [x] Update `Justfile` to run `uv sync --all-groups` to ensure dev, opt, and accel are in the venv.
  - [x] Add `just update` for local dependency maintenance.
- [x] Task: Conductor - User Manual Verification 'Phase 1'

## Phase 2: Unified Linting & Strict Typing (Ruff & Basedpyright)

- [x] **Task 2.1: Implement Strict Ruff**
  - [x] Expand `select` to include `RUF`, `ARG`, `T20`, `PIE`, `PTH`.
  - [x] Document all `ignore` reasons in `pyproject.toml`.
  - [x] Run `ruff check --fix` and verify.
- [x] **Task 2.2: Establish Basedpyright Baseline**
  - [x] Resolve critical typing errors in `src/`.
  - [x] Achieve green build in `standard` mode.
- [x] Task: Conductor - User Manual Verification 'Phase 2'
- [x] **Task 2.3: Markdown Standardization**
  - [x] Run `markdownlint-cli2 --fix` on all markdown files.
  - [x] Configure Ruff to lint code blocks in Markdown (Attempted, deferred due to noise).

## Phase 3: Code Hardening & Scientific Purity

- [ ] **Task 3.1: Docstring Coverage (`interrogate`)**
- [ ] **Task 3.2: Fuzz Testing (`atheris`)**
- [ ] **Task 3.3: Integration Audit**
  - [ ] Run `vulture` and `deptry`.
  - [ ] **Assessment:** For each unused class/function, decide: Integrate (add tests/usage), Deprecate (mark with warning), or Delete (if truly obsolete).
- [ ] **Task 3.4: JAX Purity Migration**
  - [ ] Audit `src/nhra_gt/engine.py` for `import numpy as np`.
  - [ ] Replace runtime numpy calls with `jnp` or `jax.lax` equivalents to ensure JIT compatibility.
  - [ ] Restrict `numpy` to I/O and plotting modules only.
- [ ] Task: Conductor - User Manual Verification 'Phase 3'

## Phase 4: Release Automation & Pipeline Maturity

- [ ] **Task 4.1: Automated Release Management (`commitizen`)**
- [ ] **Task 4.2: Snakemake Provenance & Versioning**
  - [ ] Update `Snakefile` to use versioned output subdirectories (e.g., `outputs/{version}/{date}/`).
  - [ ] Implement environment hashing in the pipeline to track dependency state.
- [ ] **Task 4.3: Security & License Compliance**
- [ ] Task: Conductor - User Manual Verification 'Phase 4'

## Phase 5: Dashboard Verification & Final Polish

- [ ] **Task 5.1: Functional Dashboard Testing (`AppTest`)**
- [ ] **Task 5.2: E2E Dashboard Testing (Playwright)**
- [ ] **Task 5.3: Documentation Refresh**
- [ ] Task: Conductor - User Manual Verification 'Phase 5'
