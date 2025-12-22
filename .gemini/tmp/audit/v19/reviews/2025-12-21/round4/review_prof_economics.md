# Round 4 peer-review simulation (v19)

Date: 2025-12-21

## Reviewer: Professor of Economics

### Overall recommendation
**Minor revision.** The modelling approach is coherent and better disciplined.

### Major points
1. **Separation of mechanisms.** The model now cleanly separates (i) exogenous macro drift (NEP vs costs) from (ii) strategic interaction (stage games). This improves interpretability.
2. **Multiple equilibria justify governance focus.** When multiple equilibria exist, policy is about *selection* and *commitment devices*, not marginal tuning. Your equilibrium grids support this point well.
3. **Optimisation (future).** It would be reasonable, in future work, to treat a small subset of levers as decision variables and optimise a weighted objective (e.g., minimise RR subject to fiscal constraints). Optuna is sensible for that extension, but not required for the current scope.

### Minor points
- Add one sentence clarifying why Monte Carlo is used (uncertainty + regime switching), rather than for statistical inference.
- Consider exposing the objective weights explicitly in the report (e.g., macro_drift_weight) so readers can see the “value judgement”.

### Suggested edits
- Add a brief note: “Optimisation is intentionally out-of-scope for v19; the model is used for comparative scenarios and equilibrium mapping.”
