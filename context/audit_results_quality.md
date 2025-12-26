# Audit Report: Static Analysis & Code Quality

**Date:** 2025-12-26

## 1. Summary

The codebase has a strong foundation but is currently failing strict static analysis checks, primarily due to package naming inconsistencies and missing type stubs.

## 2. Findings

### A. Linting (Ruff)

* **Status:** **Failing** (44 errors).
* **Key Issues:**
  * **Import Sorting:** `I001` (Unsorted imports).
  * **Modern Python:** `UP035` (Using `List`/`Dict` instead of `list`/`dict`), `UP015` (Unnecessary open mode).
  * **Performance:** `C416` (Unnecessary comprehensions).
  * **Security:** `S603`/`S607` (Subprocess calls in scripts).
* **Fixability:** Most are automatically fixable via `ruff check --fix`.

### B. Type Checking (Pyright)

* **Status:** **Failing** (~800 errors).
* **Root Cause 1: Package Resolution**
  * `Import "nhra_game_theory.engine" could not be resolved`.
  * Pyright config likely expects the package name to match the directory, or the `src` mapping is fragile given the `nhra_game` vs `nhra_gt` mismatch.
* **Root Cause 2: Missing Stubs**
  * `Stub file not found for "pandas"`.
  * `Stub file not found for "plotly"`.
  * While `pandas-stubs` is in the lock file, the `nox` session for `type` might not be installing it correctly or `pyright` needs explicit config.

## 3. Recommendations

1. **Immediate Fix:** Run `ruff check --fix` to clear the 40+ linting errors.
2. **Infrastructure:** Rename `src/nhra_gt` to `src/nhra_game_theory` OR update all imports to `nhra_gt` and `pyproject.toml` to match. The current split is the main source of tooling friction.
3. **Type Config:** Update `pyproject.toml` or `noxfile.py` to ensure `pandas-stubs` and other typing dependencies are present in the `type` session environment.
