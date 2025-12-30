# Plan: Troubleshoot Performance & Fix Deployment

## Phase 1: Fix Streamlit Deployment
- [x] Task: TDD - Create a test script to verify `nhra_gt` package imports without optional dependencies (simulating a clean environment)
- [x] Task: Implement - Guard `jaxtyping` imports in `src/nhra_gt/visualization/game_trees.py` to allow execution without the optional package
- [x] Task: Verify - Confirm `streamlit_app.py` can be imported successfully in a environment where `jaxtyping` is missing
- [x] Task: Conductor - User Manual Verification 'Phase 1: Fix Streamlit Deployment' (Protocol in workflow.md)

## Phase 2: Diagnose & Fix Ruff Performance
- [ ] Task: Analysis - Run `ruff check . --verbose` to identify which files/directories cause the performance hang
- [ ] Task: Fix - Update `pyproject.toml` to exclude large/irrelevant directories (e.g., `data/`, `outputs/`, `.snakemake/`) from Ruff scanning
- [ ] Task: Verify - Run `just all` and confirm the Ruff step finishes in < 10 seconds
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Diagnose & Fix Ruff Performance' (Protocol in workflow.md)

## Phase 3: Diagnose & Fix Snakemake Performance
- [ ] Task: Analysis - Run `snakemake -n --debug-dag` to determine if the hang is in DAG resolution or rule execution
- [ ] Task: Fix - Optimize `Snakefile` or config (e.g., fix recursive file searches or dependency bottlenecks)
- [ ] Task: Verify - Run a successful dry-run (`snakemake -n`) to confirm pipeline responsiveness
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Diagnose & Fix Snakemake Performance' (Protocol in workflow.md)
