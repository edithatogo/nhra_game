# Implementation Plan: Comprehensive Repo Review & Audit

This plan outlines the systematic audit of the NHRA Game repository to identify gaps, validate data pipelines, and propose architectural improvements.

## Phase 1: Game & Model Audit [checkpoint: e5fd297]
Focus on auditing the current game theoretic implementations and identifying logical extensions.

- [x] Task: Audit existing "Stage Game" implementation in `src/` and `context/nhra_stage_game_spec.md` [commit: a4736c8]
- [x] Task: Research and propose additional Healthcare Game Theory models (e.g., Principal-Agent, Queuing) [commit: a80071a]
- [x] Task: Identify "stubbed" or planned features in the codebase/docs [commit: 0c32653]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Game & Model Audit' (Protocol in workflow.md) [checkpoint: e5fd297]

## Phase 2: Data Pipeline & Provenance Audit
Deep dive into AIHW API and IHACPA pricing table integration.

- [x] Task: Verify AIHW API functionality and document data flow (Source -> Repo -> Model) [commit: 99911d0]
- [x] Task: Audit IHACPA NWAU pricing table usage across all relevant years [commit: 3b1cca3]
- [x] Task: Perform sample-based manual cross-reference of downloaded data vs source documentation [commit: 6e38760]
- [x] Task: Document data provenance and update `data/empirical/README.md` if necessary [commit: 4ff90bc]
- [~] Task: Conductor - User Manual Verification 'Phase 2: Data Pipeline & Provenance Audit' (Protocol in workflow.md)

## Phase 3: Infrastructure & Code Quality Review
Review the technical "machine" running the simulation.

- [ ] Task: Audit `Justfile`, `poetry`, `nox`, and CI/CD configurations for modernization
- [ ] Task: Review test coverage and static analysis (`ruff`, `mypy`) settings
- [ ] Task: Identify performance bottlenecks in the core simulation loop
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Infrastructure & Code Quality Review' (Protocol in workflow.md)

## Phase 4: Visualization & Reporting Enhancements
Improve how the model communicates results.

- [ ] Task: Audit existing plots in `outputs/` and suggest 3-5 high-impact visualization improvements
- [ ] Task: Create updated System Diagrams (Data Flow & Game Logic)
- [ ] Task: Generate a comprehensive "Data Source Status" table
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Visualization & Reporting Enhancements' (Protocol in workflow.md)

## Phase 5: Synthesis & Recommendations
Consolidate findings into actionable items.

- [ ] Task: Implement critical bug fixes or blockers identified during the audit
- [ ] Task: Draft final Audit Report summarizing all findings and recommendations
- [ ] Task: Create a prioritized list of "New Tracks" for future development
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Synthesis & Recommendations' (Protocol in workflow.md)
