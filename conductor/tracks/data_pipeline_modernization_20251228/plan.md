# Implementation Plan: Data Pipeline & Infrastructure Modernization

## Phase 1: Configuration & Spine Automation
- [ ] Task: Move `ParamsJax` defaults to `configs/defaults.yaml`.
- [ ] Task: Update `baseline_state_jax` to load from the latest normalized CSV.
- [ ] Task: Implement `BaselineProvider` utility to handle multi-source data loading.

## Phase 2: Registry Integration
- [ ] Task: Automate the "Staging to Active" promotion logic in `src/nhra_gt/domain/registry.py`.
- [ ] Task: Add schema-check decorators to all API ingestion functions.

## Phase 3: Final Integration & Cleanup
- [ ] Task: Create a master orchestration script `scripts/sync_data_spine.py`.
- [ ] Task: Final Conductor verification and documentation update.
