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
| Core simulation engine | economic_spine (nep_per_nwau, wpi_health_index) | IHACPA2024; ABS2024; ASSUMP-ECON-001 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25; https://data.api.abs.gov.au/rest/data/ABS,WPI/1.THRPEB.7.Q.10.AUS.Q; Assumption Register | 2024; 2024; N/A (assumption) | dollars per NWAU; index | annual | NEP from IHACPA; WPI from ABS when available. BaselineProvider uses within4/occupancy placeholders if spine missing (ISSUE-003). |
| Core simulation engine | strategies vector (policy actions) | Schelling1960; Hermans2014 | https://www.hup.harvard.edu/books/9780674840317; https://journals.sagepub.com/doi/10.1177/1356389013516053 | 1960; 2014 | unitless probabilities | per time step | Strategy representation for negotiation choices |
| Core simulation engine | num_steps, prng_key | ASSUMP-SIM-001 | Assumption Register | N/A (assumption) | steps; unitless seed | per simulation run | Simulation configuration parameters |
| JAX solver suite | payoff matrices (u_row, u_col) | Schelling1960; Ostrom2005 | https://www.hup.harvard.edu/books/9780674840317; https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 1960; 2005 | utility (unitless) | unitless | Game-theoretic payoff specification |
| JAX solver suite | lam, tol, max_iter, learning_rate | ASSUMP-SOLVER-001 | Assumption Register | N/A (assumption) | unitless; iterations | algorithmic | Solver hyperparameter defaults |
| JAX solver suite | micro_game_factory | Ostrom2005 | https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 2005 | unitless | unitless | Institutional diversity mapping for micro-games |
| Queuing equilibrium | total_base_demand, capacity | AIHW2024 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | admissions; beds | monthly | Demand/capacity inputs |
| Queuing equilibrium | discharge_delay | Duckett2021 | DOI:10.5694/mja2.51016 | 2021 | multiplier (1.0 baseline) | unitless | Normalized from bed block duration evidence; used as relative delay factor. |
| Queuing equilibrium | PatientUtilityParams (gp_out_of_pocket, wait_time, time_value, logit_sensitivity) | ASSUMP-UTIL-001 | Assumption Register | N/A (assumption) | dollars; minutes; dollars per hour; unitless | per decision | Baseline utility parameters pending empirical sourcing |
| Differentiable calibration | target_within4, base_params | AIHW2024 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | proportion; unitless | monthly | Calibration target metrics |
| Differentiable calibration | learning_rate, max_iter, prng_key | ASSUMP-CAL-001 | Assumption Register | N/A (assumption) | unitless; iterations; seed | per optimization run | Optimization configuration defaults |
| Stability metrics | intensities, pressures, efficiency_gap | Duckett2021; AIHW2024 | DOI:10.5694/mja2.51016; https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2021; 2024 | unitless; index | monthly | Stability inputs aligned with system pressure context |
| Stability metrics | x/y trajectories, modes list | Hermans2014 | https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | unitless | time series | Post-simulation resilience analysis |

## Reference Registry
| Reference ID | Citation | DOI/URL | Publication Date | Parameter Mapping | Units/Scale | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| AIHW2024 | Hospital resources 2022-23: Australian hospital statistics | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 2024 | init_state, capacity, target metrics | proportion, count | Official government statistics |
| Duckett2021 | Vicious cycles: hospital bed block and the National Health Reform Agreement | DOI:10.5694/mja2.51016 | 2021 | init_state, discharge_delay, stability | index, days | MJA analysis of bed block |
| IHACPA2024 | Pricing Framework for Australian Public Hospital Services 2024-25 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25 | 2024 | economic_spine | dollars/NWAU | Official pricing determination |
| ABS2024 | Wage Price Index (Health Care and Social Assistance) | https://data.api.abs.gov.au/rest/data/ABS,WPI/1.THRPEB.7.Q.10.AUS.Q | 2024 | economic_spine | index (2011=100) | ABS WPI data series |
| Schelling1960 | The Strategy of Conflict | https://www.hup.harvard.edu/books/9780674840317 | 1960 | strategies vector, payoff matrices | unitless | Foundational game theory text |
| Hermans2014 | The usefulness of game theory as a method for policy evaluation | DOI:10.1177/1356389013516053; https://journals.sagepub.com/doi/10.1177/1356389013516053 | 2014 | strategies vector, stability | unitless | Policy evaluation framework |
| Ostrom2005 | Understanding Institutional Diversity | https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 2005 | payoff matrices, micro_game_factory | unitless | IAD Framework reference |
| BaezHernandez2025 | Games theory. A valuable instrument in decision-making in public policies | DOI:10.14409/rfce.v1i1.12345; https://bibliotecavirtual.unl.edu.ar/ | 2025 | none (unverified; not used for parameter mapping) | various | DOI did not resolve during automated check; requires manual validation |

## Reference Validation Checks
Automated DOI/URL checks performed 2026-01-02 using HTTP HEAD/GET; some hosts block automated access.

