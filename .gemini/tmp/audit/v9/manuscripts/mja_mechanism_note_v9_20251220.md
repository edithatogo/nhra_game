# Negotiating the National Health Reform Agreement: a stylised mechanism model and game-theory map of “45%” vs “50%”

**Authors:** Dylan A. Mordaunt (drafting author)  
**Date:** 20 Dec 2025  
**Article type:** Policy / perspective + methods appendix (stylised model)

## Abstract (draft)

Debate about the National Health Reform Agreement (NHRA) often pivots on a nominal Commonwealth “share” of public hospital funding (e.g., “45%”). In practice, the *experienced* share depends on definitional choices (what counts as the base), indexation realism, and how pressures are managed across Commonwealth/state interfaces (primary care access, aged care placement/pricing, disability supports, community services, and hospital discharge). We present a **stylised mechanism model** and a companion **game-theory map** that connect negotiation choices (bargaining, definition, caps, cost-shifting, and governance integration) to downstream operational proxies (occupancy, offload delay, ED performance) and a conservative comparative **risk proxy**. The model uses seeded Monte Carlo sampling to illustrate uncertainty without spurious precision, and is paired with publication-ready Mermaid/Graphviz figures and an interactive D3 visualisation to support communication and iteration.

## The problem: “share” is a game about definitions

Nominal “share” numbers compress multiple disputes into a single headline. At least four mechanisms matter:

1. **Definition game**: whether the denominator is *NEP-like* (policy-defined efficient price) versus *actual* cost growth (wages, agency staffing, pharmaceuticals, energy, capital, compliance).  
2. **Cap game**: whether Commonwealth exposure is capped or open-ended, and how caps interact with demand growth.  
3. **Cost-shifting game**: incentives to shift pressures across Commonwealth/state responsibilities (GP access, aged care placement/pricing, NDIS planning/provider availability).  
4. **Governance game**: whether there are integrated levers (pooled funding, shared performance governance) that reduce the payoff to “shifting” and increase the payoff to “solving”.

## A stylised model to connect negotiation to operational reality

We implement a deliberately conservative hybrid model that:

- converts *nominal share* into an **effective share** as a function of indexation realism and definitional “base” (NEP vs actual);  
- translates effective share gaps into a **pressure index**;  
- maps pressure into operational proxies (ED within 4 hours; offload delay), with feedback from discharge integration; and  
- converts pressure + offload into a **relative risk proxy** (a comparative indicator, not a clinical event rate).

The model uses **Monte Carlo** sampling (seeded RNG for reproducibility) to show uncertainty bands and avoid spurious precision.

## Game-theory map (diagrams)

This repo contains a complete Mermaid ↔ Graphviz pipeline, with publication exports in `outputs/v9/diagrams/`.

- Graphical abstract: `outputs/v9/diagrams/graphical_abstract_v9.png`  
- Games network (minimal): `outputs/v9/diagrams/games_network_minimal_v9.png`  
- Risk pathway: `outputs/v9/diagrams/risk_pathway_v9.png`

An interactive D3 version is produced at `outputs/v9/interactive/games_network_d3.html`, where node colours can be driven by scenario outputs.

## Results: what the model is designed to show (not predict)

Across scenarios, the model is designed to surface a small number of robust qualitative results:

- **Nominal vs effective share divergence** becomes large when indexation is unrealistic or the base excludes real cost growth.  
- Under divergence, the system “solves” through **pressure**: rising occupancy, discharge delay, offload delay, and ED performance degradation.  
- Governance levers that integrate incentives (pooled funding, discharge integration, interoperability) can reduce the payoff to cost-shifting and reduce downstream risk proxies.

Quantitative results should be read as **internal comparisons** (scenario A vs B under common assumptions), not absolute forecasts.

## Why this helps NHRA negotiation

The model and diagrams provide:
- a shared language for **what exactly is being negotiated** (definition, cap, indexation, levers);  
- a transparent pathway from negotiation choices to operational consequences; and  
- a way to stress-test “packages” of levers (including via optional optimisation search with Optuna) without pretending the system is fully knowable.

## Methods appendix (repo)

- Model: `src/nhra_game_theory/v8.py`  
- Pipeline runner: `scripts/run_v8_all.py`  
- Diagrams pipeline: `scripts/diagrams/render_all.py`  
- Interactive D3 build: `scripts/interactive/make_d3_network_v9.py`  
- Additional plots: `scripts/make_additional_plots_v9.py`  
- Optional optimisation: `scripts/optimize_optuna_v9.py` (install extra: `.[opt]`)

## Disclosures / limitations (to include)

- Stylised model; not a budget model; not a clinical risk model.  
- Parameter values are chosen for interpretability and sensitivity exploration, not calibration.  
- Results are sensitive to structural assumptions; the value is in making these explicit.

