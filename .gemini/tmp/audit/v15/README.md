# NHRA game-theory models (v0.8.0)

This repository contains **stylised** mechanism models of the strategic interactions in NHRA negotiations and their
downstream system-pressure consequences (eg, exit block → ED crowding → ambulance offload delays).

**Important:** These models are **illustrative** and intended for **policy reasoning / sensitivity exploration**.
They are **not** a forecast and should not be interpreted as estimating real-world mortality or budget impact.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python scripts/run_v8_all.py
```

Outputs are written to `outputs/v8/`.

## Contents

- `scripts/` — runnable analysis entrypoints (including the legacy V1–V5 scripts you asked to keep)
- `src/nhra_game_theory/` — the v8 framework (scenarios, hybrid simulation, plotting utilities)
- `diagrams/` — Mermaid and Graphviz source diagrams (including your uploaded Mermaid files)
- `reports/` — HTML + plain-text modelling summary

## Key outcomes (produced by the pipeline)

- Scenario trajectories (pressure, occupancy, offload, within-4-hours)
- Strategy frequencies by “game”
- Sensitivity analysis (tornado + rank-correlation)
- Intervention “delta” plots (difference from baseline)


## v9 additions

### Diagrams (Mermaid ↔ Graphviz)
```bash
PYTHONPATH=src python scripts/diagrams/improve_mermaid_v9.py
PYTHONPATH=src python scripts/diagrams/render_all.py
```

### Interactive D3
```bash
PYTHONPATH=src python scripts/interactive/make_d3_network_v9.py
open outputs/v9/interactive/games_network_d3.html
```

### Quality tooling
```bash
pre-commit install
tox
mkdocs serve
```

### Optional optimisation
```bash
pip install -e ".[opt]"
PYTHONPATH=src python scripts/optimize_optuna_v9.py --trials 200
```


## v15 equilibrium build

Run:

```bash
PYTHONPATH=src python scripts/run_v15_all.py
PYTHONPATH=src python scripts/make_plots_v15.py
```
