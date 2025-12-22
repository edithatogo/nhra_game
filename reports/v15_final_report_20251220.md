# NHRA negotiations as interacting games: equilibrium-augmented mechanism simulation (v15 — 20 Dec 2025)

## Executive summary

This version upgrades the framework by explicitly **solving Nash equilibria** for each stage game (bargaining, cost shifting, discharge integration, and coding/audit) and using equilibrium selection to drive actions in the simulation. The model still remains stylised and is intended for **mechanism explanation, scenario comparison, and sensitivity analysis**, not point forecasting.

Across scenarios, interventions that reduce discharge delay and cost shifting produce more robust reductions in simulated pressure, offload delay, and the risk proxy than headline funding-share changes alone. Equilibrium selection mainly changes the *path* by which parties converge on cooperative versus conflictual equilibria under pressure and valuation divergence.

## Evidence bridge (clinical relevance)

A large empirical literature links emergency department crowding, access block, and ambulance offload delays with delayed care, longer length of stay, and worse outcomes, particularly for time-sensitive conditions. This model does not simulate patient outcomes directly; it uses operational proxies (pressure, offload, within-4-hour performance) as mechanisms by which governance and fiscal incentives translate into safety risk.

## Methods (summary)

- **NEP realism**: NEP is treated as an annual $/NWAU index, applied to an activity weight to represent an efficient payment base.
- **Efficiency gap**: divergence between input costs and NEP indexation evolves over time, shaping the difference between nominal and effective shares.
- **Stage games**: each period includes four 2×2 games:
  1) Bargaining: efficient-price basis vs actual-cost recognition  
  2) Cost shifting: invest upstream vs shift downstream  
  3) Discharge integration: integrate vs fragment  
  4) Coding/audit: accurate vs aggressive; low vs high audit  
- **Equilibria**: for each stage game, all pure Nash equilibria are enumerated; where applicable, a mixed equilibrium is solved. An equilibrium is selected by a stated rule (default payoff-dominant).

## Results overview

Figures and tables are produced in `outputs/v15/`. The key additions are:
- an **equilibria grid** showing how many equilibria exist as pressure and efficiency gap vary;
- scenario comparisons under alternative equilibrium selection rules.

## Data and code availability

All code and reproducible scripts are included in this repository. Key commands:

- `PYTHONPATH=src python scripts/run_v15_all.py`
- `PYTHONPATH=src python scripts/make_plots_v15.py`
- `PYTHONPATH=src pytest --cov=nhra_game_theory --cov-fail-under=95`

## Calibration roadmap

A practical next step is to calibrate NEP time series (IHACPA determinations), map the model's pressure index to a jurisdiction’s offload/crowding proxy, and constrain discharge-delay parameters to observed delayed discharge measures. The IHACPA NWAU calculators are most valuable if the model is extended to activity-mix and coding-driven NWAU variation; otherwise NEP-as-index is sufficient for the mechanism focus.


## Outputs

- `outputs/v15/tables/equilibria_grid.csv`: number of equilibria by game, across a (pressure × efficiency-gap) grid.
- `outputs/v15/tables/scenario_summary.csv`: end-year metrics under scenario set.
- `outputs/v15/plots/equilibria_grid_*.png`: equilibria-count visualisations.


### Equilibria solved

This version explicitly solves **all Nash equilibria** (pure + mixed where applicable) for each stage game, and exports:

- `outputs/v15/tables/equilibria_by_year.csv`: all equilibria for each stage game evaluated at each year’s **mean** state (pressure, efficiency gap, discharge delay).
- `outputs/v15/plots/equilibria_count_over_time_*.png`: equilibrium multiplicity by year, by game.
