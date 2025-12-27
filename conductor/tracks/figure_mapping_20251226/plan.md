# Implementation Plan: Comprehensive Figure Mapping & API Modernization

## Phase 1: Audit & Registry (Parity Foundation) [checkpoint: 190e6fb]
- [x] Task: Audit core library (`src/nhra_game_theory/plotting.py`) and analysis scripts (`scripts/make_plots_*.py`) to inventory all existing figures. e21dfb7
- [x] Task: Inspect documentation (PDFs, Markdown) and legacy ZIPs to identify "lost" visualizations.
- [x] Task: Create `docs/reports/figure_registry.json` (and `.csv` view) with schema: `id`, `source_file`, `function_name`, `output_path`, `description`, `inputs`.
- [x] Task: Implement `scripts/build_figure_report.py` to generate `docs/reports/figure_inventory.md` from the registry.
- [x] Task: Conductor - User Manual Verification 'Audit & Registry' (Protocol in workflow.md) 190e6fb

## Phase 2: API Design & Core Infrastructure [checkpoint: 2231a0f]
- [x] Task: Create `src/nhra_gt/visualization/` module structure.
- [x] Task: Define `PlotConfig` (Pydantic model) for shared styling (palettes, fonts, dimensions) in `src/nhra_gt/visualization/config.py`.
- [x] Task: Implement `AbstractPlotter` or protocol/interface for standardized function signatures: `plot_X(data, config) -> Figure`.
- [x] Task: Set up `pytest-mpl` and `tests/visualization/` directory with a baseline image cache.
- [x] Task: Conductor - User Manual Verification 'API Design & Core Infrastructure' (Protocol in workflow.md) 2231a0f

## Phase 3: Migration & Modernization (Iterative) [checkpoint: 1ddf580]
- [x] Task: Refactor "Trajectory" plots (from `plotting.py`) to the new API, adding docstrings and type hints.
- [x] Task: Refactor "Strategy Heatmaps" and "Tornado Plots" to the new API.
- [x] Task: Migrate complex script-based figures (e.g., from `dashboard.py` or `make_plots_v*.py`) into reusable library functions.
- [x] Task: Verify parity: Ensure new functions produce identical (or strictly better) outputs than legacy scripts.
- [x] Task: Conductor - User Manual Verification 'Migration & Modernization' (Protocol in workflow.md) 1ddf580

## Phase 4: Testing & Verification [checkpoint: 1ddf580]
- [x] Task: Implement Smoke Tests: Verify all registered functions execute without error on sample data.
- [x] Task: Implement Data Integrity Tests: Assert input DataFrames meet schema expectations (columns, types) before plotting.
- [x] Task: Implement Visual Regression Tests: Compare outputs against "gold standard" baselines for key figures.
- [x] Task: Conductor - User Manual Verification 'Testing & Verification' (Protocol in workflow.md) 1ddf580

## Phase 5: Documentation & Cleanup
- [ ] Task: Update `docs/models.md` and `docs/usage.md` with new visualization API usage examples.
- [ ] Task: Deprecate and remove legacy plotting code from `src/nhra_game_theory/plotting.py` and `scripts/`.
- [ ] Task: Final generation of `figure_inventory.md` reflecting the new, clean state.
- [ ] Task: Conductor - User Manual Verification 'Documentation & Cleanup' (Protocol in workflow.md)
