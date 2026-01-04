# Specification: Troubleshoot Performance & Fix Deployment

## 1. Overview

This track addresses three distinct issues:

1. **Streamlit Deployment:** The app fails on Streamlit Cloud with a `ModuleNotFoundError` for `jaxtyping`.
2. **Ruff Performance:** `just all` hangs during formatting/linting.
3. **Snakemake Performance:** The pipeline hangs without progress.

## 2. Problem Statement

* **Streamlit:** The deployed app crashes because `jaxtyping` (an optional dependency) is imported but not installed in the cloud environment.
* **Ruff:** The `ruff` tool hangs indefinitely or runs excessively slow during `just all`.
* **Snakemake:** The `snakemake` pipeline hangs silently.

## 3. Goals

* **Deployment:** Ensure `jaxtyping` is available in the Streamlit Cloud environment or handle its absence gracefully.
* **Performance:** Diagnose and fix the "hangs" in `ruff` and `snakemake`.

## 4. Acceptance Criteria

* [ ] Streamlit app loads successfully on `share.streamlit.io` without `ModuleNotFoundError`.
* [ ] `just all` completes successfully and within a reasonable time (< 1 minute for linting).
* [ ] Snakemake pipeline executes or reports errors immediately.

## 5. Out of Scope

* Major refactoring of the dashboard logic (beyond fixing the import).
