# Context and local handover

This project includes a **context system** under `context/` that acts as the single source of truth for:
- project intent and policy questions
- modelling scope, limitations, and assumptions
- abbreviations and reporting checklist guidance

## Quick start
- Build the shareable context pack:

```bash
python scripts/build_context_pack.py
```

This writes `context/CONTEXT_PACK.md`.

## Input traceability
Every model input in `nhra_gt.engine.Params` must be either:
- anchored to a **publicly retrievable source** (URL), or
- explicitly justified with a plausible range for sensitivity analysis.

To check:

```bash
python scripts/check_parameters_grounded.py
```
