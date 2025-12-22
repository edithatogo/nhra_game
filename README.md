# NHRA game-theory models (v20, 2025-12-21)

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


## Context system (local handover)

Key project context lives under `context/`.

Build a shareable context pack:

```bash
python scripts/build_context_pack.py
```

Validate that every model input is either (a) sourced to a **public URL** or (b) explicitly justified:

```bash
python scripts/check_parameters_grounded.py
```

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


## Versions

- v16 (2025-12-21): Packaging/coverage fixes; expanded narrative reporting; reviewer-round scaffolding.

- v20 (2025-12-21): Context pack + parameter registry + CI check for public sourcing/justification.

## Project context and governance

- `requirements.md` — what this project is for and acceptance criteria
- `design.md` — architecture and modelling approach
- `tasks.md` — roadmap
- `context/` — evidence registry, provenance, glossaries, context pack
