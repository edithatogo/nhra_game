# Models

## v8 hybrid model
The v8 hybrid model combines:
- valuation divergence (NEP vs actual)

**Note:** In IHACPA’s ABF architecture, the **NEP** is an annual **$ per NWAU** price. Payments are derived by applying NEP to **activity weights (NWAU)** (plus adjustments). In this repo, NEP is used mainly to frame the *efficient vs actual* cost debate; many simulations run on normalised indices (NEP=1).

- strategic games (bargain/define/cap/shift/govern/signal)
- patient-flow proxies (occupancy, offload, ED≤4h)
- a conservative harm index (comparative proxy only)

See: `src/nhra_game_theory/legacy_engine.py` and `scripts/run_v8_all.py`.

## Visualization Layer
The project uses a standardized visualization API located in `src/nhra_game_theory/visualization/`. 

### Core Components
- **Standardized API:** All plotting functions follow the pattern `plot_X(data, config) -> Figure`.
- **Configuration-Driven:** Global styling (DPI, palettes, fonts) is managed via `PlotConfig`.
- **Multi-Engine Support:** Supports Static (Matplotlib/Seaborn) and Interactive (Plotly) rendering.

### Available Plots
- **Trajectories:** Time-series analysis with quantile ribbons (`trajectories.py`).
- **Distributional:** Strategy heatmaps, KDE distributions, and Pareto frontiers (`distributional.py`).
- **Sensitivity:** Sobol indices, interaction heatmaps, and Morris tornado plots (`sensitivity.py`).
- **Interactive:** Dashboard-ready dual-line comparisons and stability maps (`interactive.py`).

