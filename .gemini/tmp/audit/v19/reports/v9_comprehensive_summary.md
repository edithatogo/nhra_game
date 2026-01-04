# v9 repository update: diagrams + engineering + dynamic visualisations

Date: 2025-12-20

## What changed in v9

### Diagram pipeline (Mermaid ↔ Graphviz)

- **User Mermaid diagrams**: `diagrams/mermaid_user/`
- Mermaid → **auto DOT**: `diagrams/graphviz_from_mermaid/`
- **Graphviz sources**: `diagrams/graphviz_sources/`
- Graphviz → **auto Mermaid**: `diagrams/mermaid_from_graphviz/`
- Publication exports (PNG + SVG): `outputs/v9/diagrams/`

Render + convert:

```bash
PYTHONPATH=src python scripts/diagrams/render_all.py
```

### Publication-quality interactive (D3)

Generated into:

- `outputs/v9/interactive/games_network_d3.html`
- `outputs/v9/interactive/games_network_v9.json`
- `outputs/v9/interactive/scenario_timeseries_v9.json`

Build:

```bash
PYTHONPATH=src python scripts/interactive/make_d3_network_v9.py
```

### More plots

Additional v9 plots are written to `outputs/v9/plots/`:

```bash
PYTHONPATH=src python scripts/make_additional_plots_v9.py
```

### Engineering / reproducibility

Added:

- Dockerfile
- Snakemake (`Snakefile`) + Justfile
- pre-commit hooks (ruff + hygiene)
- tox
- mypy strict (with ignore-missing-imports for third-party stubs)
- MkDocs site (`mkdocs.yml` + `docs_mkdocs/`)
- Hypothesis property-based tests
- Dependabot

## Stochasticity + “dynamic diagrams”

- The v8 hybrid model runs **Monte Carlo** with a **seeded RNG** (reproducible).
- The D3 network is **dynamic**: node colouring can be driven by scenario/year/metric, and can be extended to animation or edge-weight updates from sensitivity metrics.

## Optimisation (Optuna)

Added:

- `scripts/optimize_optuna_v9.py` (install with `pip install -e '.[opt]'`)

Use it to search “policy lever packages” that minimise a composite objective (risk proxy + offload penalty + ED≤4h reward). It’s best for generating candidate packages to narrate and stress-test.

## Scenario summary (2030 endpoints)

| scenario           | interventions                                                                                 |   pressure_2030 |   rr_2030 |   within4_2030 |   offload_2030 |   effshare_nominal_2030 |   effshare_effective_2030 |   effgap_2030 |
|:-------------------|:----------------------------------------------------------------------------------------------|----------------:|----------:|---------------:|---------------:|------------------------:|--------------------------:|--------------:|
| baseline           | (none)                                                                                        |           1.134 |     1.05  |          0.504 |         17.7   |                   0.444 |                     0.386 |         0.149 |
| pooled_funding     | pooled_funding                                                                                |           1.132 |     1.049 |          0.505 |         17.695 |                   0.444 |                     0.386 |         0.149 |
| ucc_integration    | ucc_integration                                                                               |           1.112 |     1.04  |          0.515 |         14.782 |                   0.444 |                     0.386 |         0.149 |
| nep_realism        | nep_realism                                                                                   |           1.126 |     1.047 |          0.508 |         17.639 |                   0.436 |                     0.394 |         0.106 |
| discharge_capacity | aged_ndis_capacity                                                                            |           1.087 |     1.032 |          0.528 |         17.523 |                   0.444 |                     0.386 |         0.15  |
| bundle_all         | pooled_funding, ucc_integration, nep_realism, aged_ndis_capacity, middle_tier, cumulative_cap |           1.052 |     1.019 |          0.547 |         14.514 |                   0.433 |                     0.396 |         0.093 |

## Key figures (paths)

- Graphical abstract: `outputs/v9/diagrams/graphical_abstract_v9.png` / `.svg`
- Network: `outputs/v9/diagrams/games_network_minimal_v9.png`
- Risk pathway: `outputs/v9/diagrams/risk_pathway_v9.png`
- Interactive D3: `outputs/v9/interactive/games_network_d3.html`

## Notes / limitations

- Mermaid→DOT conversion is best-effort (clusters are flattened).
- Outcomes are stylised proxies: useful for comparative governance reasoning, not forecasting.
