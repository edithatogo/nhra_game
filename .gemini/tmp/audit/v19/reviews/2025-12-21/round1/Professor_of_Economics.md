# Simulated Review (Round 1)

**Date:** 21 December 2025

**Version under review:** v15 (0.15.0)


## Summary
The modelling is an accessible bridge between game-theoretic incentives and system performance. The main risks are equilibrium selection justification, calibration discipline, and distinguishing descriptive vs normative claims.

## Major comments
1. **Equilibrium selection**: If multiple Nash equilibria exist, you need a principled selection approach (risk-dominant, welfare-dominant, quantal response).
2. **Calibration and identification**: State what is calibrated, what is assumed, and what is explored via sensitivity.
3. **Policy evaluation**: Present interventions as counterfactuals with uncertainty bands.

## Specific recommendations
- Add equilibrium multiplicity and selection sensitivity as first-class outputs.
- Add Monte Carlo intervals for key outcomes.
- Add a decomposition showing the marginal effect of each “game” on the risk proxy (influence network).
