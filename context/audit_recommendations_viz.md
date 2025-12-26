# Audit Report: Visualization & Reporting Enhancements

**Date:** 2025-12-26

## 1. Current State Assessment

The repository features a mature visualization suite across multiple modalities:
* **Static Time-Series:** quantile ribbons for all core state variables (`trajectories.py`).
* **Interactive:** D3-based network diagrams and Plotly timelines (`interactive.py`).
* **Game-Theoretic:** strategy frequency heatmaps and best-response traces (`distributional.py`).
* **Sensitivity:** Sobol indices and correlation tornado plots (`sensitivity.py`).

## 2. High-Impact Recommendations

The following 4 visualizations are recommended to improve policy communication and model transparency:

### A. VFI Waterfall Plot (Financial Layer)
* **Concept:** A waterfall chart showing the "leakage" from nominal funding to reality.
* **Flow:** `Nominal Share` -> `(-) Indexation Gap` -> `(-) Cap Limit` -> `(-) Audit Clawback` -> `Effective Share`.
* **Why:** This is the core "Policy Story" of the model but is currently only available as a raw dictionary in `engine.py`.

### B. Hysteresis / Phase Space Trajectory (System Dynamics)
* **Concept:** A 2D phase-space plot (e.g., `Pressure` on X-axis, `Occupancy` on Y-axis).
* **Feature:** Color the trajectory by `SystemMode` (Normal, Stress, Crisis).
* **Why:** Visualizes the "tipping points" and recovery paths mechanistically, making the hysteresis logic intuitive.

### C. Equilibrium Selection Stability (Game Layer)
* **Concept:** A time-series of "Iterations to Converge" and "Selection Rule Active".
* **Why:** Validates the robustness of the game solver and highlights periods of "Strategic Volatility" where the system struggles to find a stable coordination point.

### D. Data Pipeline Provenance Dashboard (Infrastructure)
* **Concept:** A "Traffic Light" chart for the Data Registry.
* **Indicators:** `AIHW API (Live)`, `IHACPA NEP (Hardcoded)`, `ABS WPI (Historical)`.
* **Why:** Provides immediate confidence in the grounding of the model results for external reviewers.
