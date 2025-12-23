# Track Spec: Global Sensitivity Analysis (GSA) Suite

## Overview
This track implements a rigorous Global Sensitivity Analysis (GSA) suite using **SALib** to mathematically quantify the influence of policy levers on system risk. It prioritizes the **Morris Method** for screening and **Sobol Analysis** for variance decomposition, aligning with MJA standards for robustness.

## Functional Requirements
- **FR1: SALib Integration:** Implement a `scripts/run_gsa.py` tool that interfaces with `SALib` to define parameter problems and sample distributions.
- **FR2: Multi-Method Support:** The tool must support:
    1.  **Morris Method (Elementary Effects):** For rapid parameter ranking and screening.
    2.  **Sobol Analysis (Variance-based):** For detailed first-order and interaction indices.
    3.  *(Optional)* Delta Moment-Independent Measure.
- **FR3: Parallel Execution:** Implement `multiprocessing` to parallelize model evaluations, enabling the thousands of runs required for GSA.
- **FR4: Future-Proof Architecture:** Design the evaluation loop to be modular, allowing future drop-in replacement with Surrogates (GP) or JAX/XLA accelerators.

## Non-Functional Requirements
- **NFR1: Reporting Ready:** Outputs must include publication-quality figures:
    -   Morris Tornado Plots (Influence vs Non-linearity).
    -   Sobol Interaction Heatmaps.
    -   Convergence Diagnostics (Sensitivity stability vs Sample Size).
    -   Key Driver Scatter Plots.
- **NFR2: Performance:** The suite must be capable of running a ~10,000 sample Sobol analysis in a reasonable timeframe (e.g., <1 hour on a standard multicore workstation) via parallelism.
- **NFR3: Publication Quality:** All visual outputs must be generated in multiple high-quality formats (PNG @ 300dpi, SVG, PDF) with academic standard styling (fonts, axis labels).

## Acceptance Criteria
- `scripts/run_gsa.py` executes successfully for both Morris and Sobol methods.
- Generated plots (Tornado, Heatmap, Convergence) are saved to `data/gsa_v21/plots/` in PNG, SVG, and PDF formats.
- **Sensitivity Indices Export:** Raw sensitivity tables (S1, ST, mu_star) are exported to CSV for supplementary material.
- Parallel execution utilizes available CPU cores effectively.
- A "Sensitivity Summary" report is generated, ranking parameters by importance.

## Out of Scope
- Implementing the JAX/XLA accelerator (Architecture hook only).
- Training Surrogate models (Architecture hook only).
