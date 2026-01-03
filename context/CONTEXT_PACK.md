# Context Pack — NHRA game-theory repo (built 2026-01-03)


---

## requirements.md

# requirements.md — NHRA game-theory + system-dynamics modelling for RACMA

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

# design.md — Architecture, modelling approach, and evidence system

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
parameter,description,value,units,source_type,citation_or_file,locator,range_low,range_high,justification,group
nep_to_cost_ratio_metro,Model parameter,0.9,unitless,assumed,,,0.72,1.08,Stylised mechanism parameter,Funding
nep_to_cost_ratio_regional,Model parameter,0.83,unitless,assumed,,,0.66,1.0,Stylised mechanism parameter,Funding
nep_to_cost_ratio_remote,Model parameter,0.75,unitless,assumed,,,0.6,0.9,Stylised mechanism parameter,Funding
rurality_weight,Model parameter,0.35,unitless,assumed,,,0.28,0.42,Stylised mechanism parameter,Funding
remote_weight,Model parameter,0.07,unitless,assumed,,,0.05,0.09,Stylised mechanism parameter,Funding
nominal_cth_share_target,Model parameter,0.45,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.3,0.6,Stylised mechanism parameter,Funding
effective_cth_share_base,Model parameter,0.38,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.3,0.46,Stylised mechanism parameter,Funding
cap_growth,Model parameter,0.065,fraction/year,assumed,,,0.05,0.08,Stylised mechanism parameter,Funding
has_cumulative_cap,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter,Funding
use_equilibrium_bargaining,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter,Behavioural
use_stage_game_equilibria,Model parameter,True,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter,Behavioural
equilibrium_selection_rule,Model parameter,payoff_dominant,unitless,assumed,,,,,Stylised mechanism parameter,Behavioural
nep_per_nwau_start,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter,Pricing
nep_annual_growth,Model parameter,0.03,fraction/year,primary,https://www.ihacpa.gov.au/resources/national-efficient-price-determination-2025-26,NEP Indexation,0.01,0.08,Stylised mechanism parameter,Pricing
representative_nwau,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter,Pricing
input_cost_per_nwau_start,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter,Pricing
input_cost_annual_growth,Model parameter,0.04,fraction/year,primary,https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia,WPI Health,0.01,0.08,Stylised mechanism parameter,Pricing
demand_base,Model parameter,1.0,unitless,assumed,,,0.8,1.2,Stylised mechanism parameter,Operations
avoidable_ed_share,Model parameter,0.18,fraction,secondary,https://www.publichospitalfunding.gov.au/,NHRA Agreement,0.1,0.3,Stylised mechanism parameter,Operations
discharge_delay_base,Model parameter,1.0,unitless,assumed,,,0.5,2.0,Stylised mechanism parameter,Operations
bed_capacity_index,Model parameter,1.0,unitless,assumed,,,0.7,1.3,Stylised mechanism parameter,Operations
cost_shifting_intensity,Model parameter,0.35,unitless,assumed,,,0.05,0.8,Stylised mechanism parameter,Policy
fragmentation_index,Model parameter,1.0,unitless,assumed,,,0.6,1.5,Stylised mechanism parameter,Policy
audit_pressure,Model parameter,0.5,unitless,assumed,,,0.05,1.0,Stylised mechanism parameter,Policy
admin_burden_weight,Model parameter,0.25,unitless,assumed,,,0.05,0.6,Stylised mechanism parameter,Policy
occupancy_base,Model parameter,0.88,unitless,assumed,,,0.7,1.0,Stylised mechanism parameter,Clinical
offload_base_min,Model parameter,18.0,unitless,assumed,,,5.0,60.0,Stylised mechanism parameter,Clinical
within4_base,Model parameter,0.53,unitless,assumed,,,0.3,0.8,Stylised mechanism parameter,Clinical
rr_beta_pressure,Model parameter,0.35,unitless,assumed,,,0.1,0.6,Stylised mechanism parameter,Clinical
rr_beta_offload,Model parameter,0.015,unitless,assumed,,,0.0,0.05,Stylised mechanism parameter,Clinical
offload_threshold_min,Model parameter,20.0,unitless,assumed,,,10.0,40.0,Stylised mechanism parameter,Clinical
tau,Model parameter,0.25,unitless,assumed,,,0.1,0.5,Stylised mechanism parameter,Behavioural
bargaining_cost,Model parameter,0.12,unitless,assumed,,,0.05,0.3,Stylised mechanism parameter,Behavioural
political_salience,Model parameter,0.3,unitless,assumed,,,0.05,0.8,Stylised mechanism parameter,Policy
use_quantal_response,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter,Behavioural
qre_lambda,Model parameter,4.0,unitless,assumed,,,1.0,10.0,Stylised mechanism parameter,Behavioural
use_burden_feedback,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter,Behavioural
burden_to_throughput_beta,Model parameter,0.06,unitless,assumed,,,0.0,0.2,Stylised mechanism parameter,Behavioural
noise_sd,Model parameter,0.03,unitless,assumed,,,0.01,0.1,Stylised mechanism parameter,Behavioural
capacity_lag,Model parameter,0.15,unitless,assumed,,,0.05,0.5,Stylised mechanism parameter,Operations
orchestration_mode,Model parameter,simultaneous,unitless,assumed,,,,,Stylised mechanism parameter,Policy
isolated_game,Model parameter,None,unitless,assumed,,,,,Stylised mechanism parameter,Policy
cap_rule_type,Model parameter,hard,unitless,assumed,,,,,Stylised mechanism parameter,Policy
audit_rule_type,Model parameter,proportional,unitless,assumed,,,,,Stylised mechanism parameter,Policy
adjustment_cost_beta,Model parameter,5.0,unitless,assumed,,,1.0,10.0,Stylised mechanism parameter,Operations
cannibalization_beta,Model parameter,0.1,unitless,assumed,,,0.0,0.5,Stylised mechanism parameter,Policy
block_funding_base,Model parameter,0.15,fraction,assumed,,,0.05,0.3,Stylised mechanism parameter,Funding
shifting_friction,Model parameter,0.05,unitless,assumed,,,0.0,0.2,Stylised mechanism parameter,Funding
signal_lag_months,Model parameter,1.0,months,assumed,,,0.0,6.0,Stylised mechanism parameter,Lags
claims_lag_months,Model parameter,3.0,months,assumed,,,0.0,12.0,Stylised mechanism parameter,Lags
gp_out_of_pocket,Model parameter,40.0,NZD,assumed,,,0.0,120.0,Stylised mechanism parameter,Choice
gp_wait_time_min,Model parameter,15.0,minutes,assumed,,,0.0,120.0,Stylised mechanism parameter,Choice
patient_time_value_hour,Model parameter,25.0,NZD/hour,assumed,,,5.0,100.0,Stylised mechanism parameter,Choice
expansion_lag,Model parameter,0.1,unitless,assumed,,,0.05,0.3,Stylised mechanism parameter,Operations
contraction_lag,Model parameter,0.2,unitless,assumed,,,0.05,0.5,Stylised mechanism parameter,Operations
use_sequential_bargaining,Model parameter,False,unitless,assumed,,,0.0,0.0,Stylised mechanism parameter,Behavioural
discount_rate,Model parameter,0.9,unitless,assumed,,,0.5,1.0,Stylised mechanism parameter,Behavioural
economic_spine,Historical NEP and WPI series,(DataFrame),unitless,calibrated,https://www.ihacpa.gov.au/,,,Ingested from official sources,Pricing
cap_rule,Runtime rule object,(runtime),unitless,assumed,,,,,Runtime rule object,Policy
audit_rule,Runtime rule object,(runtime),unitless,assumed,,,,,Runtime rule object,Policy
eligibility_rule,Runtime rule object,(runtime),unitless,assumed,,,,,Runtime rule object,Policy
reconciliation_rule,Runtime rule object,(runtime),unitless,assumed,,,,,Runtime rule object,Policy
spine,Economic spine time series,(EconomicSpineJax|None),unitless,calibrated,https://www.ihacpa.gov.au/,,,Economic inputs,Pricing
```


---

## 08_glossary_abbreviations.md

# Glossary and Abbreviations

## Acronyms & Domain Terms
- **ABF**: Activity-Based Funding. A funding method where hospitals are paid based on the number and mix of services provided.
- **ACEC**: Australian Emergency Care Classification.
- **AIHW**: Australian Institute of Health and Welfare.
- **IHACPA**: Independent Health and Aged Care Pricing Authority. Sets the NEP.
- **IHPA**: Independent Hospital Pricing Authority (historic name).
- **NEP**: National Efficient Price (annual $/NWAU, determined by IHACPA).
- **NWAU**: National Weighted Activity Unit. A measure of health service activity expressed as a common unit of cost.
- **NHFB**: National Health Funding Body. Administers the payments.
- **NHRA**: National Health Reform Agreement. The policy framework being modeled.
- **VFI**: Vertical Fiscal Imbalance. The mismatch between revenue raising powers and expenditure responsibilities.
- **ED≤4h**: Emergency Department performance metric (Percentage of presentations completed within 4 hours).
- **LHN**: Local Hospital Network. The state-managed entity operating hospitals.

## Game Theoretic Concepts
- **Nash Equilibrium**: A stable state of a system involving the interaction of different participants, in which no participant can gain by a unilateral change of strategy.
- **Cost Shifting**: Strategic action where an agent transfers costs to another agent without a corresponding transfer of benefits.
- **Upcoding**: Systematically assigning higher-paying codes to patient encounters than is warranted by the clinical documentation.
- **Fragility Node**: A point in the system (e.g., information lag) that is structurally vulnerable to exploitation or failure.
- **Information Lag**: The delay between an action (e.g., treating a patient) and the observation of its outcome (e.g., data reporting), creating strategic ambiguity.

## Parameter Mapping (Manuscript vs. Code)
This table maps the mathematical symbols used in the manuscripts to the variable names in the `nhra_gt` codebase.

| Manuscript Symbol | Code Variable | Description |
| :--- | :--- | :--- |
| $\alpha$ (Alpha) | `nwau_utility` | Weight placed on revenue generation in the agent's utility function. |
| $\beta$ (Beta) | `kpi_satisfaction` / `ramping_penalty` | Weight placed on reputation or KPI satisfaction (often related to tipping points). |
| $\theta$ (Theta) | `coding_intensity` | The level of upcoding effort exerted by the LHN. |
| $P_{audit}$ | `audit_pressure` | The probability or intensity of an audit by the regulator. |
| $\delta$ (Delta) | `discount_rate` | Factor used to discount future payoffs in sequential or multi-period games. |
| $C_{adjust}$ | `adjustment_costs` | Cost associated with changing capacity or service levels (frictional cost). |


---
## Missing files

- tasks.md

- 05_evidence_provenance.md
