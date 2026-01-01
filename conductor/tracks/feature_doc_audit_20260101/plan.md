# Implementation Plan: Feature & Doc Audit & Consolidation

This plan outlines the steps to audit the `nhra_gt` codebase against its specifications, consolidate documentation into a single MkDocs site, and clean up technical debt.

## Phase 1: Exhaustive Feature Audit & Gap Analysis [checkpoint: b311846]
Goal: Identify every planned feature and its true implementation status.

- [x] Task: Catalog all "Planned Features" from `conductor/product.md` and `context/nhra_all_in_spec.md`. (470f357)
- [x] Task: Search the codebase for feature implementations, identifying full implementations, stubs, and undocumented features. (ca95db9)
- [x] Task: Create the "Feature Audit Matrix" mapping features to code files and status. (ca95db9)
- [x] Task: Document all "Hidden" features (implemented but missing from specs). (ca95db9)
- [x] Task: Generate the audit report at `docs/reports/feature_audit_2026.md`. (ca95db9)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Feature Audit' (Protocol in workflow.md) (b311846)

## Phase 2: Documentation Consolidation & Standardization
Goal: Unify all project knowledge into a centralized, searchable MkDocs site with standardized API docs.

- [ ] Task: Initialize/Refine `mkdocs.yml` configuration (ensure search and `mkdocstrings` are enabled).
- [ ] Task: Create 'Developer Guide' explicitly mapping the conceptual 'System Map' to the actual directory/module structure.
- [x] Task: Standardize docstrings in core simulation modules (`src/nhra_gt/`) to Google/NumPy style. (4c59835)
- [x] Task: Migrate existing scattered Markdown files (`context/`, `docs/`, root) into the MkDocs structure. (4c59835)
- [x] Task: Configure `mkdocstrings` to automatically generate API reference documentation from code. (4c59835)
- [x] Task: Verify the local build of the MkDocs site and ensure full-text search works. (677a6de)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Documentation' (Protocol in workflow.md) (677a6de)

## Phase 3: Technical Debt Cleanup & Plan Alignment [checkpoint: 12c372d]
Goal: Clean up the codebase and ensure the project plan accurately reflects the ground truth.

- [x] Task: Run automated dead code analysis (e.g., using `vulture`) to identify unused functions and variables. (677a6de)
- [x] Task: Move identified dead, deprecated, or unreachable code to the `archive/` directory. (677a6de)
- [x] Task: Audit `pyproject.toml` and `requirements.txt` to identify and remove unused dependencies. (677a6de)
- [x] Task: Update `conductor/product.md` to be the definitive source of truth, incorporating "hidden" features found during audit. (677a6de)
- [x] Task: Append "Remediation Tasks" to `PLAN.md` for all features identified as "Stubbed" or "Missing". (12c372d)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Cleanup & Sync' (Protocol in workflow.md) (12c372d)
