# Implementation Plan: Data Pipeline & Infrastructure Modernization

## Phase 1: Configuration & Spine Automation [checkpoint: 315984b]
- [x] Task: Move `ParamsJax` defaults to `configs/defaults.yaml`.
- [x] Task: Update `baseline_state_jax` to load from the latest normalized CSV.
- [x] Task: Implement `BaselineProvider` utility to handle multi-source data loading.

## Phase 2: Registry Integration [checkpoint: 315984b]
- [x] Task: Automate the "Staging to Active" promotion logic in `src/nhra_gt/domain/registry.py`.
- [x] Task: Add schema-check decorators to all API ingestion functions.

## Phase 3: Final Integration & Cleanup [checkpoint: 315984b]
- [x] Task: Create a master orchestration script `scripts/sync_data_spine.py`.
- [x] Task: Final Conductor verification and documentation update.
