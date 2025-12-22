# Round 2 Review — Professor of Health Policy
**Date:** 2025-12-21  
**Scope:** Policy relevance, governance mechanisms, interpretability, and narrative alignment to NHRA decision points.

## Summary
v16 has good scaffolding. The next improvement is to present outputs in a way that directly supports “what should RACMA ask for?” and “what changes the state variables that create high-pressure equilibria?”.

## Major points
1. **Decision relevance:** Add intervention scenarios that map to specific policy asks (pooled funding pilots, UCC governance integration, aged care placement throughput, NEP indexation realism).
2. **Show deltas:** Present intervention impacts as deltas vs baseline to prevent over-reading absolute values.
3. **Equilibrium selection sensitivity:** Include alternative equilibrium selection assumptions and show robustness of directionality.

## Recommendation
**Minor revision.**

## v17 response / implementation
Implemented in v17 via:
- Intervention scenario set and delta tables (outputs/v17/tables/intervention_scenarios.csv and intervention_deltas.csv).
- Scenario set including equilibrium selection alternatives (row-favourable, random) (outputs/v17/tables/scenario_summary.csv).
- Expanded report narrative linking state variables ↔ mechanisms ↔ asks (reports/v17_report_20251221.md).
