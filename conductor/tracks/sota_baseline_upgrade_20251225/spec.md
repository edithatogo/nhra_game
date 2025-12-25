# Specification: SOTA Game-Theory Model Baseline Upgrade

## 1. Overview
This track aims to upgrade the current Python repository to a "State-of-the-Art (SOTA) game-theory model" baseline. The focus is on establishing robust developer tooling, static analysis, profiling, benchmarking, advanced testing (PBT, Fuzzing, Load), and comprehensive E2E pipeline verification.

## 2. Functional Requirements
The system must be upgraded to include the following elements (The "Target Baseline"), strictly adhering to the "minimal, surgical diffs" rule.

### A) Typing / Static Analysis
-   **Tooling:** Ensure `pyright` (preferred strict) and `mypy` (tightened) are configured.
-   **Config:** Strict-oriented configuration for the core package (`src/` and `scripts/`).

### B) Runtime Validation (Boundaries)
-   **Scope:** Applied to external boundaries (CLI, Configs, JSON/YAML).
-   **Tooling:** `pydantic` and `pandera`.

### C) Numeric Typing
-   **Numpy:** Adopt `numpy.typing.NDArray` in new/edited typing helpers.
-   **JAX:** Add `jaxtyping` support.

### D) Testing / Invariants (Standard & Advanced)
-   **Core:** Maintain existing `pytest` suite.
-   **Property-Based:** Add `hypothesis`, `hypothesis-auto`, and `icontract-hypothesis` for automated PBT.
-   **Fuzzing:** Implement `atheris` fuzzing targets for core solver logic.
-   **Load Testing:** Integrate `locust` for performance/load testing of the dashboard/API.

### E) Dev UX / Hygiene
-   **Linting:** `ruff` with `S` (security) rules enabled.
-   **Hooks:** `.pre-commit-config.yaml` (ruff, formatting, trailing-whitespace, bandit, deptry).
-   **CI:** GitHub Actions workflow (test + type + lint + pipeline).

### F) SOTA Profiling (Opt-in)
-   **Tools:** `scalene`, `pyinstrument`, `py-spy`, `memray`.

### G) SOTA Benchmarking
-   **Tools:** `pytest-benchmark`, `asv`.

### H) Coverage
-   **Tools:** `pytest-cov`.
-   **Requirement:** **Individual file test coverage > 95%**, enforced in CI and `pyproject.toml`.

### I) Dev Task Runner
-   **Tool:** `nox`.
-   **Sessions:** `lint`, `type`, `tests`, `docs`, `coverage`, `bench`, `asv_quick`, `fuzz`, `load`.

### J) E2E Pipeline Verification
-   **Scope:** Verify the entire pipeline execution involving `snakemake`.
-   **Implementation:** `pytest` E2E tests that trigger the full pipeline.

## 3. Non-Functional Requirements
-   **Idempotency:** Re-running setup/scripts should produce no diffs.
-   **Minimal Diffs:** Preserve existing formatting/style.
-   **No Runtime Side Effects:** Advanced testing tools must be opt-in/dev-only.
-   **Interface Isolation:** Game-theory protocols in `src/nhra_game_theory/interfaces/`.

## 4. Acceptance Criteria (Definition of Done)
-   **Inventory Complete.**
-   **Tooling Installed:** All tools (including Locust, Atheris, etc.) in `pyproject.toml`.
-   **Configuration Exists:** Config files present and valid.
-   **E2E Pipeline Passes:** `snakemake` execution verified via tests.
-   **Coverage > 95% per file:** Verified by coverage reports.
-   **Documentation:** `tests/README.md` created with procedures.