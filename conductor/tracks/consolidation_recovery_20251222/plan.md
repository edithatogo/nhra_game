# Track Plan: Project Consolidation, Cleanup, and Feature Audit

## Phase 1: Workspace Reorganization & Archiving
- [x] **Task 1: Create core directory structure** c1b3d4d
  - Create `docs/diagrams`, `docs/figures`, `data/raw`, and `archive/legacy_versions`.
- [x] **Task 2: Categorize and move loose visual artifacts** bbcafa0
  - Move all Mermaid files (`.mmd`, `.png`) to `docs/diagrams/`.
  - Move other loose images (`.png`, `.svg`) to `docs/figures/`.
- [ ] **Task 3: Categorize and move loose data/archive artifacts**
  - Move loose data files (`.csv`, `.xlsb`, `.7z`) to `data/raw/`.
  - Move all `nhra_game_theory_repo_v*.zip` files to `archive/legacy_versions/`.
- [ ] **Task 4: Archive legacy version directories**
  - Move all folders matching `nhra_game_theory_repo_v*` (except v21) to `archive/legacy_versions/`.
- [ ] **Task 5: Conductor - User Manual Verification 'Workspace Reorganization' (Protocol in workflow.md)**

## Phase 2: Root Promotion & Git Initialization
- [ ] **Task 6: Promote v21 to project root**
  - Move the contents of `nhra_game_theory_repo_v21_20251221` to the current working directory root.
- [ ] **Task 7: Initialize Git repository**
  - Run `git init`.
  - Create a robust `.gitignore` including `archive/`, `.DS_Store`, and temporary files.
- [ ] **Task 8: Perform initial commit**
  - Add all files and commit with message `feat: initial repository structure from v21`.
- [ ] **Task 9: Conductor - User Manual Verification 'Git Initialization' (Protocol in workflow.md)**

## Phase 3: Infrastructure Setup & Baseline Validation
- [ ] **Task 10: Validate dependency management**
  - Ensure `pyproject.toml` is in the root and correctly lists all dependencies identified in the tech stack.
- [ ] **Task 11: Configure development tooling**
  - Initialize/update `.pre-commit-config.yaml`.
  - Verify `Snakefile` paths match the new root structure.
- [ ] **Task 12: Baseline Quality Check**
  - Run `ruff check`, `mypy`, and `pytest` to establish the current quality baseline.
- [ ] **Task 13: Conductor - User Manual Verification 'Infrastructure Setup' (Protocol in workflow.md)**

## Phase 4: Feature Audit
- [ ] **Task 14: Version Comparison Analysis**
  - Sample core logic files from `archive/legacy_versions/` (v10, v15, v19) and compare against root `src/`.
- [ ] **Task 15: Document Feature Gaps**
  - Create `docs/feature_audit.md` summarizing any dropped features or logic variations.
- [ ] **Task 16: Conductor - User Manual Verification 'Feature Audit' (Protocol in workflow.md)**
