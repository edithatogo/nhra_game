# Context Pack — NHRA game-theory repo (built 2025-12-26)


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

- `src/nhra_gt/` — core model library
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
nep_to_cost_ratio_metro,Model parameter,0.9,unitless,assumed,,,0.7200000000000001,1.08,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
nep_to_cost_ratio_regional,Model parameter,0.83,unitless,assumed,,,0.664,0.9959999999999999,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
nep_to_cost_ratio_remote,Model parameter,0.75,unitless,assumed,,,0.6000000000000001,0.8999999999999999,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
rurality_weight,Model parameter,0.35,unitless,assumed,,,0.27999999999999997,0.42,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
remote_weight,Model parameter,0.07,unitless,assumed,,,0.05600000000000001,0.084,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
nominal_cth_share_target,Model parameter,0.45,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.36000000000000004,0.54,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
effective_cth_share_base,Model parameter,0.38,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.30400000000000005,0.45599999999999996,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
cap_growth,Model parameter,0.065,fraction/year,assumed,,,0.052000000000000005,0.078,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
has_cumulative_cap,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
use_equilibrium_bargaining,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
use_stage_game_equilibria,Model parameter,True,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
equilibrium_selection_rule,Model parameter,payoff_dominant,unitless,assumed,,,,,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
nep_per_nwau_start,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
nep_annual_growth,Model parameter,0.03,fraction/year,primary,https://www.ihacpa.gov.au/resources/national-efficient-price-determination-2025-26,NEP Indexation,0.024,0.036,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
representative_nwau,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
input_cost_per_nwau_start,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
input_cost_annual_growth,Model parameter,0.04,fraction/year,primary,https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia,WPI Health,0.032,0.048,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
demand_base,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
avoidable_ed_share,Model parameter,0.18,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.144,0.216,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
discharge_delay_base,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
bed_capacity_index,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
cost_shifting_intensity,Model parameter,0.35,unitless,assumed,,,0.27999999999999997,0.42,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
fragmentation_index,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
audit_pressure,Model parameter,0.5,unitless,assumed,,,0.4,0.6,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
admin_burden_weight,Model parameter,0.25,unitless,assumed,,,0.2,0.3,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
occupancy_base,Model parameter,0.88,unitless,assumed,,,0.7040000000000001,1.056,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
offload_base_min,Model parameter,18.0,unitless,assumed,,,14.4,21.599999999999998,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
within4_base,Model parameter,0.53,unitless,assumed,,,0.42400000000000004,0.636,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
rr_beta_pressure,Model parameter,0.35,unitless,assumed,,,0.27999999999999997,0.42,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
rr_beta_offload,Model parameter,0.015,unitless,assumed,,,0.012,0.018,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
offload_threshold_min,Model parameter,20.0,unitless,assumed,,,16.0,24.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
tau,Model parameter,0.25,unitless,assumed,,,0.2,0.3,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
bargaining_cost,Model parameter,0.12,unitless,assumed,,,0.096,0.144,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
political_salience,Model parameter,0.3,unitless,assumed,,,0.24,0.36,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
use_quantal_response,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
qre_lambda,Model parameter,4.0,unitless,assumed,,,3.2,4.8,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
use_burden_feedback,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
burden_to_throughput_beta,Model parameter,0.06,unitless,assumed,,,0.048,0.072,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
noise_sd,Model parameter,0.03,unitless,assumed,,,0.024,0.036,Stylised mechanism parameter used for scenario comparison rather than forecasting. Default chosen for face-valid dynamics; explored in sensitivity analysis. Pending formal calibration against jurisdictional data where available.
economic_spine,Historical NEP and WPI series,(DataFrame),unitless,calibrated,https://www.ihacpa.gov.au/,Multiple determinations 2011-2025,,,Ingested from official sources via scripts/data/ingest_economic_spine.py
capacity_lag,Model parameter,0.15,unitless,assumed,,,0.1,0.3,Stylised mechanism parameter representing the operational inertia and hiring friction in expanding bed or workforce capacity. This ensures that system throughput does not adjust instantaneously to demand shocks, reflecting realistic constraints in hospital staffing and physical infrastructure expansion over short time horizons.
orchestration_mode,Model parameter,simultaneous,unitless,assumed,,,,,Strategic control parameter determining whether game-theory sub-games are solved simultaneously (parallel strategic choices) or sequentially (respecting causal dependencies like Signalling before Bargaining). This is critical for exploring how the order of negotiations influences final funding and operational outcomes in the NHRA framework.
isolated_game,Model parameter,None,unitless,assumed,,,,,Diagnostic parameter used in 'isolation mode' to freeze all strategic actors except for one specific sub-game (e.g. Bargaining or Coding). This allows for rigorous counterfactual analysis of individual game mechanics without the confounding noise of interacting strategic feedback loops, aiding in model identification and mechanism validation.
cap_rule_type,Model parameter,hard,unitless,assumed,,,,,Structural policy parameter defining the implementation of the National Funding Growth Cap. 'Hard' represents a strict 6.5 percent limit on Commonwealth growth, while 'Soft' allows for negotiated overages or threshold-based penalties. This enables testing the impact of different budget constraint definitions on jurisdictional bargaining toughness and activity surges.
audit_rule_type,Model parameter,proportional,unitless,assumed,,,,,Integrity regime parameter defining how Auditor agents detect upcoding or boundary-shifting behavior. 'Proportional' risk increases linearly with coding intensity, while 'Threshold' risk spikes only when outliers cross specific statistical bounds. This captures the strategic 'arms race' between provider gaming and regulatory scrutiny in the activity-based funding environment.
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

- tasks.md

- 05_evidence_provenance.md
