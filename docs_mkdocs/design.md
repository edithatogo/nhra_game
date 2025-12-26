# design.md — Architecture, modelling approach, and evidence system (v21)

**Version:** v21  
**Date:** 2025-12-21

## Overview

The repository is designed as a **model-based policy analysis** toolchain with three pillars:

1. **Evidence / Context layer** (public-only parameter grounding, provenance, checklists)
2. **Modelling layer** (stage games + system dynamics; optional stochasticity; deterministic checks)
3. **Outputs layer** (reports, plots, tables, diagrams; reproducible pipelines)

## Repo structure

- `src/nhra_game_theory/` — core model library
- `tests/` — unit + property-like tests; coverage enforced
- `context/` — project intent, policy questions, parameter registry, provenance, glossaries
- `scripts/` — runnable pipelines (versioned; avoid “magic” by keeping scripts thin)
- `outputs/` — generated tables/plots
- `reports/` — rendered narrative reports (MD + HTML)
- `diagrams/` — mermaid + graphviz sources and rendered figures

## Evidence and “public-only” constraint

### Parameter registry
`context/04_parameter_registry.csv` is the single source of truth for parameters.

Each parameter record includes:
- value and units,
- source type (`primary`, `secondary`, `calibrated`, `assumed`, `normalisation`),
- a **public URL** and locator (page/table/section),
- plausible range (low/high) and distribution (optional),
- justification (required for assumptions).

### Enforcement
`scripts/check_parameters_grounded.py` fails CI if:
- a parameter is labelled `primary` or `secondary` and lacks a public URL,
- an URL is not http/https,
- a parameter is `assumed` but justification is insufficiently detailed,
- range bounds are missing.

This ensures the model can be audited by external reviewers.

## Modelling approach

### 1) Stage games
A small set of two-player stage games represent strategic tensions, e.g.:
- definition (what counts as “efficient”),
- bargaining (cap/glide path),
- cost shifting,
- discharge coordination,
- governance integration (UCCs etc),
- compliance/audit incentives.

For each game, the code:
- constructs payoff matrices from state variables (pressure, efficiency gap, discharge delay),
- solves **all Nash equilibria** (pure + mixed) using enumeration / support methods,
- selects equilibria for simulation using a configurable rule (e.g., welfare, risk-dominant).

### 2) System dynamics
A compact set of state variables evolve annually (or finer if needed), including:
- NEP index and input-cost index (publicly sourced where available),
- efficiency gap as cost-per-NWAU relative to NEP,
- pressure, discharge delay, and flow proxies.

The dynamics support:
- stochastic Monte Carlo runs (for robustness),
- deterministic mean-field and fixed-point checks (equation solving for stability).

## Outputs and reporting

### Reports
Reports are built from templates that:
- introduce each results section in full sentences,
- provide figure/table titles, captions, and abbreviations,
- include a synthesis paragraph per section and an overall conclusion.

### Diagrams
Diagrams are maintained in source form:
- `diagrams/*.mmd` (Mermaid)
- `diagrams/*.dot` (Graphviz)

Render scripts generate publication-ready PNG/SVG.

## Reproducibility and CI

- `Justfile` provides a consistent local interface.
- `Snakefile` provides a DAG for pipelines.
- `.github/workflows/ci.yml` runs:
  - lint/format, tests, coverage gates, grounding checks, context pack build.