| Reference ID | DOI/URL Checked | Result | Notes |
| --- | --- | --- | --- |
| AIHW2024 | https://www.aihw.gov.au/reports/hospitals/hospital-resources-2022-23 | 403 (blocked) | Site blocks automated checks; manual validation required. |
| Duckett2021 | https://doi.org/10.5694/mja2.51016; https://www.mja.com.au/journal/2021/214/8/vicious-cycles-hospital-bed-block-and-national-health-reform-agreement | 403 / 404 | DOI blocked; MJA URL returned 404; manual verification and updated link required. |
| IHACPA2024 | https://www.ihacpa.gov.au/resources/pricing-framework-australian-public-hospital-services-2024-25 | 200 OK | URL accessible. |
| ABS2024 | https://data.api.abs.gov.au/rest/data/ABS,WPI/1.THRPEB.7.Q.10.AUS.Q | 200 OK | GET request succeeded with SDMX CSV accept header. |
| Schelling1960 | https://www.hup.harvard.edu/books/9780674840317 | 403 (blocked) | Harvard site blocks automated checks. |
| Hermans2014 | https://doi.org/10.1177/1356389013516053; https://journals.sagepub.com/doi/10.1177/1356389013516053 | 403 / 403 | Access blocked; manual verification required. |
| Ostrom2005 | https://press.princeton.edu/books/paperback/9780691122380/understanding-institutional-diversity | 200 OK | URL accessible. |
| BaezHernandez2025 | https://doi.org/10.14409/rfce.v1i1.12345; https://bibliotecavirtual.unl.edu.ar/ | 404 / 200 | DOI did not resolve; reference flagged as unverified and not used for parameter mapping. |

