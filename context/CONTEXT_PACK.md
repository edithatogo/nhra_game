# Context Pack — NHRA game-theory repo (built 2025-12-24)


---

## requirements.md

# requirements.md — NHRA game-theory + system-dynamics modelling for RACMA (v21)

**Version:** v21  
**Date:** 2025-12-21  
**Audience:** RACMA Policy & Advocacy Directorate; technical collaborators; reviewers (MJA)

## Problem statement

NHRA negotiations (2025–2030) require decision‑relevant insight into how **vertical fiscal imbalance**, **activity‑based funding rules (NEP × NWAU)**, and **interface constraints** (aged care/NDIS/primary care) translate into operational risk and throughput failure (e.g., ED crowding, access block, ambulance offload delay). RACMA requires analysis that is:

1. Mechanistically credible (causal story and incentives).
2. Quantitatively disciplined (parameters traceable to public evidence or justified).
3. Communicable (figures/tables that support both a RACMA position statement and an MJA original article).

## Primary users

- **RACMA policy leaders:** need an interpretable “negotiation dashboard” and mechanism-ranked asks.
- **MJA reviewers/readers:** need transparent methods, parameter grounding, robustness checks.
- **Technical maintainers:** need reproducible runs, CI, and a portable context pack.

## Objectives

1. Produce a **model-based policy analysis** of NHRA mechanisms, with explicit treatment of:
   - NEP as annual **$/NWAU** and payments as **NEP × NWAU** (stylised where needed).
   - input-cost growth vs NEP indexation drift (“valuation divergence”).
   - strategic interactions (“games”) that drive cost shifting and governance fragmentation.
2. Provide **decision-relevant outputs**:
   - scenario comparisons (baseline vs policy packages),
   - one-way + probabilistic sensitivity (where supported by evidence),
   - equilibrium transparency (solving stage-game equilibria; deterministic checks for dynamics).
3. Maintain a strict **publicly retrievable evidence constraint**: every non-trivial parameter must have
   - a public URL with locator (page/table/section), **or**
   - be explicitly labelled **assumed** with detailed justification + sensitivity bounds.

## Scope

### In-scope
- Mechanism-level modelling of NHRA dynamics and incentives (Commonwealth vs state split levers).
- Stage games (definition/bargaining/cost shifting/discharge coordination/governance/compliance).
- System dynamics for pressure, discharge delay, and flow proxies.
- Evidence registry and context pack generation.
- Reproducible pipeline: `just`, `snakemake`, CI checks.

### Out-of-scope (for now)
- Full implementation of IHACPA NWAU XLSB calculators at runtime.
- Jurisdiction‑specific hospital cost accounting.
- Patient-level simulation; individual facility operational optimisation.

## Functional requirements

- FR1: Generate baseline trajectories (2025–2030) for:
  - pressure index, risk proxy, offload proxy, ED within‑4 proxy, efficiency gap.
- FR2: Solve **all Nash equilibria** for each stage game at each year’s mean state.
- FR3: Produce intervention scenarios reflecting RACMA “asks” (pooled funding, UCC governance integration, NEP alignment).
- FR4: Produce evidence-linked figures and tables with captions and abbreviations.

## Non-functional requirements

- NFR1: Reproducible runs (seeded, deterministic options available).
- NFR2: CI quality gates:
  - lint + formatting,
  - tests,
  - per-file coverage threshold,
  - evidence-grounding checks,
  - context pack build.
- NFR3: Clear separation between **model code** and **evidence/data**.

## Acceptance criteria

- A1: `just all` and `snakemake` complete on a clean machine.
- A2: `scripts/check_parameters_grounded.py` passes with **public-only** sources.
- A3: Reports contain titled tables and figures with captions, abbreviations, and narrative synthesis.


---

## design.md

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


---

## tasks.md

# tasks.md — Roadmap and implementation plan (v21)

**Version:** v21  
**Date:** 2025-12-21

## Completed in v21

1. Added **requirements.md**, **design.md**, **tasks.md** as durable context artifacts.
2. Extended the **context pack** to incorporate these artifacts.
3. Tightened the grounding system to enforce **publicly retrievable sources only**.
4. Updated developer workflows (`just`, `snakemake`) to build the context pack and run grounding checks.

## Next (v22) — make the model more “MJA original article” ready

### Empirical spine
- Add NEP time series sourced to public IHACPA determinations (annual $/NWAU) with locators.
- Add input-cost proxy series (ABS WPI health) with locators.
- Add a lightweight back-test: demonstrate the model reproduces directionality of 2–3 observed indicators.

### Reporting
- Add an “NHRA negotiation dashboard”:
  - threshold plot for effective share drift,
  - ranked intervention table with uncertainty ranges.
- Expand the methods appendix and the parameter registry export into the paper-ready format.

