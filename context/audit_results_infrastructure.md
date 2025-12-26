# Audit Report: Infrastructure & Code Quality

**Date:** 2025-12-26

## 1. Summary

The repository's infrastructure is highly mature, modern, and follows best practices for Python development.

## 2. Component Audit

### A. Task Runner (`Justfile`)

* **Status:** **Excellent**.
* **Observations:** clearly defined recipes for all lifecycle stages (lint, test, build, docs). Uses `PYTHONPATH=src` explicitly to ensure correct module resolution.

### B. Dependency Management (`poetry` / `pyproject.toml`)

* **Status:** **Good**, with minor naming inconsistency.
* **Observations:**
  * Dependencies are well-segmented (dev, optional extras like `jax`/`optuna`).
  * Tool configuration (`ruff`, `mypy`, `coverage`) is centralized in `pyproject.toml`.
  * **Finding:** Project name is `nhra_game` but package import is `nhra_gt`. While mapped correctly via `packages = [{include = "nhra_gt", from = "src"}]`, this mismatch caused confusion in the smoke test (`tests/test_engine_smoke.py`).

### C. Automation (`noxfile.py`)

* **Status:** **Excellent**.
* **Observations:** Covers the full "Quality Pyramid":
  * **Static:** Lint (Ruff), Type (Pyright), Security (Bandit).
  * **Dynamic:** Unit Tests (Pytest, multi-version), Coverage.
  * **Performance:** Benchmarks (ASV, pytest-benchmark), Load (Locust).
  * **Resilience:** Fuzzing (Atheris), Mutation (Mutmut).

### D. CI/CD (`.github/workflows/`)

* **Status:** **Present**.
* **Workflows:**
  * `ci.yml`: Likely runs the `nox` suite on PRs.
  * `data_refresh.yml`: Likely handles automated data ingestion (e.g., AIHW).
  * `deploy_docs.yml`: Deploys MkDocs to GitHub Pages.

## 3. Recommendations

1. **Standardize Naming:** Rename the Poetry project to `nhra_gt` (or the package to `nhra_game`) to align the PyPI name with the import name. This reduces friction for new developers.
2. **Fix Deprecations:** Address the `datetime` parsing DeprecationWarning observed in pytest logs to future-proof against Python 3.15.
