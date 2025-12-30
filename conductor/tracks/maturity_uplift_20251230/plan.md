# Implementation Plan: Project Maturity, SOTA Architecture & Context Overhaul

## Phase 1: Stabilization & Foundation
*Goal: Fix immediate crashes, restore dashboard functionality, and establish dynamic versioning.*

- [x] Task: Fix `KeyError: 'effshare_effective_2030'` in dashboard. [commit: 9caefc7]
    - [x] Sub-task: Create a failing test case in `tests/` that mocks engine output missing the required key.
    - [x] Sub-task: Identify where the key is generated in the engine vs where it is consumed in `dashboard.py`.
    - [x] Sub-task: Implement fix (ensure engine produces the key or dashboard handles its absence) and pass tests.
- [x] Task: Implement Dynamic Versioning. [commit: 17228]
    - [x] Sub-task: Modify `dashboard.py` and `src/nhra_gt/__init__.py` to read version from `pyproject.toml`.
    - [x] Sub-task: Remove all hard-coded version strings (e.g., "v21") from the UI and filenames.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Stabilization & Foundation' (Protocol in workflow.md) [checkpoint: 17228]

## Phase 2: Architectural Consolidation (JAX)
*Goal: Eliminate technical debt by deprecating the legacy engine in favor of the high-performance JAX engine.*

- [x] Task: Feature Parity Audit. [commit: ab65315]
    - [x] Sub-task: Use `codebase_investigator` to map all functions in the "Legacy Engine" vs "New Engine".
    - [x] Sub-task: Document any unique logic in Legacy that is missing from New.
- [x] Task: Migration & Deprecation. [commit: ab65315]
    - [x] Sub-task: Port identified unique logic from Legacy to the JAX-based New engine.
    - [x] Sub-task: Refactor `dashboard.py` to use only the consolidated New engine.
    - [x] Sub-task: Remove/Archive the legacy engine source files.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Architectural Consolidation (JAX)' (Protocol in workflow.md)

## Phase 3: Context, Scenarios & Interpretation
*Goal: Bridge the gap between abstract game mechanics and NHRA policy reality for a global audience.*

- [ ] Task: Implementation of "Scenario Library".
    - [ ] Sub-task: Define 3-5 standard policy scenarios (e.g., "Fiscal Cliff", "Pandemic Shock") in a YAML configuration.
    - [ ] Sub-task: Add a Scenario Selector to the Streamlit sidebar that auto-updates slider values.
- [ ] Task: Interpretation Layer.
    - [ ] Sub-task: Add "How to Interpret" expander components to every major visualization in the dashboard.
    - [ ] Sub-task: Add descriptive tooltips to all input sliders/parameters.
- [ ] Task: Background & Theory Content.
    - [ ] Sub-task: Draft and implement a "Background" page in the dashboard explaining NHRA issues and Game Theory mechanics (Players, Moves, Payoffs).
    - [ ] Sub-task: Add a "Technical Stack" page justifying the use of Gambit/JAX with links to documentation.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Context, Scenarios & Interpretation' (Protocol in workflow.md)

## Phase 4: Documentation & Reproducibility
*Goal: Create a rigorous academic documentation suite and a reliable "Zero-to-Hero" build path.*

- [ ] Task: Model Theory Overhaul.
    - [ ] Sub-task: Create MkDocs pages for each core model with LaTeX formulae and notation.
    - [ ] Sub-task: Implement evidence-linking (citations to `data/bibliography`).
- [ ] Task: Automated Glossary Integration.
    - [ ] Sub-task: Implement a glossary script or MkDocs plugin to auto-link key terms (LHN, ABF, etc.) to definitions.
    - [ ] Sub-task: Populate the glossary with all identified acronyms and technical terms.
- [ ] Task: System Visualization.
    - [ ] Sub-task: Implement Mermaid.js architecture and data-flow diagrams in MkDocs.
- [ ] Task: Reproducibility Guide.
    - [ ] Sub-task: Write a "Zero-to-Hero" guide for external researchers.
    - [ ] Sub-task: Verify the guide by executing a clean build from a fresh environment.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Documentation & Reproducibility' (Protocol in workflow.md)

## Phase 5: Validation & Final Polish
*Goal: Ensure the model matches basic reality and the codebase is clean.*

- [ ] Task: Baseline Calibration Check.
    - [ ] Sub-task: Execute a baseline simulation run and compare outputs against "realistic" expectations (e.g., budget stability).
    - [ ] Sub-task: Tune default parameter values in `configs/` if outputs are non-plausible.
- [ ] Task: Final Quality Audit.
    - [ ] Sub-task: Run `nox` (lint, type-check, tests) and resolve any remaining "low-hanging fruit".
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Validation & Final Polish' (Protocol in workflow.md)
