# Implementation Plan: Comprehensive Figure Mapping & API Modernization

## Phase 1: Audit & Registry (Parity Foundation)
- [x] Task: Audit core library (`src/nhra_game_theory/plotting.py`) and analysis scripts (`scripts/make_plots_*.py`) to inventory all existing figures. e21dfb7
- [ ] Task: Inspect documentation (PDFs, Markdown) and legacy ZIPs to identify "lost" visualizations.
- [ ] Task: Create `docs/reports/figure_registry.json` (and `.csv` view) with schema: `id`, `source_file`, `function_name`, `output_path`, `description`, `inputs`.
- [ ] Task: Implement `scripts/build_figure_report.py` to generate `docs/reports/figure_inventory.md` from the registry.
- [ ] Task: Conductor - User Manual Verification 'Audit & Registry' (Protocol in workflow.md)

## Phase 2: API Design & Core Infrastructure
- [ ] Task: Create `src/nhra_game_theory/visualization/` module structure.
- [ ] Task: Define `PlotConfig` (Pydantic model) for shared styling (palettes, fonts, dimensions) in `src/nhra_game_theory/visualization/config.py`.
- [ ] Task: Implement `AbstractPlotter` or protocol/interface for standardized function signatures: `plot_X(data, config) -> Figure`.
- [ ] Task: Set up `pytest-mpl` and `tests/visualization/` directory with a baseline image cache.
- [ ] Task: Conductor - User Manual Verification 'API Design & Core Infrastructure' (Protocol in workflow.md)

## Phase 3: Migration & Modernization (Iterative)
- [ ] Task: Refactor "Trajectory" plots (from `plotting.py`) to the new API, adding docstrings and type hints.
- [ ] Task: Refactor "Strategy Heatmaps" and "Tornado Plots" to the new API.
- [ ] Task: Migrate complex script-based figures (e.g., from `dashboard.py` or `make_plots_v*.py`) into reusable library functions.
- [ ] Task: Verify parity: Ensure new functions produce identical (or strictly better) outputs than legacy scripts.
- [ ] Task: Conductor - User Manual Verification 'Migration & Modernization' (Protocol in workflow.md)

## Phase 4: Testing & Verification
- [ ] Task: Implement Smoke Tests: Verify all registered functions execute without error on sample data.
- [ ] Task: Implement Data Integrity Tests: Assert input DataFrames meet schema expectations (columns, types) before plotting.
- [ ] Task: Implement Visual Regression Tests: Compare outputs against "gold standard" baselines for key figures.
- [ ] Task: Conductor - User Manual Verification 'Testing & Verification' (Protocol in workflow.md)

## Phase 5: Documentation & Cleanup
- [ ] Task: Update `docs/models.md` and `docs/usage.md` with new visualization API usage examples.
- [ ] Task: Deprecate and remove legacy plotting code from `src/nhra_game_theory/plotting.py` and `scripts/`.
- [ ] Task: Final generation of `figure_inventory.md` reflecting the new, clean state.
- [ ] Task: Conductor - User Manual Verification 'Documentation & Cleanup' (Protocol in workflow.md)
