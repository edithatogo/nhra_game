# Specification: Comprehensive Figure Mapping & API Modernization

## 1. Overview
The goal of this track is to consolidate, map, and verify all figure generation capabilities within the `nhra_game_theory` repository. This involves auditing all existing plotting logic (currently scattered across scripts and legacy modules), standardizing the API into a modern functional interface within `src/`, and implementing a robust testing suite that includes smoke, data integrity, and visual regression tests.

## 2. Functional Requirements

### 2.1 Figure Mapping & Registry
- **Comprehensive Audit:** Identify all unique figures produced by:
    - Core library (`src/nhra_game_theory/plotting.py`)
    - Analysis scripts (`scripts/make_plots_*.py`, `scripts/visualize/*.py`)
    - Documentation (PDFs, Markdown) and legacy ZIP archives.
- **Registry Creation:** Create a machine-readable registry (CSV/JSON) listing:
    - Figure ID / Name
    - Source Function
    - Output Filename(s)
    - Data Dependencies
    - Description/Caption
- **Report Generation:** Auto-generate a human-readable Markdown report (`docs/reports/figure_inventory.md`) from this registry.

### 2.2 API Modernization
- **Refactoring:** Move plotting logic from ad-hoc scripts into a structured module: `src/nhra_game_theory/visualization/`.
- **Standardized Interface:** Implement a consistent functional API pattern:
    - `plot_<name>(data: DataFrame, config: PlotConfig) -> Figure`
    - Functions should separate data preparation from rendering.
- **Unified Configuration:** Create a `PlotConfig` (or similar) to centralize styling (colors, fonts, dimensions) and ensuring consistency across all figures (e.g., using project-standard Teal/Tealrose palettes).

### 2.3 Verification & Parity
- **Parity Check:** Ensure every figure identified in the audit is reproducible via the new API.
- **Missing Figures:** Re-implement any "lost" figures found in documentation/zips but missing from the current codebase.

### 2.4 Testing
- **Smoke Tests:** Verify all mapped functions execute successfully.
- **Data Integrity Tests:** Assert that data fed to plot functions matches expected schemas and values.
- **Visual Regression Tests:** Implement `pytest-mpl` (or similar) to compare generated plots against reference baselines.

## 3. Non-Functional Requirements
- **Modularity:** Plotting code must be decoupled from simulation logic.
- **Maintainability:** Reduce code duplication between similar plots.
- **Performance:** Figure generation should not bottleneck the pipeline (avoid redundant computations).
- **Format Support:** Support export to PNG, SVG, and PDF.

## 4. Out of Scope
- Creating entirely new types of visualizations not previously existing or described (unless needed to fill a parity gap).
- Changing the fundamental simulation logic (this is strictly a visualization refactor).
