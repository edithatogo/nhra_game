# Implementation Plan: Gap Analysis & Artifact Synchronization

This plan outlines the steps to perform a gap analysis between the academic manuscripts and the current codebase/dashboard, synchronize all artifacts, and ensure "maximal feature parity."

## Phase 1: Deep Investigation & Audit (Investigation Phase)
Goal: Identify all discrepancies between manuscripts, code, and the dashboard.

- [x] **Task: Conductor - User Manual Verification 'Phase 1 Initial State' (Protocol in workflow.md)**
- [x] **Task: Analyze Paper 1 (Qualitative Mapping) vs. Codebase**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to map every game-theoretic mechanism described in P1 to its implementation in `src/`.
    - [x] Document any theoretical mechanisms in P1 that are missing or simplified in the code.
- [x] **Task: Analyze Paper 2 (Quantitative Modeling) vs. Codebase**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to cross-reference all parameters and formulas in P2 with `src/nhra_gt` and `context/04_parameter_registry.csv`.
    - [x] Identify any "lost" quantitative features or validation steps described in P2.
- [x] **Task: Audit Streamlit Dashboard vs. Manuscripts/Code**
    - [x] **Method:** Use `delegate_to_agent(codebase_investigator)` to identify features in the Streamlit app not present in manuscripts.
    - [x] Verify the hosted dashboard matches the repository's main branch.
- [x] **Task: Conductor - User Manual Verification 'Phase 1 Completion' (Protocol in workflow.md)**

## Phase 2: Reporting & Strategic Planning (Planning Phase)
Goal: Formalize the gaps and decide on implementation strategies.

- [x] **Task: Generate Gap Analysis Report**
    - [x] Create `reports/gap_analysis_2026.md` detailing all missing features and discrepancies.
    - [x] Classify gaps into "Immediate Fix" (Phase 3/4) or "Future Track" (Phase 6).
- [x] **Task: Propose "Value-Add" Mechanisms**
    - [x] Identify theoretical hybrids or ensembles from the papers that would improve the model.
- [x] **Task: Update & Automate Glossary Verification**
    - [x] Refine `context/08_glossary_abbreviations.md` to be the definitive dictionary.
    - [x] Write a script (`scripts/check_terminology.py`) to scan code and manuscripts for deviations.
- [x] **Task: Conductor - User Manual Verification 'Phase 2 Completion' (Protocol in workflow.md)**

## Phase 3: Manuscript Synchronization & Figure Regeneration (Artifacts Phase)
Goal: Update the scientific documentation to match the "maximal" feature set.

- [x] **Task: Update Manuscript P1 (Mapping)**
    - [x] Integrate dashboard logic and any new game-theory translations into the qualitative text.
- [x] **Task: Update Manuscript P2 (Modelling)**
    - [x] Update parameter tables and methodology to reflect the current JAX implementation.
- [x] **Task: Regenerate Manuscript Figures**
    - [x] Write/Run scripts to generate identical figures for both papers and dashboard.
    - [x] Ensure all figures in `publications/` are up-to-date and high-resolution.
- [x] **Task: Sync Bibliographies**
    - [x] Update `.bib` files and manuscript references to include all sources used in the code.
- [x] **Task: Conductor - User Manual Verification 'Phase 3 Completion' (Protocol in workflow.md)**

## Phase 4: Feature Recovery & Protocol Verification (Implementation Phase)
Goal: Reintroduce lost features and finalize reproducibility artifacts.

- [x] **Task: Implement "Lost" Features (TDD)**
    - [x] Write failing tests for a priority feature identified in Phase 1.
    - [x] Implement the feature in `src/`.
    - [x] Verify tests pass and update coverage.
- [x] **Task: Update OSF Protocols & Supplementary Materials**
    - [x] Ensure all "Analysis Artifacts" match the newly synchronized state.
    - [x] Create a "Dashboard Snapshot" (e.g., tag a release) specifically for the OSF protocol to reference.
- [x] **Task: Perform Dependency & Environment Audit**
    - [x] Verify `pyproject.toml` and `Dockerfile` are correct and minimal.
- [x] **Task: Conductor - User Manual Verification 'Phase 4 Completion' (Protocol in workflow.md)**

## Phase 5: Final Review & Backlog (Finalization Phase)
Goal: Close the track and set the stage for future work.

- [x] **Task: Final "Maximal Parity" Check**
    - [x] Verify that Code, Dashboard, and Manuscripts are now 1:1 in feature description.
- [x] **Task: Generate Future Tracks**
    - [x] Create new track folders for any long-term gaps identified in Phase 2.
- [x] **Task: Conductor - User Manual Verification 'Phase 5 Completion' (Protocol in workflow.md)**
