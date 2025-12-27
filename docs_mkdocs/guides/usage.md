# Usage Guide

This guide covers installation, quickstart, and common workflows for the NHRA Game Theory toolkit.

## Installation

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- [Poetry](https://python-poetry.org/) (recommended) or pip

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/edithatogo/nhra_game.git
cd nhra_game

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
pip install nhra-gt
```

### Optional Extras

```bash
# For optimization (Optuna)
poetry install --extras opt

# For JAX acceleration
poetry install --extras accel

# For observability (Logfire)
poetry install --extras observability
```

---

## Quick Start

### Running a Basic Simulation

```python
from nhra_gt.engine import Params, run_simulation

# Create default parameters
params = Params()

# Run a 10-year simulation with 100 Monte Carlo samples
results = run_simulation(years=10, n_samples=100, params=params)

# Access results
print(f"Final pressure: {results['pressure'].mean():.2f}")
```

### Using the CLI Pipeline

The project uses [Snakemake](https://snakemake.github.io/) for reproducible pipelines:

```bash
# Run the baseline simulation
snakemake --cores 4 run_baseline

# Build the full context pack
snakemake --cores 4 context_pack

# Run all experiments
snakemake --cores 4 all
```

### Interactive Dashboard

Launch the Streamlit dashboard for interactive exploration:

```bash
streamlit run scripts/dashboard.py
```

---

## Common Workflows

### 1. Sensitivity Analysis

Run Sobol global sensitivity analysis:

```bash
python scripts/run_sobol_analysis.py --samples 1024
```

### 2. Policy Scenario Comparison

Compare policy interventions:

```python
from nhra_gt.engine import Params, run_simulation

# Baseline
baseline = run_simulation(years=10, params=Params())

# Pooled funding scenario
pooled = run_simulation(
    years=10, 
    params=Params(cost_shifting_intensity=0.2)
)
```

### 3. Validation and Backtesting

Run the recursive backtest:

```bash
python scripts/validation/recursive_backtest.py
```

---

## Visualization

The toolkit includes a comprehensive visualization suite in `nhra_gt.visualization`.

### Basic Trajectories

```python
from nhra_gt.visualization.trajectories import plot_trajectory
from nhra_gt.visualization.base import save_figure

# plot mean + quantile ribbon
fig = plot_trajectory(
    df, 
    y_col="pressure_mean", 
    ylabel="Pressure Index",
    q_low_col="pressure_p10",
    q_high_col="pressure_p90"
)
save_figure(fig, "outputs/plots/pressure.png")
```

### Scenario Comparisons

```python
from nhra_gt.visualization.trajectories import plot_comparison_trajectory

# combined_df should have a 'Scenario' column
fig = plot_comparison_trajectory(
    combined_df, 
    y_col="within4_mean", 
    ylabel="ED Within 4h"
)
```

### Strategic Heatmaps

```python
from nhra_gt.visualization.distributional import plot_strategy_heatmap

# strat_df columns: ['year', 'game', 'strategy', 'share']
fig = plot_strategy_heatmap(strat_df)
```

### Global Sensitivity (Tornado)

```python
from nhra_gt.visualization.sensitivity import plot_rank_tornado

fig = plot_rank_tornado(
    df, 
    outcome_col="pressure_2030", 
    params=["rurality_weight", "cost_shifting_intensity"]
)
```

---

## Configuration

### Parameter Registry

All model parameters are defined in `context/04_parameter_registry.csv`. Each parameter includes:

- Value and units
- Source type (primary, secondary, calibrated, assumed)
- Public URL for traceability
- Plausible range for sensitivity analysis

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOGFIRE_SEND_TO_LOGFIRE` | Enable Logfire telemetry | `false` |
| `NHRA_DEBUG` | Enable debug logging | `false` |

---

## Next Steps

- [:material-chart-bell-curve: Explore the Game Theory Models](models.md)
- [:material-file-document: Read the Design Documentation](../design.md)
- [:material-api: Browse the API Reference](../reference/index.md)
