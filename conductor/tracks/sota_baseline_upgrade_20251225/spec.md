# Specification: SOTA Game-Theory Model Baseline Upgrade

## 1. Overview
This track aims to upgrade the current Python repository to a "State-of-the-Art (SOTA) game-theory model" baseline. The focus is on establishing robust developer tooling, static analysis, profiling, benchmarking, and documentation infrastructure without altering the core runtime behavior or refactoring existing logic unnecessarily. The goal is to provide a solid foundation for future development with strict typing and rigorous verification.

## 2. Functional Requirements
The system must be upgraded to include the following elements (The "Target Baseline"), strictly adhering to the "minimal, surgical diffs" rule.

### A) Typing / Static Analysis
-   **Tooling:** Ensure `pyright` (preferred strict) or `mypy` (tightened) is configured.
-   **Config:** Strict-oriented configuration for the core package (`src/` if applicable).
-   **Extensions:** Add `typing_extensions` only if required.

### B) Runtime Validation (Boundaries)
-   **Scope:** Only applied to external boundaries (CLI, Configs, JSON/YAML).
-   **Tooling:** Use `pydantic` if dependencies exist or boundary inputs need validation.
-   **Constraint:** Do NOT force `pydantic` into inner loops or if no boundary inputs exist.

### C) Numeric Typing
-   **Numpy:** Adopt `numpy.typing.NDArray` in new/edited typing helpers.
-   **JAX:** Add `jaxtyping` if JAX is used (dev/test only).
-   **Torch:** Minimal changes; do not force `jaxtyping`.

### D) Testing / Invariants
-   **Core:** Maintain existing `pytest` suite.
-   **Property-Based:** Add `hypothesis` (dev-dep) and a property-based test skeleton for game-theory invariants (e.g., zero-sum, payoff shapes).

### E) Dev UX / Hygiene
-   **Linting:** Ensure `ruff` is present with sensible defaults.
-   **Security:** Enable security scanning (Bandit rules within Ruff).
-   **Hooks:** Add/update `.pre-commit-config.yaml` (ruff, formatting, trailing-whitespace).
-   **CI:** Add/ensure a minimal, idempotent GitHub Actions workflow (test + type + lint).

### F) SOTA Profiling (Opt-in)
-   **Tools:** `scalene`, `pyinstrument` (plus `py-spy`, `memray` as dev-deps).
-   **Integration:**
    -   Add `scripts/profile_target.py` (or similar runner).
    -   Ensure outputs go to `profiles/` (gitignored).
    -   Add `docs/profiling.md`.
-   **Constraint:** No runtime overhead by default.

### G) SOTA Benchmarking
-   **Tools:** `pytest-benchmark`, `asv` (airspeed velocity).
-   **Integration:**
    -   Add minimal benchmark skeleton (`benchmarks/`).
    -   Add `asv.conf.json` and `.asv/` (gitignored).
    -   Docs for running benchmarks.

### H) Coverage
-   **Tools:** `pytest-cov`.
-   **Integration:**
    -   Config in `pyproject.toml` or `.coveragerc`.
    -   Nox session or script to run coverage generation.
    -   Gitignore `htmlcov/`, `.coverage`.

### I) Dev Task Runner
-   **Tool:** `nox`.
-   **Sessions:** `lint`, `type`, `tests`, `docs`, `coverage`, `bench`, `asv_quick`.

### J) Documentation Tooling
-   **Primary:** `mkdocs` (with `mkdocstrings`).
-   **Integration:** Nox sessions to build.

### K) Runtime Type Checking (Opt-in)
-   **Tools:** `beartype`, `typeguard` (dev-deps).
-   **Integration:**
    -   Minimal smoke test (`tests/test_runtime_typecheck_smoke.py`).
    -   Nox session `type_runtime`.

## 3. Non-Functional Requirements
-   **Idempotency:** Re-running setup/scripts should produce no diffs.
-   **Minimal Diffs:** Preserve existing formatting/style. No wholesale refactoring.
-   **No Runtime Side Effects:** Profiling/Verification tools must be opt-in/dev-only.
-   **Pragmatism:** Fix obvious, low-risk deficits (e.g., gitignore, minor typos) even if not explicitly listed.
-   **Baselining:** Use baseline files for type-checking/linting to ensure a green build on existing code without requiring immediate refactoring.
-   **Interface Isolation:** Add new game-theory interfaces/protocols into a dedicated namespace (e.g., `src/nhra_game/interfaces/`).

## 4. Acceptance Criteria (Definition of Done)
-   **Inventory Complete:** A summary of the initial state is generated.
-   **Tooling Installed:** All tools in A-K (excluding Sphinx) are present in `pyproject.toml` (or equiv).
-   **Configuration Exists:** Config files (`noxfile.py`, `mkdocs.yml`, `pyrightconfig.json`, etc.) are present and valid.
-   **Verification Passes:** Running `nox` (or individual tools) results in a passing state.

## 5. Phasing Strategy
The implementation will follow a Logical Grouping strategy:
1.  **Phase 1: Inventory & Core Hygiene:** Initial audit, `nox`, `ruff`, Pre-commit, CI (Items E, I + Security).
2.  **Phase 2: Typing & Validation:** Static Typing, Runtime Boundaries, Numeric Typing, Runtime Checks (Items A, B, C, K).
3.  **Phase 3: Testing & Coverage:** Pytest, Hypothesis, Coverage (Items D, H).
4.  **Phase 4: Performance & Benchmarking:** Profiling, Benchmarking (Items F, G).
5.  **Phase 5: Documentation & Final Polish:** MkDocs (Item J).
