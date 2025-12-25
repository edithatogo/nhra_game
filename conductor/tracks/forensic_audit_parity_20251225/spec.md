# Specification: Forensic Parity Audit & Feature Recovery

**Track ID:** forensic_audit_parity_20251225
**Type:** Feature / Audit
**Status:** DRAFT

## 1. Overview
The goal of this track is to perform a comprehensive "four-way" forensic audit to ensure total feature parity between the project's origin and its current state. We will employ AST logic fingerprinting and visual-to-code traceability to compare archived zip files, original diagrams, ChatGPT context, and the live repository.

## 2. Functional Requirements

### 2.1 Source Discovery & Cataloguing
- **Archived Zips (AST Audit):** Identify and recursively audit all `.zip` files. Use AST parsing to extract logic fingerprints (function signatures, constants, game logic) to prevent missing logic due to renaming.
- **Diagram Audit (Visual-to-Code):** Catalogue all nodes and edges in Graphviz/Mermaid diagrams. Explicitly verify that every strategic influence (edge) in the diagrams has a corresponding implementation in the engine.
- **ChatGPT Context:** Capture the ChatGPT origin conversation via headful browser and save as `context/origin_chatgpt_context.md`.

### 2.2 Parity Analysis & Matrix
- **Parity Matrix Generation:** Create a structured matrix tracking every feature/subgame discovered across all sources with status: `[Implemented]`, `[Refactored]`, or `[Missing]`.
- **Intent Parity:** Cross-reference captured ChatGPT context with the live implementation to identify dropped qualitative requirements.

### 2.3 Reporting & Documentation
- **Gap Report:** Generate a comprehensive new `reports/lost_features_audit.md` (archiving the old version).
- **Recovery Candidate List:** Provide the user with a prioritized list of missing features/logic for approval to restore.

## 3. Acceptance Criteria
- [ ] Every `.zip` file has been fingerprints via AST.
- [ ] Visual-to-code traceability report confirms alignment with all diagrams.
- [ ] `context/origin_chatgpt_context.md` is populated.
- [ ] A machine-readable Parity Matrix is generated.
- [ ] The new `reports/lost_features_audit.md` is finalized.

## 4. Out of Scope
- Automatic re-implementation of missing features. Implementation will follow user approval of the Recovery Candidate List.
