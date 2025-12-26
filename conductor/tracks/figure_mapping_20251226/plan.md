# Implementation Plan: Comprehensive Figure Mapping & API Modernization

## Phase 1: Audit & Registry (Parity Foundation)
- [x] Task: Audit core library (`src/nhra_game_theory/plotting.py`) and analysis scripts (`scripts/make_plots_*.py`) to inventory all existing figures. e21dfb7
- [ ] Task: Inspect documentation (PDFs, Markdown) and legacy ZIPs to identify "lost" visualizations.
- [ ] Task: Create `docs/reports/figure_registry.json` (and `.csv` view) with schema: `id`, `source_file`, `function_name`, `output_path`, `description`, `inputs`.
- [ ] Task: Implement `scripts/build_figure_report.py` to generate `docs/reports/figure_inventory.md` from the registry.
- [ ] Task: Conductor - User Manual Verification 'Audit & Registry' (Protocol in workflow.md)

## Phase 2: API Design & Core Infrastructure [checkpoint: 16e41e2]
- [x] Task: Create `src/nhra_game_theory/visualization/` module structure. 1281561
- [x] Task: Define `PlotConfig` (Pydantic model) for shared styling (palettes, fonts, dimensions) in `src/nhra_game_theory/visualization/config.py`. 1281561
- [x] Task: Implement `AbstractPlotter` or protocol/interface for standardized function signatures: `plot_X(data, config) -> Figure`. 1281561
- [x] Task: Set up `pytest-mpl` and `tests/visualization/` directory with a baseline image cache. 1281561
- [x] Task: Conductor - User Manual Verification 'API Design & Core Infrastructure' (Protocol in workflow.md) 16e41e2

## Phase 3: Migration & Modernization (Iterative) [checkpoint: 748d61e]
- [x] Task: Refactor "Trajectory" plots (from `plotting.py`) to the new API, adding docstrings and type hints. 437f8f2
- [x] Task: Refactor "Strategy Heatmaps" and "Tornado Plots" to the new API. 437f8f2
- [x] Task: Migrate complex script-based figures (e.g., from `dashboard.py` or `make_plots_v*.py`) into reusable library functions. 437f8f2
- [x] Task: Verify parity: Ensure new functions produce identical (or strictly better) outputs than legacy scripts. 748d61e
- [x] Task: Conductor - User Manual Verification 'Migration & Modernization' (Protocol in workflow.md) 748d61e

## Phase 4: Testing & Verification [checkpoint: 59f0dc2]
- [x] Task: Implement Smoke Tests: Verify all registered functions execute without error on sample data. 59f0dc2
- [x] Task: Implement Data Integrity Tests: Assert input DataFrames meet schema expectations (columns, types) before plotting. 59f0dc2
- [x] Task: Implement Visual Regression Tests: Compare outputs against "gold standard" baselines for key figures. 59f0dc2
- [x] Task: Conductor - User Manual Verification 'Testing & Verification' (Protocol in workflow.md) 59f0dc2

## Phase 5: Documentation & Cleanup [checkpoint: 0b7bb45]
- [x] Task: Update `docs/models.md` and `docs/usage.md` with new visualization API usage examples. 0b7bb45
- [x] Task: Deprecate and remove legacy plotting code from `src/nhra_game_theory/plotting.py` and `scripts/`. 0b7bb45
- [x] Task: Final generation of `figure_inventory.md` reflecting the new, clean state. 0b7bb45
- [x] Task: Conductor - User Manual Verification 'Documentation & Cleanup' (Protocol in workflow.md) 0b7bb45
