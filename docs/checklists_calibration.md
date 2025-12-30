# Reporting Checklists: Calibration Track (v21)

**Date:** 2025-12-23  
**Track:** calibration_recovery_20251222

## STRESS (Simulation Study Reporting)
- **Objectives:** Align stylised model with empirical Australian health system benchmarks to ensure predictive fidelity.
- **Model Logic:** Hybrid Game-Theory + System Dynamics (implemented in `src/nhra_game_theory/v9.py`).
- **Data Sources:**
    - IHACPA NEP 2024-25 ($6,465/NWAU).
    - AIHW ED performance metrics (53% within 4 hours).
    - Medicare UCC handover data.
- **Randomness:** 100 Monte Carlo rollouts per trial; seeded RNG (42).
- **Calibration Method:** Optuna TPESampler using a stochastic objective function (MSE of means + 0.5 * average variance).

## CHEERS 2022 (Health Economic Evaluation)
- **Analytical Methods:** Model-based policy analysis using Nash Equilibrium solving for stage games.
- **Uncertainty:** Probabilistic Sensitivity Analysis (PSA) supported by posterior parameter distributions saved in `data/calibration/calibration_trials_posterior.csv`.
- **Calibration:** Formalised against a multi-metric target suite (ED, Occupancy, NEP).
