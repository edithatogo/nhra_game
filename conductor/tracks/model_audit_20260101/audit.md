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

## Input & Parameter Sources
| Model | Input | Source ID | DOI/URL | Publication Date | Units | Scaling | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Core simulation engine | init_state (occupancy, within4, offload, discharge_delay) | AIHW2024; Duckett2021 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23; DOI:10.5694/mja2.51016 | 2024; 2021 | proportion; minutes; days | monthly | Baseline hospital performance inputs |
| Core simulation engine | economic_spine (nep_per_nwau, wpi_health_index) | IHACPA2024 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25 | 2024 | dollars per NWAU; index | annual | Pricing framework inputs |
| Core simulation engine | strategies vector (policy actions) | Schelling1960; Hermans2014 | https://www.hup.harvard.edu/books/9780674840317; https://journals.sagepub.com/doi/10.1177/1356389013516053 | 1960; 2014 | unitless probabilities | per time step | Strategy representation for negotiation choices |
| Core simulation engine | num_steps, prng_key | BaezHernandez2025 | https://bibliotecavirtual.unl.edu.ar/ | 2025 | steps; unitless seed | per simulation run | Simulation configuration parameters |
| JAX solver suite | payoff matrices (u_row, u_col) | Schelling1960; Ostrom2005 | https://www.hup.harvard.edu/books/9780674840317; https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 1960; 2005 | utility (unitless) | unitless | Game-theoretic payoff specification |
| JAX solver suite | lam, tol, max_iter, learning_rate | Hermans2014 | https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | unitless; iterations | iterative | Solver configuration parameters |
| JAX solver suite | micro_game_factory | Ostrom2005 | https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 2005 | unitless | unitless | Institutional diversity mapping for micro-games |
| Queuing equilibrium | total_base_demand, capacity | AIHW2024 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | admissions; beds | monthly | Demand/capacity inputs |
| Queuing equilibrium | discharge_delay | Duckett2021 | DOI:10.5694/mja2.51016 | 2021 | days | per patient | Bed block and discharge delay context |
| Queuing equilibrium | PatientUtilityParams (gp_out_of_pocket, wait_time, time_value, logit_sensitivity) | BaezHernandez2025 | https://bibliotecavirtual.unl.edu.ar/ | 2025 | dollars; minutes; dollars per hour; unitless | per decision | Utility parameterization requires further source refinement |
| Differentiable calibration | target_within4, base_params | AIHW2024 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | proportion; unitless | monthly | Calibration target metrics |
| Differentiable calibration | learning_rate, max_iter, prng_key | Hermans2014 | https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | unitless; iterations; seed | per optimization run | Calibration configuration |
| Stability metrics | intensities, pressures, efficiency_gap | Duckett2021; AIHW2024 | DOI:10.5694/mja2.51016; https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2021; 2024 | unitless; index | monthly | Stability inputs aligned with system pressure context |
| Stability metrics | x/y trajectories, modes list | Hermans2014 | https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | unitless | time series | Post-simulation resilience analysis |

## Reference Registry
| Reference ID | Citation | DOI/URL | Publication Date | Parameter Mapping | Units/Scale | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| AIHW2024 | Hospital resources 2022-23: Australian hospital statistics | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | init_state, capacity, target metrics | proportion, count | Official government statistics |
| Duckett2021 | The new National Health Reform Agreement: a major step backward? | DOI:10.5694/mja2.51016 | 2021 | init_state, discharge_delay, stability | index, days | MJA critique of NHRA |
| IHACPA2024 | Pricing Framework for Australian Public Hospital Services 2024-25 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25 | 2024 | economic_spine | dollars/NWAU | Official pricing determination |
| Schelling1960 | The Strategy of Conflict | https://www.hup.harvard.edu/books/9780674840317 | 1960 | strategies vector, payoff matrices | unitless | Foundational game theory text |
| Hermans2014 | Dynamic evaluation of public policy: a conceptual framework | https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | strategies vector, solver params, stability, calibration | unitless | Policy evaluation framework |
| Ostrom2005 | Understanding Institutional Diversity | https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 2005 | payoff matrices, micro_game_factory | unitless | IAD Framework reference |
| BaezHernandez2025 | Queuing and Utility parameters (Projected) | https://bibliotecavirtual.unl.edu.ar/ | 2025 | num_steps, queuing utility | various | Placeholder for forthcoming manuscript/thesis data |

## Reference Registry Conventions
- Registry file: publications/shared/references/library.yaml
- Validation command: python scripts/pub_tools/manage_refs.py publications/shared/references/library.yaml
- Required fields: id, title, author, year, doi/url
- Optional fields: journal or publisher, type, quality, recency, volume/issue/pages
- All entries must include DOI when available; otherwise a stable URL.

## Data Access & Licensing Constraints
- Identify licensing terms for each published source (open access, subscription, or restricted).
- Access restrictions (paywalls, institutional access, embargoes) must be documented per source.
- Reproducibility impact: note any constraints that limit replication or redistribution.
- Capture any usage limitations (e.g., non-commercial clauses) and mitigation steps.

## Assumption & Risk Register
### Assumption & Risk Register Conventions
- Required fields: assumption, rationale, risk, impact, mitigation
- Risk levels: low, medium, high
- Capture likelihood and evidence notes where available.

| Assumption | Rationale | Risk (low/med/high) | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| M/M/s Queuing Approximation | Closed-form approximation for ED wait times avoids DES overhead. | Medium | May underestimate wait times during rapid transient congestion spikes. | Calibrate discharge rates to empirical wait times; use steady-state validity. |
| Monthly Time Steps | System dynamics aggregated to monthly accounting cycles (1440 min/day used for capacity). | Low | Misses circadian/daily variance and shift-level bottlenecks. | Ensure parameters are monthly averages; sufficient for strategic policy analysis. |
| Linear Efficiency Drift/Decay | Empirical observation of gradual system degradation without intervention. | Medium | Long-term projections are sensitive to the decay rate parameter. | Sensitivity analysis on drift/decay parameters validation. |
| Logit Choice Patient Model | Standard utility maximization framework for GP vs ED choice. | Low | Assumes rational trade-off between wait time and out-of-pocket cost. | Calibrate sensitivity parameter to observed ED/GP presentations. |
| Stylized 2x2 Game Payoffs | Abstracted representation of Federal-State funding conflict (Prisoner's Dilemma). | High | Ignores complex multi-lateral negotiation and political side-payments. | Use primarily for mechanism design logic, not predictive forecasting. |
| Hardcoded Start Year 2025 | Default start year for simulation initialization. | Low | Verification scripts rely on specific dates. | Ensure override parameters are exposed in all entry points. |

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
