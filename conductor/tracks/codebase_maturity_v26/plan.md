# Track Plan: Codebase Maturity & Modernization (v26)

**Goal:** Align the project with pyOpenSci standards, automate documentation deployment, and prepare for JAX-based acceleration.

## Phase 1: Community & Documentation (pyOpenSci)
- [x] **Task 1.1: Community Health Files**
  - [x] Sub-task: Create `CONTRIBUTING.md` with development setup and PR guides.
  - [x] Sub-task: Create `CODE_OF_CONDUCT.md` (Contributor Covenant).
- [x] **Task 1.2: Metadata & Packaging**
  - [x] Sub-task: Update `pyproject.toml` with PyPI classifiers, URLs, and keywords.
- [x] **Task 1.3: Automated Documentation Deployment**
  - [x] Sub-task: Create `.github/workflows/deploy_docs.yml` to deploy MkDocs to GitHub Pages on `main`.
- [x] **Task: Conductor - User Manual Verification 'Community Standards' (Protocol in workflow.md)**

## Phase 2: JAX Migration Preparation
- [x] **Task 2.1: JAX Dependencies**
  - [x] Sub-task: Add `jax`, `jaxlib`, and `jaxtyping` to dependencies.
- [x] **Task 2.2: Solver Validation Harness**
  - [x] Sub-task: Create a test harness comparing current Numpy solvers against a (future) JAX implementation.
- [x] **Task: Conductor - User Manual Verification 'JAX Prep' (Protocol in workflow.md)** 7165eaa

## Phase 3: CI Hardening
- [x] **Task 3.1: Matrix Testing**
  - [x] Sub-task: Update `.github/workflows/ci.yml` to run tests on Ubuntu, macOS, and Windows.
- [x] **Task: Conductor - User Manual Verification 'CI Matrix' (Protocol in workflow.md)**

---
**Track Status:** COMPLETED 2025-12-24
Codebase aligned with pyOpenSci standards. Community files added. Documentation deployment automated. JAX dependencies prepared. CI matrix expanded.
