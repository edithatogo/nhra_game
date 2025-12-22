# Technology Stack

## Language & Runtime
- **Primary Language:** Python 3.10+
- **Containerization:** Docker (Mandatory for MJA reproducibility and deployment)

## Core Modeling & Simulation
- **Numerical Computing:** NumPy, Pandas, SciPy
- **Network Analysis:** NetworkX
- **Optimization & Calibration:** Optuna (Tree-structured Parzen Estimator)
- **Sensitivity Analysis:** SALib (For Sobol and Morris global sensitivity methods)

## Workflow & Infrastructure
- **Pipeline Management:** Snakemake (Ensures reproducible and parallelizable HPC execution)
- **Deployment:** GitHub Actions (CI/CD)

## Visualization & Interaction
- **War Gaming Dashboard:** Streamlit
- **Static & Interactive Plots:** Plotly, Matplotlib
- **Legacy Components:** D3.js (Support for existing interactive network visualizations)

## Development & Quality Assurance
- **Build System:** Hatch
- **Linting & Formatting:** Ruff
- **Static Type Checking:** Mypy
- **Testing:** Pytest, Hypothesis (Property-based testing)
- **Automation:** Pre-commit, Tox
- **Documentation:** MkDocs (Material theme)
