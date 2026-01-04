# Specification: Maturity Uplift & Modernization (v26)

## 1. Overview
This track focuses on modernizing the project's development toolchain, consolidating configuration, and ensuring the codebase reaches a state of "maturity" suitable for a State-of-the-Art (SOTA) designation. This involves migrating to faster, more unified tools (Ruff, uv, Basedpyright), eliminating technical debt (stubs, dead code), hardening the verification pipeline (E2E testing, docstring coverage), and automating release management.

## 2. Functional Requirements

### 2.1 Toolchain Migration & Consolidation
-   **Package Management:** Migrate from `poetry`/`conda` to **`uv`** for dependency management and virtual environment handling.
-   **Linting & Formatting:** Consolidate `isort`, `bandit`, and `flake8` functionality into **`Ruff`**. Remove legacy configuration files (`.flake8`, `isort.cfg`, etc.).
-   **Type Checking:** Migrate from `mypy` to **`Basedpyright`** for stricter, faster type analysis.
-   **Orchestration:** Ensure `nox` is the sole task runner, removing any residual `tox` configuration. Maximize usage of **`just`** for developer convenience (shortcuts).
-   **Configuration:** Centralize all possible tool configurations into `pyproject.toml`.

### 2.2 Quality Assurance & Hardening
-   **Docstring Coverage:** Implement **`interrogate`** to enforce documentation standards on public interfaces.
-   **Fuzz Testing:** Integrate **`atheris`** for edge-case testing on core game theoretic logic.
-   **Dead Code Detection:** Use **`vulture`** to identify unused code and **`deptry`** to verify dependency usage.
-   **Stub Resolution:** Scan for and resolve any `NotImplementedError`, `pass` blocks, or mock functions intended for production.
-   **Security & Compliance:**
    -   Add **`osv-scanner`** or **`safety`** for supply chain security.
    -   Add license compliance scanning (e.g., `pip-licenses`).

### 2.3 Streamlit Dashboard Verification
-   **Testing Strategy:** Implement a tiered testing approach:
    1.  **Unit/Integration:** Use `streamlit.testing` (AppTest) for fast, functional verification.
    2.  **E2E:** Refine or replace the existing Playwright suite to ensure robust, headless browser verification.
-   **Documentation:** Ensure repository documentation explicitly links to and explains the dashboard.

### 2.4 Workflow & Provenance
-   **Release Management:** Enforce **Conventional Commits** (via `commitizen` or `pre-commit`) and configure **Python Semantic Release** for automated versioning/changelogs.
-   **Snakemake Maturity:** Ensure `Snakemake` workflows utilize provenance tracking, version pinning, and maximizing feature usage (e.g., profiles, containerization directives).
-   **CI/CD Optimization:** Audit GitHub Actions to utilize `uv` caching, minimize redundancy, and integrate the new tools (Basedpyright, Ruff).

### 2.5 Documentation (MkDocs)
-   **Plugins:** Add `mkdocs-git-revision-date-localized-plugin` and `mkdocs-literate-nav` to enhance navigation and currency.
-   **Completeness:** Ensure all new tools and workflows are documented in `CONTRIBUTING.md` or `dev.md`.

## 3. Non-Functional Requirements
-   **Performance:** CI pipeline time should decrease or remain neutral.
-   **Maintainability:** Reduce root directory clutter.
-   **Reliability:** The main branch must remain passing.

## 4. Acceptance Criteria
-   [ ] `uv.lock` replaces `poetry.lock` / `requirements.txt`.
-   [ ] `ruff` handles all linting and imports.
-   [ ] `basedpyright` passes in strict mode.
-   [ ] `interrogate` passes with defined thresholds.
-   [ ] `vulture` and `deptry` reports are clean.
-   [ ] No production code relies on `NotImplementedError`.
-   [ ] Streamlit dashboard passes both `AppTest` and Playwright suites.
-   [ ] `snakemake` provenance tracking is active.
-   [ ] Semantic release workflow is configured.
-   [ ] Documentation includes dashboard links and new tool usage.

## 5. Out of Scope
-   Major architectural refactoring of the *simulation engine* (unless required to fix stubs).
