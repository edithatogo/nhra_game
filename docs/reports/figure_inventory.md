# Figure Inventory

Generated from `docs/reports/figure_registry.json`.

## Active Figures

| ID | Description | Source | Output |
|---|---|---|---|
| **fig_trajectory** | Time-series plot of simulation variables with optional quantile ribbons. | `src/nhra_game_theory/plotting.py` (`plot_trajectory`) | `outputs/plots/trajectory_*.png` |
| **fig_strategy_heatmap** | Heatmap showing strategy frequency evolution over time for each game node. | `src/nhra_game_theory/plotting.py` (`plot_strategy_heatmap`) | `outputs/plots/strategy_heatmap_*.png` |
| **fig_tornado_rankcorr** | Tornado plot showing Spearman rank correlations between parameters and outcomes. | `src/nhra_game_theory/plotting.py` (`tornado_from_rankcorr`) | `outputs/plots/tornado_*.png` |
| **fig_games_network** | Interactive Plotly network diagram of game nodes and influence edges. | `src/nhra_game_theory/plotting.py` (`render_games_graph_interactive`) | `outputs/plots/games_network.html` |
| **fig_sobol_indices** | Bar chart of First-order (S1) and Total-order (ST) sensitivity indices. | `src/nhra_game_theory/sensitivity.py` (`plot_sobol_indices`) | `outputs/gsa/sobol_indices_*.png` |
| **fig_sobol_heatmap** | Heatmap of Second-order (S2) parameter interactions. | `src/nhra_game_theory/sensitivity.py` (`plot_sobol_heatmap`) | `outputs/gsa/sobol_heatmap.png` |
| **fig_morris_tornado** | Tornado plot of Morris mu_star values. | `src/nhra_game_theory/sensitivity.py` (`plot_morris_tornado`) | `outputs/gsa/morris_tornado.png` |
| **fig_psa_distribution** | Histogram/KDE of probabilistic sensitivity analysis outcomes. | `scripts/analysis/run_psa.py` | `outputs/psa/psa_distribution.png` |
| **fig_theil_decomposition** | Bar chart showing decomposition of Theil inequality index (Bias, Variance, Covariance). | `scripts/validation/plot_theil_decomposition.py` | `outputs/validation/theil_decomposition.png` |
| **fig_trajectory_animation** | Animated GIF of Monte Carlo trajectory swarm evolution. | `scripts/visualize/animate_trajectories.py` | `outputs/animations/trajectory.gif` |
| **fig_dashboard_risk** | Risk exposure over time (Plotly). | `scripts/dashboard.py` (`(embedded)`) | `(dashboard)` |
| **fig_dashboard_pressure** | System pressure dynamics (Plotly). | `scripts/dashboard.py` (`(embedded)`) | `(dashboard)` |
| **fig_dashboard_share** | Nominal vs Effective Commonwealth share (Plotly). | `scripts/dashboard.py` (`(embedded)`) | `(dashboard)` |

## Missing / Legacy Figures

| ID | Description | Source | Output |
|---|---|---|---|
| **fig_distributions** | Distribution plots of key variables (Found in legacy fingerprints). | (legacy) | `outputs/plots/distributions.png` |
| **fig_pareto** | Pareto frontier plot for tradeoff analysis (Found in legacy fingerprints). | (legacy) | `outputs/plots/pareto.png` |