### Robustness
- Add PSA with evidence-based distributions for selected parameters.
- Add stability analysis summary for deterministic dynamics.

## Governance and maintenance

- Maintain a `decisions/` log for major modelling choices.
- Ensure each version update:
  - increments CHANGELOG,
  - regenerates CONTEXT_PACK.md/json,
  - re-runs `just all` in CI.


---

## 00_project_intent.md

# Project intent (local handover)

This repository contains **stylised mechanism models** and **game-theory maps** designed to support:

1) RACMA’s **NHRA negotiation positioning (2025–2030)**, and
2) an **MJA original article** focusing on *governance, incentives, and system pressure* (not forecasting).

## What this is
- A reproducible set of small models encoding hypothesised mechanisms:
  - valuation divergence (NEP vs inputs)
  - vertical fiscal imbalance (VFI) spillovers
  - discharge coordination/exit block dynamics
  - governance integration choices
  - compliance/audit dynamics
  - strategic interaction (“games”) among key actors

## What this is not
- Not a prediction tool.
- Not an ABF calculator.
- Not a mortality model.

## Outputs that matter
- A short set of **decision-ready figures** that are stable across scenarios.
- A transparent **parameter registry** with public sources or explicit assumption justifications.
- A **position statement** narrative aligned to the mechanism findings.

## Primary policy questions
See `context/01_policy_questions.md`.


---

## 01_policy_questions.md

# Policy questions

These questions are the “north star” for both the **RACMA position statement** and the **MJA article**.

## Negotiation questions
1. When the Commonwealth offers “45%”, what *exactly* is being shared?
   - 45% of **efficient price** (NEP × NWAU), 45% of **efficient growth**, or 45% of **actual cost**?
2. Under what conditions does a **capped** grant (hard/soft cap) shift financial risk to States?
3. How do different cap designs (hard cap vs cumulative catch‑up) change incentives?

## System performance questions
4. How does **vertical fiscal imbalance** create predictable pathways from upstream constraints
   (primary care, aged care, disability supports) to downstream pressure (ED throughput, occupancy, offload)?
5. Which levers are likely to reduce **exit block** most effectively (aged care capacity, discharge coordination,
   interoperability, middle‑tier workforce)?

## Governance questions
6. Which “integration” interventions are most likely to improve safety without adding administrative burden?
7. What contractual and governance conditions should attach to Commonwealth-funded models (e.g., UCCs)
   to avoid fragmentation?


---

## 03_model_overview.md

# Model overview

## What the models are
These models are **stylised mechanism models** that combine:
- a **system dynamics backbone** (pressure → occupancy/offload/ED≤4h), and
- a layer of interacting **stage games** (bargaining/definition/cost-shifting/discharge/governance/compliance/signalling).

They are designed for *scenario comparison* and *mechanism explanation*.

## What the models are not
- Not a forecast, not an econometric model, not a clinical-outcomes model.
- Not suitable for estimating real-world morbidity/mortality.

## Core state variables
- **Pressure (index):** composite of demand, discharge delay, and valuation divergence.
- **Occupancy:** proxy for access block.
- **Ambulance offload minutes:** proxy for ED access block.
- **ED≤4h:** throughput proxy.
- **Risk proxy:** comparative index derived from pressure/offload/ED≤4h.

## Parameterisation philosophy
All parameters must be either:
1) backed by a **publicly retrievable source**, or
2) explicitly labelled as an **assumption/calibration**, with a written rationale and a plausible range for sensitivity analysis.

The canonical record is `context/04_parameter_registry.csv`.


---

## 04_parameter_registry.csv

