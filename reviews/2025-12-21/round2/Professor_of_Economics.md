# Round 2 Review — Professor of Economics
**Date:** 2025-12-21  
**Scope:** Game-theoretic coherence, equilibrium handling, and welfare interpretation.

## Summary
v16 is conceptually sound for a stylised model. It should avoid over-claiming quantitative precision and should clearly document equilibrium selection assumptions.

## Major points
1. **Equilibria transparency:** Continue exporting all equilibria; add a clear section interpreting multiplicity and selection.
2. **Intervention identification:** Interventions should be described as parameter shifts and linked to mechanisms (avoid “black-box” claims).

## Recommendation
**Minor revision.**

## v17 response / implementation
Implemented in v17 via:
- Equilibria exports at each year’s mean state (outputs/v17/tables/equilibria_by_year.csv).
- Equilibria multiplicity plots per game (outputs/v17/plots/equilibria_count_over_time_*.png).
- Intervention deltas as transparent parameter-shift outputs (report section 4).
