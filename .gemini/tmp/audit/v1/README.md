# NHRA game-theoretic mechanism models (v1 bundle)

This repo packages a set of **stylised** mechanism models intended to support policy discussion about the
National Health Reform Agreement (NHRA) negotiations.

## Contents

- `src/nhra_games_v1.py` — mechanism models (V1)
- `src/nhra_games_v2_calibrated.py` — calibrated variants (V2)
- `src/nhra_hybrid_v3.py` ... `v5` — combined/hybrid dynamics models
- `outputs/` — generated figures and CSVs

## Quick start

```bash
python src/nhra_games_v1.py
python src/nhra_games_v2_calibrated.py
python src/nhra_hybrid_v3.py
python src/nhra_hybrid_v4.py
python src/nhra_hybrid_v5.py
```

Outputs are written to the **current working directory** (each script sets `OUTDIR="."`).