```csv
parameter,description,value,units,source_type,citation_or_file,locator,range_low,range_high,justification
nep_to_cost_ratio_metro,mechanism,0.9,unitless,assumed,,,0.6,1.05,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
nep_to_cost_ratio_regional,mechanism,0.83,unitless,assumed,,,0.6,1.05,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
nep_to_cost_ratio_remote,mechanism,0.75,unitless,assumed,,,0.6,1.05,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
rurality_weight,mechanism,0.35,unitless,assumed,,,0.0,0.6,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
remote_weight,mechanism,0.07,unitless,assumed,,,0.0,0.6,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
nominal_cth_share_target,mechanism,0.45,unitless,assumed,,,0.25,0.55,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
effective_cth_share_base,mechanism,0.38,unitless,assumed,,,0.25,0.55,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
cap_growth,NHFB summary of Addendum clause A56 / funding cap.,0.065,fraction per year,primary,https://www.publichospitalfunding.gov.au/basis-national-health-reform-funding-commonwealth-2020-21-2024-25,Funding Cap (A56): Overall growth capped at 6.5% a year,0.04,0.09,Public source provides a defensible anchor; treat as scenario input when uncertain. Range widened to support sensitivity around cap relaxation/tightening.
has_cumulative_cap,mechanism,False,unitless,assumed,,,,,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
use_equilibrium_bargaining,mechanism,False,unitless,assumed,,,,,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
use_stage_game_equilibria,mechanism,True,unitless,assumed,,,,,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
equilibrium_selection_rule,mechanism,payoff_dominant,unitless,assumed,,,,,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
nep_per_nwau_start,Model uses NEP mostly for reporting; set to index=1 unless using actual $/NWAU.,1.0,$ per NWAU (or index=1),normalisation,,,0.8,1.2,"Normalisation constant: we set NEP start to 1.0 as an index baseline (not a literal NEP $/NWAU). Scenario results depend on growth differentials and relative changes, not the absolute NEP level. Sensitivity explores 0.8–1.2 to confirm scaling invariance."
nep_annual_growth,Keep as scenario parameter; use public determination for plausibility.,0.03,fraction per year,assumed,,,0.01,0.06,Assumed NEP annual growth rate used for stylised valuation-drift scenarios. In v21 we avoid implying a specific IHACPA indexation figure unless a full publicly-sourced NEP time series is ingested (planned v22). Bounds 1–6% cover plausible annual movements in administered price growth; sensitivity analysis assesses robustness.
representative_nwau,mechanism,1.0,unitless,assumed,,,0.8,1,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
input_cost_per_nwau_start,mechanism,1.0,unitless,assumed,,,0.8,1,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
input_cost_annual_growth,Proxy for workforce cost growth; adjust as needed.,0.028,fraction per year,primary,https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/dec-2024,"Dec 2024: Health care and social assistance annual change 2.8% (WPI, original series)",0.015,0.05,"Uses ABS Wage Price Index (WPI) for Health care and social assistance as a publicly available proxy for workforce input-cost growth. This is a proxy (not full cost index) but is transparent, updateable, and suitable for sensitivity. Range allows higher locum/award shocks."
demand_base,mechanism,1.0,unitless,assumed,,,25.0,25.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
avoidable_ed_share,mechanism,0.18,unitless,assumed,,,0.25,0.55,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
discharge_delay_base,mechanism,1.0,unitless,assumed,,,25.0,25.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
bed_capacity_index,mechanism,1.0,unitless,assumed,,,0.8,1,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
cost_shifting_intensity,mechanism,0.35,unitless,assumed,,,0.28,0.42,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
fragmentation_index,mechanism,1.0,unitless,assumed,,,0.8,1,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
audit_pressure,mechanism,0.5,unitless,assumed,,,0.4,0.6,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
admin_burden_weight,mechanism,0.25,unitless,assumed,,,0.0,0.6,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
occupancy_base,mechanism,0.88,unitless,assumed,,,25.0,25.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
offload_base_min,mechanism,18.0,unitless,assumed,,,25.0,25.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
within4_base,Use latest available national figure when updating.,0.53,fraction,secondary,https://www.aihw.gov.au/reports-data/myhospitals/sectors/emergency-department-care,2024–25: 53% of ED visits completed within 4 hours (national),0.45,0.65,Public source provides a defensible anchor; treat as scenario input when uncertain.
rr_beta_pressure,mechanism,0.35,unitless,assumed,,,0.28,0.42,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
rr_beta_offload,mechanism,0.015,unitless,assumed,,,0.012,0.018,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
offload_threshold_min,mechanism,20.0,unitless,assumed,,,16,24,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
tau,mechanism,0.25,unitless,assumed,,,0.2,0.3,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
bargaining_cost,mechanism,0.12,unitless,assumed,,,0.096,0.144,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
political_salience,mechanism,0.3,unitless,assumed,,,0.24,0.36,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Range set as ±20% default for sensitivity where no published bounds are available.
noise_sd,mechanism,0.03,unitless,assumed,,,0.0,0.1,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis.
```


---

## 08_glossary_abbreviations.md

# Glossary and abbreviations

- **ABF**: Activity-based funding.
- **ACEC**: Australian Emergency Care Classification.
- **AIHW**: Australian Institute of Health and Welfare.
- **IHACPA**: Independent Health and Aged Care Pricing Authority.
- **IHPA**: Independent Hospital Pricing Authority (historic name).
- **NEP**: National Efficient Price (annual $/NWAU, determined by IHACPA) used with a service **NWAU** weight to compute an efficient payment.
- **NWAU**: National Weighted Activity Unit.
- **NHFB**: National Health Funding Body.
- **NHRA**: National Health Reform Agreement.
- **VFI**: Vertical fiscal imbalance.
- **ED≤4h**: Percentage of ED presentations completed within 4 hours.


---
## Missing files

- 05_evidence_provenance.md
