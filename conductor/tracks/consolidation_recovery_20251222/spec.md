# Track Spec: Project Consolidation, Cleanup, and Feature Audit

## Goal
Establish a clean, professional, and version-controlled repository based on the latest development version (v21), while archiving legacy artifacts and identifying any features lost during iterative development.

## Scope

### 1. Workspace Cleanup
- Reorganize the root directory to eliminate clutter.
- Categorize loose artifacts (Mermaid charts, figures, data files) into structured subdirectories.
- Move all previous version folders and zip files to a dedicated archive.

### 2. Repository Initialization
- Promote the v21 codebase to the project root.
- Initialize a Git repository with a comprehensive `.gitignore`.
- Perform the first "clean" commit.

### 3. Infrastructure & Quality
- Verify the build system (Hatch) and dependency management.
- Configure pre-commit hooks and Snakemake for the root-level structure.
- Ensure the project meets the baseline quality standards (linting, type checking).

### 4. Feature Audit
- Conduct a technical comparison between the archived versions (v1-v20) and the current v21.
- Document any identified feature regressions or unintentional omissions to inform the SOTA roadmap.

## Success Criteria
- Root directory contains only standard repository files/folders (src, tests, docs, data, etc.).
- `archive/` contains all legacy versions and non-current zips.
- Git is initialized and tracking the clean state.
- A `docs/feature_audit.md` file exists detailing the findings of the version comparison.
