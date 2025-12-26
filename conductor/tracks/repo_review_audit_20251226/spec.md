# Specification: Comprehensive Repo Review & Audit

## 1. Overview
Perform a deep-dive investigation and review of the entire NHRA Game repository. The goal is to audit the current state of game theoretic models, data ingestion pipelines (AIHW, IHACPA), and visualization outputs. This track will result in a set of concrete recommendations, documentation updates (including diagrams/tables), and immediate fixes for any critical issues discovered.

## 2. Objectives
-   **Gap Analysis:** Identify missing games, data sources, or visualization opportunities.
-   **Validation:** Verify the reliability and correctness of data pipelines and simulation logic.
-   **Roadmap Generation:** Create a prioritized list of actionable recommendations for future tracks.
-   **Immediate Remediation:** Fix or refactor any critical bugs or blockers found during the audit.

## 3. Scope of Investigation

### 3.1 Game Theoretic Models
-   **Audit:** Review the existing "Stage Game" structure in `src/` and `context/` to understand its current limitations.
-   **Extensions:**
    -   Search for "stubbed" or planned features in comments/docs.
    -   Propose standard Healthcare Game Theory models (e.g., Principal-Agent, Queuing) relevant to the project.
    -   Suggest variations to the current Stage Game (e.g., multi-hospital competition).

### 3.2 Data Pipelines (AIHW & IHACPA)
-   **AIHW API:**
    -   Determine if the API integration is functional.
    -   Document exactly *what* is being downloaded and *how* it is injected into the repository.
    -   Verify data provenance against source requirements.
-   **IHACPA NWAU Tables:**
    -   Verify if *all* available pricing tables for each relevant year are being used.
    -   Audit the logic used to select and apply these parameters.
-   **Verification Level:** Full Audit (Surface check + Logic verification + Sample cross-reference).

### 3.3 Visualizations & Reporting
-   **Audit:** Review existing plots in `outputs/` and generation logic.
-   **Recommendations:** Suggest additional plots or tables to better communicate results.
-   **Documentation:** Create diagrams and tables that explicitly outline:
    -   Data sources (What they are, what they do).
    -   Data flow (How data moves from source -> repo -> model).

### 3.4 General Codebase Improvements
-   **Infrastructure:** Review `Justfile`, `poetry`, `nox`, and CI/CD workflows for modernization opportunities.
-   **Quality:** Assess test coverage and static analysis configurations (`ruff`, `mypy`).
-   **Performance:** Identify potential bottlenecks in the simulation loop.

## 4. Deliverables
1.  **Audit Report:** A markdown document summarizing findings for all scope items.
2.  **System Diagrams:** Visual representation of the data ingestion and game logic flow.
3.  **Data Source Table:** A detailed table listing all data sources, their status, and usage.
4.  **Fixes:** Code changes for any critical bugs identified during the review.
5.  **Recommendations:** A list of suggested "New Tracks" for future development.

## 5. Out of Scope
-   Implementation of complex new game models (recommendation only).
-   Full refactoring of the entire codebase (targeted fixes only).
