# Track Spec: Model Validation & Backtesting (SOTA)

## Overview

This track implements an advanced econometric validation framework to evaluate and prove the model's predictive fidelity against historical NHRA outcomes (2011–2025). It employs recursive rolling backtesting, structural consistency checks, and a strict "Blind" out-of-sample holdout to ensure the model's credibility for MJA publication and policy-maker trust.

## Functional Requirements

- **FR0: Infrastructure Rigor (Quality Baseline):**
  - Refactor `Params` and `EvidenceRegistry` to use **Pydantic V2** for automated validation and type safety.
  - Implement **Pandera** schemas for all historical and ingested DataFrames to enforce data contracts.
  - Replace `tox` with **Nox** for pure-Python environment orchestration and reproducibility testing.
- **FR1: Historical Reference Ingestion:**
  - Ingest and align historical NHRA datasets: 2011–2019 (Transition), 2020–2022 (COVID Stress), 2023–2025 (Current).
- **FR2: Multi-Metric Validation Engine:**
  - Calculate **RMSE**, **MAPE**, **Theil’s Inequality Coefficient**, **Directional HIT Rate**, and **MAE**.
  - **PSA Calibration Check:** Verify that historical outcomes consistently fall within the model's 95% Confidence Interval.
- **FR3: Recursive Rolling Horizon Validation:**
  - Implement a "Train-Test" loop: Calibrate on data up to Year N, predict Year N+1, compare, and increment across the 2011–2023 period.
- **FR4: Structural Integrity & Mechanism Validation:**
  - Automated verification that the model's "Primary Driver" (identified via GSA) matches historical policy narratives for specific periods (e.g., verifying that the "Efficiency Gap" drove pressure in the mid-agreement slump).
- **FR5: Blind Out-of-Sample Holdout:**
  - Strictly isolate 2024–2025 data. Calibrate on pre-2024 data only, then execute a "Blind Reveal" test to measure true predictive power.
- **FR6: Interactive Validation Dashboard:**
  - **Validation Scorecard:** Tabular metrics by period and horizon.
  - **"Ghost of NHRA Past" Overlay:** Interactive Plotly charts overlaying history vs. model predictions.
- **FR7: Automated Validation Reporting:**
  - Generate an MJA-ready "Technical Validation Report" (Markdown/PDF) including error decomposition and bias analysis.

## Non-Functional Requirements

- **Rigor:** Adherence to STRESS (Strengthening The Reporting of Empirical Simulation Studies) and CHEERS 2022 guidelines for validation reporting.
- **Reproducibility:** Full automation via `scripts/run_validation.py` with versioned reference data.

## Acceptance Criteria

- `scripts/run_validation.py` executes the recursive loop and generates a bias/variance decomposition.
- The "Blind Reveal" test results are documented, with error rates (MAPE) meeting pre-defined scientific thresholds.
- The Dashboard "Ghost Overlay" accurately aligns historical timestamps with model trajectory years.
- All mechanism validation tests confirm that model drivers (e.g., Access Block) are logically consistent with RoGS historical data.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