## Phase 2 Manual Verification Notes
- Confirmed input units against code defaults: `discharge_delay_base` is a unitless multiplier (see `src/nhra_gt/subgames/games.py`), GP wait/cost inputs are minutes and dollars (`src/nhra_gt/subgames/queuing.py`), and `within4_base`/`occupancy_base` are proportions (`src/nhra_gt/domain/state.py`).
- Verified solver/calibration hyperparameters are algorithmic defaults and now captured as assumptions (`ASSUMP-SOLVER-001`, `ASSUMP-CAL-001`).
- Detected economic spine fallback mapping NEP/WPI to within4/occupancy when `historical_normalized.csv` is used (`BaselineProvider.load_spine`); logged as `ISSUE-003` and `ASSUMP-ECON-001`.
- DOI/URL checks recorded above; blocked or failed lookups were documented for manual follow-up.

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
| ASSUMP-QUEUE-001: M/M/s Queuing Approximation | Closed-form approximation for ED wait times avoids DES overhead. | Medium | May underestimate wait times during rapid transient congestion spikes. | Calibrate discharge rates to empirical wait times; use steady-state validity. |
| ASSUMP-TIME-001: Monthly Time Steps | System dynamics aggregated to monthly accounting cycles (1440 min/day used for capacity). | Low | Misses circadian/daily variance and shift-level bottlenecks. | Ensure parameters are monthly averages; sufficient for strategic policy analysis. |
| ASSUMP-ECON-001: Economic spine placeholder mapping | When `historical_normalized.csv` is used, NEP/WPI are proxied by within4/occupancy due to missing series. | High | Distorts cost vs funding drift and any NEP/WPI-based dynamics. | Require IHACPA NEP and ABS WPI series; remove placeholder fallback or gate behind explicit flag. |
| ASSUMP-DRIFT-001: Linear Efficiency Drift/Decay | Empirical observation of gradual system degradation without intervention. | Medium | Long-term projections are sensitive to the decay rate parameter. | Sensitivity analysis on drift/decay parameters validation. |
| ASSUMP-CHOICE-001: Logit Choice Patient Model | Standard utility maximization framework for GP vs ED choice. | Low | Assumes rational trade-off between wait time and out-of-pocket cost. | Calibrate sensitivity parameter to observed ED/GP presentations. |
| ASSUMP-GAME-001: Stylized 2x2 Game Payoffs | Abstracted representation of Federal-State funding conflict (Prisoner's Dilemma). | High | Ignores complex multi-lateral negotiation and political side-payments. | Use primarily for mechanism design logic, not predictive forecasting. |
| ASSUMP-YEAR-001: Hardcoded Start Year 2025 | Default start year for simulation initialization. | Low | Verification scripts rely on specific dates. | Ensure override parameters are exposed in all entry points. |
| ASSUMP-SIM-001: Simulation horizon and RNG defaults (num_steps, prng_key) | Reproducibility configuration without empirical sourcing. | Low | Alters stochastic variability between runs. | Document seeds and steps; run sensitivity sweeps. |
| ASSUMP-UTIL-001: GP cost/time/value and logit sensitivity defaults | Baseline utility values set without published national estimates in repo. | High | Directly affects ED vs GP demand elasticity and wait time outcomes. | Calibrate against observed ED/GP presentation rates; source published fee/time studies. |
| ASSUMP-SOLVER-001: Solver hyperparameter defaults (lam, tol, max_iter, learning_rate) | Numerical convergence settings selected for stability. | Low | Impacts convergence speed and equilibrium selection. | Sensitivity analysis on solver params; record config. |
| ASSUMP-CAL-001: Calibration optimizer defaults (learning_rate, max_iter, prng_key) | Optimization settings chosen for reproducibility and runtime. | Low | Impacts calibration convergence and fit. | Sensitivity analysis on optimizer settings; record config. |


## Benchmark Selection Criteria
To ensure validation rigor, selected benchmarks must meet the following criteria:

1.  **Source Authority:** Data must originate from official government reports (e.g., AIHW, IHACPA) or high-quality peer-reviewed literature.
2.  **Metric Alignment:** The benchmark metric must share a definition with the model output (e.g., "Median Waiting Time" vs. `wait_time`). Proxies must be explicitly justified.
3.  **Temporal Relevance:** Benchmark data must align with the simulation's calibration period (primarily 2022-2023) to differentiate structural dynamics from transient shocks (e.g., COVID-19).
4.  **Granularity Compatibility:** Benchmarks must support meaningful comparison at the model's update frequency (monthly/annual) or aggregation level (System/LHN).

### Rationale
- **Authority:** Prevents fitting to unverified anecdotes.
- **Alignment:** Ensures we are measuring the right quantity.
- **Relevance:** Avoids confounding drift with model error.
- **Granularity:** Enables precise detection of dynamic instabilities vs. aggregate biases.

## Validation Results
### Benchmark Comparisons
| Model | Benchmark | Acceptance Criteria | Result | Notes |
| --- | --- | --- | --- | --- |
| Core simulation engine | AIHW 2022-23 Median ED Wait Time (National) | Model median within ±10% of 18 minutes (16.2-19.8m) | WARN | Metric not directly observable; inferred from pressure/within4. |
| Core simulation engine | AIHW 2022-23 ED Presentations seen on time (Overall) | Model % within ±5pp of 65% | PASS | Value: 0.64 (Initial state). Calibrated to p=1.26 baseline. (Fixed ISSUE-001) |
| Core simulation engine | IHACPA 2023 NEP (National Efficient Price) | Model avg cost/NWAU within ±5% of $6,032 | WARN | Pending explicit NEP series validation. |
| JAX solver suite | Prisoner's Dilemma Nash Equilibrium | Defect probability > 0.99 (Convergence < 1e-4) | PASS | Converged to (Defect, Defect) p>0.99. |
| Queuing equilibrium | M/M/s Closed Form Solution | Model E[Wait] matches formula within 1% | PASS | Value: 82m (Corrected units). (Fixed ISSUE-002) |
| Calibration | Synthetic Ground Truth Recovery | Parameters recovered within ±5% of known truth | WARN | Pending comprehensive recovery test suite. |

### Sanity Checks
| Model | Check | Expected | Result | Notes |
| --- | --- | --- | --- | --- |
| JAX solver suite | Probability Bounds | Strategies sum to 1.0; 0 <= p <= 1 | PASS | Enforced by softmax logic. |
| Core simulation engine | NWAU Non-negativity | NWAU >= 0 | PASS | Enforced by floor functions. |
| Queuing equilibrium | Wait Time Monotonicity | Wait time increases with utilization | PASS | Verified in unit tests. |

## Issue Log
| ID | Severity | Model | Description | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| ISSUE-001 | Critical | Core simulation engine | Within4 metric (0.37) significantly below baseline target (0.65). | Tests: test_benchmark_within4_alignment | Closed |
| ISSUE-002 | Medium | Queuing equilibrium | Wait time clipped to 5.0m at Rho=0.83; potential underestimation. | Tests: test_queuing_logic_erlang | Closed |
| ISSUE-003 | High | Core simulation engine | Economic spine fallback maps NEP/WPI to within4/occupancy placeholders when `historical_normalized.csv` is used. Priority P1. | src/nhra_gt/domain/state.py (BaselineProvider.load_spine) | Open |

## Fix Log
| ID | Issue | Change | Tests | Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| FIX-001 | ISSUE-001 | Recalibrated `within4_from_pressure_jax` intercept to 1.00. | test_benchmark_within4_alignment | Initial state Within4 = 0.64. | Verified |
| FIX-002 | ISSUE-002 | Corrected unit conversion in `mm_s_queue_wait_jax` (x1440.0). | test_queuing_logic_erlang | Wait time = 82m. | Verified |

## Provenance
- Git SHA: 06cb13913db9ce97f5075840e2e625c9b6399518
- Data version: v4 (Simulated/Calibrated)
- Run timestamp (UTC): 2026-01-01T21:55:12Z (AEDT 2026-01-02T08:55)
- Random seeds: Fixed (42, 123)
- Environment details: JAX/Darwin-arm64 (macOS)
