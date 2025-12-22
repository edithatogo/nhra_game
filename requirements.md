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
