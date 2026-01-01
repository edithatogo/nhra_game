# Model Audit Report

## Audit Artifacts
- Model inventory table (Model Inventory section)
- Reference registry (Reference Registry section)
- Assumption & risk register (Assumption & Risk Register section)
- Validation results tables (Benchmark Comparisons and Sanity Checks)
- Issue log (Issue Log section)
- Fix log (Fix Log section)

## Audit Methodology
1. Inventory all computational models and their inputs/outputs.
2. Map each input and assumption to a published source or document justified assumptions.
3. Validate outputs against benchmarks when available and apply sanity checks otherwise.
4. Log issues, repair them, and record before/after evidence.
5. Capture provenance for reproducibility.

## Model Inventory
| Model | Location | Purpose | Inputs | Outputs | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Core simulation engine | src/nhra_gt/engine.py | Orchestrate system dynamics and scenario runs | base_params, initial_state, scenario config | trajectories, summary metrics | domain/*, subgames/*, solvers_jax, agents | Primary Python engine |
| JAX solver suite | src/nhra_gt/solvers_jax.py | Compute equilibria and solver utilities | payoff matrices, constraints | equilibrium strategies, diagnostics | jax, numpy | Vectorized solver core |
| Queuing equilibrium | src/nhra_gt/subgames/queuing.py | M/M/s queue solver for ED wait/demand | arrival rate, service rate, capacity, utility params | equilibrium demand, wait times | engine mm_s_queue_wait, jax (optional) | Legacy + JAX paths |
| Differentiable calibration | src/nhra_gt/calibration/differentiable.py | Calibrate parameters to target metrics | target metrics, base_params, init state | optimized params, loss | jax | Optimization loop |
| Stability metrics | src/nhra_gt/domain/stability.py | Hysteresis area and recovery metrics | trajectory series | hysteresis area, recovery stats | numpy | Post-simulation metrics |

## Reference Registry
| Reference ID | Citation | DOI/URL | Publication Date | Parameter Mapping | Units/Scale | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Assumption & Risk Register
| Assumption | Rationale | Risk (low/med/high) | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

## Validation Results
### Benchmark Comparisons
| Model | Benchmark | Acceptance Criteria | Result | Notes |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

### Sanity Checks
| Model | Check | Expected | Result | Notes |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

## Issue Log
| ID | Severity | Model | Description | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Fix Log
| ID | Issue | Change | Tests | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Provenance
- Git SHA: TBD
- Data version: TBD
- Run timestamp (UTC): TBD
- Random seeds: TBD
- Environment details: TBD
