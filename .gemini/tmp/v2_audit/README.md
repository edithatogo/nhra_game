# NHRA game-theoretic mechanism models (v2)

This repository provides **publication-ready, reproducible** stylised game-theoretic models for NHRA dynamics,
plus a small Markov Perfect Equilibrium (MPE) extension (V7.2/V8) used for scenario and sensitivity analysis.

> These models are **not forecasts**. They are conceptual “mechanism models” to test how incentives, constraints,
and governance levers can shift system-level outcomes.

## Structure
- `src/` — model code (V1–V5 scripts + MPE models)
- `scripts/` — runnable entrypoints
- `outputs/` — generated plots/tables
- `reports/` — embedded report (markdown)
- `.github/workflows/` — CI checks (lint + tests)

## Run everything (recommended)
```bash
python scripts/run_all.py
```

## Run fast MPE scenario suite only
```bash
python scripts/run_mpe.py --fast
```

## Reproducibility
- Deterministic seeds are used where stochasticity exists.
- CI uses “fast” settings so the pipeline stays lightweight.
