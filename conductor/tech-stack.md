# Technology Stack

## Language & Runtime
- **Primary Language:** Python 3.10+
- **Containerization:** Docker (Mandatory for MJA reproducibility and deployment)

## Core Modeling & Simulation
- **Numerical Computing:** NumPy, Pandas, SciPy
- **Data Validation:** Pydantic V2 (Models), Pandera (DataFrame Schemas)
- **Network Analysis:** NetworkX
- **Optimization & Calibration:** Optuna (Tree-structured Parzen Estimator)
- **Sensitivity Analysis:** SALib (For Sobol and Morris global sensitivity methods)

## Development & Quality Assurance
- **Build System:** Hatch
- **Environment Orchestration:** Nox (Replacing Tox)
- **Linting & Formatting:** Ruff, Bandit
- **Static Analysis:** Pyright (Strict), Mypy, Deptry (Dependency Audit)
- **Advanced Testing:** Hypothesis (PBT), Atheris (Fuzzing), Locust (Load), Mutmut (Mutation Testing), pytest-mpl (Visual Regression)
- **Runtime Verification:** Icontract (Design-by-Contract), Beartype, Typeguard
- **Documentation:** MkDocs, Mkdocstrings
