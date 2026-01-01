# Track Specification: Feature & Doc Audit & Consolidation

## Overview
This track focuses on a comprehensive audit and recovery of all "planned features" across the project's history to ensure the `nhra_gt` repository serves as a complete State-of-the-Art (SOTA) predictive model. It aims to bridge the gap between "planned" and "implemented" features by meticulously verifying the codebase against all sources of truth (`product.md`, `nhra_all_in_spec.md`, root plans, and existing code).

Simultaneously, it addresses documentation fragmentation, code consistency issues, and technical debt. The goal is to produce a verified, fully implemented, and well-documented codebase where the "Plan" and the "Code" are in perfect sync.

## Goals
1.  **Feature Recovery & Verification:** Identify and catalogue all features mentioned in `product.md` and `nhra_all_in_spec.md`. Verify their implementation status (Implemented, Stubbed, Missing).
2.  **Codebase-Plan Sync:** Update `product.md` to reflect "hidden" features found in the code but missing from documentation.
3.  **Documentation Consolidation:** Unify scattered markdown files, `product.md`, and other docs into a single, searchable MkDocs site.
4.  **Standardization:** Apply docstring standards across the codebase to enable automatic API documentation generation.
5.  **Technical Debt Cleanup:** Identify and remove or archive dead, deprecated, or unreachable code to improve maintainability.
6.  **Gap Remediation:** Create specific, actionable tasks (or subsequent tracks) to implement missing or stubbed features.

## Functional Requirements
1.  **Audit Report:** A detailed artifact listing every feature from the sources of truth and its current status (File/Line reference if implemented, "Stub" if incomplete, "Missing" if not found).
2.  **Updated `product.md`:** A revised Product Guide that includes valid features discovered in the codebase that were previously undocumented.
3.  **MkDocs Site:** A functional static site generated from the `docs/` directory, containing:
    *   Project Overview & Context (`product.md`, `product-guidelines.md`).
    *   Technical Docs (API Reference generated from code).
    *   User Guides (from existing markdown files).
4.  **Standardized Docstrings:** Python code must use a consistent docstring format (e.g., Google or NumPy style) compatible with `mkdocstrings`.
5.  **Dead Code Cleanup:** Identification and removal (or moving to `archive/`) of dead, deprecated, or unreachable code found during the audit.

## Non-Functional Requirements
1.  **Completeness:** The audit must be exhaustive. No "planned" feature should be left unchecked.
2.  **Searchability:** The documentation site must allow full-text search.
3.  **Traceability:** Every claimed feature must map to specific code artifacts.

## Acceptance Criteria
- [ ] An "Audit Matrix" or report is produced and saved to `docs/reports/feature_audit_2026.md`.
- [ ] `product.md` is updated to be the definitive source of truth, matching the actual codebase capabilities.
- [ ] A `mkdocs.yml` configuration is active and successfully builds a local documentation site.
- [ ] Core modules have compliant docstrings and appear in the generated API docs.
- [ ] Dead/deprecated code is either removed or archived in the `archive/` directory.
- [ ] A set of "Remediation Tasks" are added to `PLAN.md` for any features found to be missing or stubbed.

## Out of Scope
-   Implementation of the "missing" features themselves (this track is for *identifying* and *planning* the fix, or setting up the docs structure, not rewriting the simulation logic immediately, unless simple).
-   Major refactoring of the simulation logic (focus is on documentation, verification, and technical debt cleanup).
