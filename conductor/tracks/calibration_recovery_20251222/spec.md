# Track Spec: Re-integrate v2 Calibration Logic into v21

## Overview
This track ports specific calibration logic from the early `v2` implementation into the current `v21` Optuna framework. The goal is to improve the model's predictive fidelity by re-introducing granular bargaining constraints and historical objective functions while maintaining SOTA standards for uncertainty and reproducibility.

## Functional Requirements
- **FR1: Bargaining Game Constraints:** Port parameter bounds and tuning logic from `nhra_games_v2_calibrated.py` to the `v21` model definition.
- **FR2: Integrated Optuna Objective:** Update the Optuna objective function in `v21` to incorporate the ported `v2` historical matching logic.
- **FR3: Calibration Target Suite:** Implement the `v2` ground-truth data points as a formalized calibration target dataset in `data/raw/`.
- **FR4: Stochastic Calibration:** Modify the objective function to include variance penalization from Monte Carlo rollouts (Uncertainty-aware calibration).
- **FR5: Posterior Sampling:** Enable the generation of parameter distributions (posteriors) from the calibration results to support Probabilistic Sensitivity Analysis (PSA).

## Non-Functional Requirements
- **NFR1: Methodological Alignment:** The re-integrated logic must preserve the strategic bargaining behaviors documented in the original `v2` audit.
- **NFR2: Performance Benchmarking:** The new calibration must demonstrate a reduction in residuals (better fit to historical data) compared to the standalone `v2` version.
- **NFR3: CHEERS/STRESS Compliance:** All calibration results must be documented in a way that satisfies the reporting checklists defined in `product-guidelines.md`.
- **NFR4: Regression Testing:** Ensure existing `v21` equilibrium solutions remain stable and solvable under the new constraints.

## Acceptance Criteria
- The Optuna optimization script includes all re-integrated `v2` bargaining constraints and objective terms.
- Calibration runs produce parameter sets that pass the 95% CI validation threshold.
- A technical comparison demonstrates improved model-to-data fit compared to the baseline `v2` implementation.
- **Parameter Sensitivity Report:** A ranked list of parameter importance derived from the posterior sampling is generated.
- The `v21` pipeline remains reproducible and functional via Snakemake.

## Out of Scope
- Porting non-calibration logic from `v2` (e.g., legacy plotting).
- Implementing real-time data feeds (planned for a future track).
