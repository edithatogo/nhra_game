# Specification: NHRA Engine Modernization (JAX/XLA & Polars)

## 1. Overview
Fundamental re-architecture of the NHRA simulation engine to support JAX/XLA functional core, Polars data handling, and PyGambit-based Game Tree Exploration for 2-player, Multi-player, and Hybrid/Hierarchical games.

## 2. Functional Requirements

### FR1: JAX-Accelerated Functional Core
- **Temporal Scan & Vectorization:** Use `jax.lax.scan` for timelines and `jax.vmap` for thousands of parallel MC samples/Jurisdictions.
- **Pytree State:** Unified state management for transformation and autodiff.

### FR2: Differentiable & Prescriptive Solvers
- **Solver Suite:** QRE (Logit), Regret Minimization, and Discrete (Custom JVP) solvers.
- **Prescription:** Integrated `jaxopt` for optimal policy search.

### FR3: Polars Data Infrastructure
- **Modern Stack:** Polars-based rewrite of AIHW/IHACPA ingestion and schema validation.

### FR4: PyGambit & Game Tree Explorer (Static + Dynamic)
- **Comprehensive Trees:** Generate **Static (SVG)** and **Dynamic (Interactive GTE)** trees for all games.
- **Hybrid Support:** Explicitly support **Hybrid/Hierarchical** game trees representing nested Commonwealth -> State -> LHN negotiations.
- **Evidence Linkage:** Bind tree nodes to `Bibliography` metadata for grounded UI exploration.

### FR5: Bayesian Calibration
- **NumPyro HMC:** Gradient-based calibration for 100+ parameters.

## 3. Acceptance Criteria
- Full 1000-sample MC simulation (6 years) executes in < 2.0 seconds.
- Dashboard provides interactive trees for all 9 games, including **Hybrid** Extensive Form views.
- JAX core matches legacy NumPy v26 logic within 6 decimal places (Logic Parity).
