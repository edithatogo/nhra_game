# Specification: Maturity Uplift & Modernization (v26)

## 1. Overview

This track focuses on modernizing the project's development toolchain, consolidating configuration, and ensuring the codebase reaches a state of "maturity" suitable for a State-of-the-Art (SOTA) designation. This involves migrating to faster, more unified tools (Ruff, uv, Basedpyright), eliminating technical debt, hardening the verification pipeline, and automating release management.

**Key Constraint:** "YOLO mode" is active for execution, but architectural decisions must be documented and reversible.

## 2. Functional Requirements

### 2.1 Toolchain Migration & Consolidation

- **Package Management:** Migrate from `poetry`/`conda` to **`uv`** for dependency management.
  - Ensure `uv.lock` is the single source of truth.
  - **Requirement:** All dependencies (dev, opt, accel) must be installed in the local `.venv`.
- **Linting & Formatting:** Consolidate `isort`, `bandit`, and `flake8` into **`Ruff`**.
  - **Strictness:** Enable `RUF` (Ruff specific), `ARG` (Unused arguments), `T20` (Print statements), and `PIE` (Misc) rulesets.
  - **Documentation:** Explicitly document *why* any rule is ignored in `pyproject.toml`.
- **Type Checking:** Migrate from `mypy` to **`Basedpyright`**.
  - Target `strict` mode eventually, but establish a passing `standard` baseline first.
- **Orchestration:** Ensure `nox` is the sole task runner, wrapped by `just` for convenience.

### 2.2 Quality Assurance & Integration

-   **Integration of "Lost" Logic:**

    -   **Agents:** Integrate `AuditorValidator` (for post-hoc analysis) and `LLMAgent` (as a configurable player type) into the main engine or verification suite.

    -   **Solvers:** Expose `regret_min_solver_jax` and `solve_hierarchical_game_jax` in the top-level API or use them in specific advanced scenarios.

    -   **Observability:** Integrate **`logfire`** for structured logging/tracing within the main simulation loop (optional flag) to satisfy the dependency requirement.

-   **JAX Purity Check:**

    -   Audit the `src/nhra_gt/engine.py` and solvers for legacy `numpy` usage.

    -   **Goal:** Ensure core simulation logic is JAX-compliant (pure, compilable). `numpy` should only be used for I/O (Pandas) and plotting.


- **Docstring Coverage:** Implement **`interrogate`** to enforce documentation standards.
- **Property-Based Testing:** Expand usage of **`Hypothesis`** for edge-case testing on core game theoretic logic and JAX solvers.

### 2.3 Pipeline Provenance (Snakemake)

- **Versioning:** Ensure Snakemake rules explicitly track:
  - **Input Data:** Checksums or strict versioning for input files.
  - **Dependencies:** Environment hash or container ID used for execution.
  - **Outputs:** Output paths should include version/timestamp identifiers to prevent overwrites and enable comparison.
- **Reproducibility:** The pipeline must be resumable and deterministic.

### 2.4 Streamlit Dashboard Verification

- **Testing:** Implement `AppTest` (unit) and Playwright (E2E) suites.
- **Documentation:** Ensure repository documentation explicitly links to and explains the dashboard.

### 2.5 Workflow & Release

- **Release Management:** Enforce **Conventional Commits** and configure **Python Semantic Release**.
- **Dependency Updates:**
  - Dependabot is cloud-only (GitHub).
  - **Local Equivalent:** Add a `just update` command using `uv lock --upgrade` to facilitate local maintenance.

### 2.6 Markdown Standardization

- **Linting:** Maintain and enforce `markdownlint-cli2` across all documentation.
- **Formatting:** Ensure consistent line breaks and heading styles.
- **Code Blocks:** Use Ruff to lint Python code blocks within Markdown files.
- **Performance:** CI pipeline time should decrease.
- **Maintainability:** Centralize config in `pyproject.toml`.
- **Reliability:** The main branch must remain passing.

## 4. Acceptance Criteria

- [ ] `uv` fully manages the environment (dev/opt/accel).
- [ ] `ruff` passes with expanded ruleset (`RUF`, `ARG`, `T20`).
- [ ] `basedpyright` passes in `standard` mode (baseline).
- [ ] `engine.py` is audit-confirmed for JAX purity (no runtime numpy mix).
- [ ] Unused code is integrated or explicitly deprecated.
- [ ] `snakemake` outputs include provenance metadata.
- [ ] Streamlit dashboard passes automated tests.

## 5. Out of Scope

- Refactoring the entire simulation to a new framework (sticking to JAX/Flax).
