# Implementation Plan: Feature & Doc Audit & Consolidation

This plan outlines the steps to audit the `nhra_gt` codebase against its specifications, consolidate documentation into a single MkDocs site, and clean up technical debt.

## Phase 1: Exhaustive Feature Audit & Gap Analysis
Goal: Identify every planned feature and its true implementation status.

- [~] Task: Catalog all "Planned Features" from `conductor/product.md` and `context/nhra_all_in_spec.md`.
- [ ] Task: Search the codebase for feature implementations, identifying full implementations, stubs, and undocumented features.
- [ ] Task: Create the "Feature Audit Matrix" mapping features to code files and status.
- [ ] Task: Document all "Hidden" features (implemented but missing from specs).
- [ ] Task: Generate the audit report at `docs/reports/feature_audit_2026.md`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Feature Audit' (Protocol in workflow.md)

## Phase 2: Documentation Consolidation & Standardization
Goal: Unify all project knowledge into a centralized, searchable MkDocs site with standardized API docs.

- [ ] Task: Initialize/Refine `mkdocs.yml` configuration (ensure search and `mkdocstrings` are enabled).
- [ ] Task: Create 'Developer Guide' explicitly mapping the conceptual 'System Map' to the actual directory/module structure.
- [ ] Task: Standardize docstrings in core simulation modules (`src/nhra_gt/`) to Google/NumPy style.
- [ ] Task: Migrate existing scattered Markdown files (`context/`, `docs/`, root) into the MkDocs structure.
- [ ] Task: Configure `mkdocstrings` to automatically generate API reference documentation from code.
- [ ] Task: Verify the local build of the MkDocs site and ensure full-text search works.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Documentation' (Protocol in workflow.md)

## Phase 3: Technical Debt Cleanup & Plan Alignment
Goal: Clean up the codebase and ensure the project plan accurately reflects the ground truth.

- [ ] Task: Run automated dead code analysis (e.g., using `vulture`) to identify unused functions and variables.
- [ ] Task: Move identified dead, deprecated, or unreachable code to the `archive/` directory.
- [ ] Task: Audit `pyproject.toml` and `requirements.txt` to identify and remove unused dependencies.
- [ ] Task: Update `conductor/product.md` to be the definitive source of truth, incorporating "hidden" features found during audit.
- [ ] Task: Append "Remediation Tasks" to `PLAN.md` for all features identified as "Stubbed" or "Missing".
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cleanup & Sync' (Protocol in workflow.md)
