# Model Candidate Scan

## Model Definition
Any computational component that transforms inputs into outputs for simulation, prediction, optimization, calibration, or decision analysis.

## Candidate Locations (Initial Scan)
This initial scan lists candidate model components and will be refined during the full inventory.

### Core engine and solvers
- src/nhra_gt/engine.py (primary simulation engine)
- src/nhra_gt/engine_jax.py (JAX engine)
- src/nhra_gt/legacy_engine.py (legacy engine)
- intermediate_engine.py (intermediate engine wrapper)
- src/nhra_gt/solvers_jax.py (JAX solvers)
- src/nhra_gt/hierarchical_jax.py (hierarchical solver)
- src/nhra_gt/optimization_jax.py (optimization routines)

### Calibration and sensitivity
- src/nhra_gt/calibration/ (calibration models)
- src/nhra_gt/sensitivity.py (sensitivity analysis)
- scripts/calibrate_differentiable.py (calibration workflow)
- scripts/calibrate_hmc.py (HMC calibration workflow)
- scripts/optimize_calibration.py (optimization workflow)

### Game structure and rules
- src/nhra_gt/subgames/ (subgame definitions and payoffs)
- src/nhra_gt/domain/ (state/transition models)
- src/nhra_gt/rules.py (rules engine)
- src/nhra_gt/agent_logic.py (agent decision logic)

### README-informed components
- src/nhra_gt/agents/base.py (LLMAgent/HeuristicAgent frameworks)
- src/nhra_gt/agents/jax.py (JAX heuristic agents)
- src/nhra_gt/subgames/queuing.py (M/M/s queuing equilibrium)
- src/nhra_gt/domain/stability.py (hysteresis and recovery metrics)
- src/nhra_gt/domain/state.py (state and fiscal variables)

### Pipelines and scenario execution
- scripts/run_baseline.py (baseline simulation run)
- scripts/run_gsa.py (global sensitivity analysis)
- scripts/run_p2_experiments.py (scenario experiments)
- scripts/validation/ (validation pipelines)
