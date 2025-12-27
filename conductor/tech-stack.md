# Technology Stack

## Language & Runtime
- **Primary Language:** Python 3.10+
- **Containerization:** Docker (Mandatory for MJA reproducibility and deployment)

## Core Modeling & Simulation
- **Numerical Computing:** JAX/XLA (Functional Core), Polars (Data Spine), NumPy, SciPy
- **Data Validation:** Pydantic V2 (Models), Pandera (DataFrame Schemas)
- **Network Analysis:** NetworkX
- **Optimization & Calibration:** Optuna (Tree-structured Parzen Estimator)
- **Computational Acceleration:** JAX/XLA (Vectorized Nash solving and differentiable simulation)
- **Bayesian Inference:** NumPyro (Hamiltonian Monte Carlo calibration)
- **Sensitivity Analysis:** SALib (For Sobol and Morris global sensitivity methods)
- **Strategic Game Analysis:** PyGambit (C++ Nash Oracle and tree construction)

## Development & Quality Assurance
- **Build System:** Hatch
- **Environment Orchestration:** Nox (Replacing Tox)
- **Linting & Formatting:** Ruff, Bandit
- **Static Analysis:** Pyright (Strict), Mypy, Deptry (Dependency Audit)
- **Profiling & Benchmarking:** Pyinstrument, Scalene
- **Advanced Testing:** Hypothesis (PBT), Atheris (Fuzzing), Locust (Load), Mutmut (Mutation Testing)
- Runtime Verification: Icontract (Design-by-Contract), Beartype, Typeguard
- Documentation: MkDocs, Mkdocstrings

## Publication & Meta-Research
- Citation Management: Custom YAML-to-BibTeX/RIS pipeline (`manage_refs.py`)
- Quality Metrics: Textstat (Readability/Grade Level optimization)
