# Track Spec: Gap Analysis & Artifact Synchronization (Manuscripts vs. Code)

## Overview
This track involves a comprehensive gap analysis and alignment exercise to synchronize the NHRA Game project's academic manuscripts (P1: Qualitative Mapping, P2: Quantitative Parameterization) with the current codebase and Streamlit dashboard. The goal is to achieve "maximal feature parity"—ensuring that the code, the UI, and the scientific documentation all reflect the most advanced and complete version of the models, including recovering any "lost" features and incorporating improvements made during development.

## User Persona
- **Researcher/Author:** Needs the manuscripts and OSF protocols to accurately reflect the actual analysis performed in the code.
- **Developer:** Needs to ensure the code implements all mechanisms theorized in the foundational papers.
- **Reviewer (MJA/RACMA):** Expects perfect alignment between the methodology described in the text and the results produced by the artifacts.

## Functional Requirements
1.  **Codebase & Manuscript Audit:**
    -   Perform a deep investigation of `publications/P1_Qualitative_MJA` and `publications/P2_Modelling_MJA` against the current JAX core and Streamlit dashboard.
    -   Identify specific game-theoretic mechanisms, parameters, or subgames described in the papers that are missing from the code.
    -   Identify dashboard features (e.g., specific visualizations or levers) that are not yet described or justified in the manuscripts.
2.  **Scientific Gap Analysis:**
    -   Evaluate whether alternative mechanisms (e.g., specific hybrids, ensembles, or alternative translations) mentioned in the papers were discarded and if their re-introduction adds value.
3.  **Artifact Alignment & Versioning:**
    -   Generate a detailed report (`reports/gap_analysis_2026.md`) summarizing findings.
    -   Update Manuscripts (v3.0) to incorporate dashboard features and newer model logic.
    -   Update OSF protocols and supplementary materials (e.g., parameter tables, metadata) to match the "maximal" feature set.
4.  **Dashboard & Figure Sync:**
    -   **Dashboard Source Verification:** Compare the local code with the hosted version (`https://gameofnhra.streamlit.app/`) to ensure the repo contains all deployed features.
    -   **Visual Alignment:** Regenerate manuscript figures directly from the current codebase/dashboard logic to ensure data and styling consistency.
5.  **Bibliography & Evidence Sync:**
    -   Cross-reference all code-level citations/logic with manuscript bibliographies and the `data/registry/` to ensure full academic grounding.
6.  **Environment & Terminology:**
    -   **Dependency Audit:** Verify `pyproject.toml` and `Dockerfile` match the exact environment needed for the analysis.
    -   **Glossary Unification:** Update `context/08_glossary_abbreviations.md` to serve as the definitive dictionary, and check both code and manuscripts for terminology deviations.
7.  **Backlog Generation:**
    -   Create new "Feature" tracks in `conductor/tracks.md` for any identified missing features that require separate implementation.

## Non-Functional Requirements
-   **Consistency:** Terminology must be standardized across the code, dashboard, and all three manuscripts.
-   **Traceability:** The source of each feature (Paper 1, Paper 2, Dashboard, or New) must be documented.
-   **Reproducibility:** Ensure OSF protocols accurately describe reproduction of the *current* state.

## Acceptance Criteria
-   [ ] A `reports/gap_analysis_2026.md` file exists detailing all discrepancies found.
-   [ ] Updated versions of P1 and P2 manuscripts reflect the current "maximal" feature set.
-   [ ] OSF protocols and supplementary artifacts match the codebase.
-   [ ] All manuscript figures are regenerated and consistent with the current model.
-   [ ] Bibliographies are synchronized between code and manuscripts.
-   [ ] Dependency environment is verified and documented.
-   [ ] Glossary is updated and standardized across artifacts.
-   [ ] All identified "lost" features are either reintroduced or added as new tracks.

## Out of Scope
-   Major refactoring of the core JAX engine (unless required for feature recovery).
-   Deployment beyond the existing Streamlit Cloud setup.
