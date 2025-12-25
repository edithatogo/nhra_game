# Track Plan: Forensic Parity Audit & Feature Recovery

**Goal:** Achieve 100% feature parity by auditing archived zips, diagrams, and ChatGPT context against the current repository using AST fingerprinting and visual-to-code traceability.

## Phase 1: Environment & Source Discovery [checkpoint: eb0fd16]
- [x] **Task 1.1: Source Inventory (TDD)** cbe0c5a
  - [x] Sub-task: Implement `scripts/audit/inventory_sources.py` to recursively list all `.zip` files and diagram files (`.mmd`, `.dot`).
  - [x] Sub-task: Verify that all zip files found in `archive/` and the root are accessible.
- [x] **Task 1.2: Audit Infrastructure Setup** 854cee8
  - [x] Sub-task: Install `playwright` or `selenium` for headful browser capture.
  - [x] Sub-task: Archive existing `reports/lost_features_audit.md` to `archive/legacy_versions/lost_features_audit_v25.md`.
- [x] **Task: Conductor - User Manual Verification 'Discovery' (Protocol in workflow.md)**

## Phase 2: Forensic Cataloguing (AST & Visual)
- [ ] **Task 2.1: AST Logic Fingerprinting Tool (TDD)**
  - [ ] Sub-task: Implement `src/nhra_game_theory/audit/fingerprint.py` to extract function signatures, constants, and subgame logic from Python files (handling legacy versions).
  - [ ] Sub-task: Implement a loop to unzip and fingerprint every archived `.zip`.
- [ ] **Task 2.2: Visual Traceability Tool (TDD)**
  - [ ] Sub-task: Implement `src/nhra_game_theory/audit/visual_trace.py` to parse Mermaid/Graphviz files and extract strategic "edges" (influence logic).
- [ ] **Task: Conductor - User Manual Verification 'Forensic Tools' (Protocol in workflow.md)**

## Phase 3: ChatGPT Context Capture
- [ ] **Task 3.1: ChatGPT Session Capture**
  - [ ] Sub-task: Use the headful browser to load the ChatGPT origin link, capture the conversation, and save as `context/origin_chatgpt_context.md`.
- [ ] **Task: Conductor - User Manual Verification 'Context Capture' (Protocol in workflow.md)**

## Phase 4: Parity Analysis & Matrix Generation
- [ ] **Task 4.1: Cross-Reference Engine (TDD)**
  - [ ] Sub-task: Implement `scripts/audit/generate_parity_matrix.py` to compare fingerprints vs current repo vs diagram edges vs ChatGPT intent.
  - [ ] Sub-task: Generate `reports/parity_matrix.csv` with status `[Implemented]`, `[Refactored]`, or `[Missing]`.
- [ ] **Task 4.2: Gap Identification**
  - [ ] Sub-task: Identify "Orphaned Logic" (e.g., specific subgames or feedback loops present in old versions/diagrams but absent in `engine.py`).
- [ ] **Task: Conductor - User Manual Verification 'Parity Matrix' (Protocol in workflow.md)**

## Phase 5: Reporting & Finalization
- [ ] **Task 5.1: Comprehensive Audit Report**
  - [ ] Sub-task: Generate the new `reports/lost_features_audit.md` synthesizing findings from the matrix and traceability report.
- [ ] **Task 5.2: Recovery Candidate List**
  - [ ] Sub-task: Prepare a prioritized list of missing features for user approval to begin Phase 6 (Implementation).
- [ ] **Task: Conductor - User Manual Verification 'Audit Finalization' (Protocol in workflow.md)**
