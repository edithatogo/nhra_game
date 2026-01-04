# Feature Audit Matrix 2026

This document tracks the implementation status of all planned features for the `nhra_gt` project, as defined in `conductor/product.md` and `context/nhra_all_in_spec.md`.

## Status Key

- **Implemented**: Full functionality exists in the codebase.
- **Stubbed**: Placeholder exists (e.g., function with `pass` or `NotImplementedError`).
- **Missing**: No trace of the feature found in the codebase.
- **Undocumented**: Feature found in code but not in any specification.

---

## 1. High-Level Product Features (product.md)

| Feature | Source | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| High-Performance Sensitivity & Calibration (JAX) | product.md | Implemented | `src/nhra_gt/engine.py` | Full JAX/XLA functional core implemented. |
| Strategic Scenario Analysis | product.md | Implemented | `scripts/dashboard.py` | Interactive counterfactuals via sidebar. |
| Interactive Web Dashboard (Streamlit) | product.md | Implemented | `streamlit_app.py` | Deployed and functional. |
| Automated Data Pipelines (AIHW/ABS) | product.md | Implemented | `src/nhra_gt/domain/ihacpa_api.py` | Local XLSB parsing and AIHW API integration. |
| Extensive Form Game Explorer (GTE-style) | product.md | Partial | `src/nhra_gt/visualization/game_trees.py` | Game trees exist but limited interactivity compared to GTE. |
| Prescription & Policy Optimization (Gradients) | product.md | Implemented | `src/nhra_gt/optimization_jax.py` | JAX gradients used for policy search. |
| Real-time Simulation Visualization | product.md | Implemented | `scripts/dashboard.py` | Plotly/D3 integration for live feedback. |
| Performance Modernization Reporting | product.md | Implemented | `scripts/benchmark_modernization.py` | Automated benchmarking script exists. |
| Automated Quality & Security Audits | product.md | Implemented | `pyproject.toml` | `mutmut`, `bandit`, `safety` integrated into CI. |
| Scenario Library & Interactive Interpretation | product.md | Implemented | `scenario_library/` | YAML-based scenario configs. |

## 2. Model Inputs & Parameters (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Players/Institutions (Cth, States, LHNs) | Inputs | Implemented | `src/nhra_gt/domain/state.py` | Full hierarchical player model (StateJax). |
| Agreement period & schedules | Inputs | Implemented | `src/nhra_gt/engine.py` | `agreement_clock` and period logic. |
| Funding streams (ABF, Block, PubHealth) | Inputs | Partial | `src/nhra_gt/rules.py` | ABF and Block implemented; PubHealth missing. |
| Pricing & classification (NEP/NEC, NWAU) | Inputs | Implemented | `src/nhra_gt/domain/ihacpa_api.py` | Automated NEP series extraction. |
| Policy parameters (Cap, Rec rules) | Inputs | Implemented | `src/nhra_gt/rules.py` | 6.5% cap and redistribution rules. |
| One-off adjustments / Schedule K | Inputs | Stubbed | `data/raw/calibration_targets.csv` | Schedule K values present but simplified in engine. |
| Demand drivers & shocks | Inputs | Implemented | `src/nhra_gt/engine.py` | Population/morbidity drivers via `noise_sd`. |
| Capacity & adjustment frictions | Inputs | Implemented | `src/nhra_gt/engine.py` | `mm_s_queue_wait_jax` and friction logic. |
| Cost structure (Fixed/Variable) | Inputs | Implemented | `src/nhra_gt/engine.py` | `efficiency_gap` mapping. |
| Cross-system substitution | Inputs | Implemented | `src/nhra_gt/subgames/queuing.py` | Substitution between ED and primary care. |
| Information structure (Lags, Error) | Inputs | Implemented | `src/nhra_gt/domain/state.py` | `lag_buffer_nwau` implemented. |
| Integrity/compliance regime (Audit) | Inputs | Partial | `src/nhra_gt/audit/fingerprint.py` | Basic suspicion tracking; logic is simplified. |
| Political/reputational constraints | Inputs | Implemented | `src/nhra_gt/agents/jax.py` | `political_salience` affects payoffs. |
| Mid-term review / scrutiny pressure | Inputs | Missing | | No explicit mid-term review signal logic found. |

## 3. Mechanisms & Rules Engine (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| ABF payment rule | Mechanism | Implemented | `src/nhra_gt/engine.py` | `NEP * NWAU` logic. |
| Block funding eligibility + payment | Mechanism | Implemented | `src/nhra_gt/rules.py` | `NWAUEligibilityRule` implemented. |
| Tri-stream choice | Mechanism | Missing | | PubHealth stream not yet selectable by agents. |
| Efficient growth accounting | Mechanism | Implemented | `src/nhra_gt/rules.py` | `GrowthCapRule` applies full/reduced rates. |
| National growth cap + kinked payoffs | Mechanism | Implemented | `src/nhra_gt/rules.py` | Piecewise funding around 6.5% cap. |
| Monthly payments + annual recon loop | Mechanism | Implemented | `src/nhra_gt/engine.py` | Monthly step simulation logic. |
| Dispute resolution & data matching | Mechanism | Missing | | Not explicitly modeled in the engine. |
| Renegotiation / extension bargaining | Mechanism | Implemented | `src/nhra_gt/subgames/games_jax.py` | `renegotiation_game_jax` implemented. |
| Audit / integrity "arms race" | Mechanism | Stubbed | `src/nhra_gt/audit/fingerprint.py` | Suspicion tracking present but arms race feedback is weak. |
| Transparency as public signals | Mechanism | Implemented | `src/nhra_gt/engine.py` | Signal lags and reported vs actual metrics. |

## 4. Operational Dynamics (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Queues & congestion (ED, elective) | Operations | Implemented | `src/nhra_gt/subgames/queuing.py` | M/M/s queuing solver. |
| Capacity with adjustment costs | Operations | Implemented | `src/nhra_gt/engine.py` | `adjustment_cost_beta` and friction logic. |
| Substitution rules | Operations | Implemented | `src/nhra_gt/engine.py` | ED vs Primary care substitution. |
| Quality as endogenous | Operations | Implemented | `src/nhra_gt/engine.py` | Pressure -> `within4` performance mapping. |
| Threshold-triggered political loss | Operations | Implemented | `src/nhra_gt/agents/jax.py` | Step penalties for KPI breaches. |

## 5. Outputs & Reporting (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Funding flows (by stream/state) | Outputs | Implemented | `src/nhra_gt/engine.py` | `total_revenue`, `total_block_revenue`. |
| Activity & case-mix (NWAU, coding) | Outputs | Implemented | `src/nhra_gt/engine.py` | `reported_nwau`, `coding_intensity`. |
| Efficiency & cost (Cost per NWAU) | Outputs | Implemented | `src/nhra_gt/engine.py` | `efficiency_gap` reporting. |
| Access & timeliness (Waiting lists) | Outputs | Implemented | `src/nhra_gt/engine.py` | `within4`, `pidx` (pressure). |
| Quality & safety (Readmissions) | Outputs | Implemented | `src/nhra_gt/domain/state.py` | `HighReliabilityOrg` (HRO) metrics. |
| Equity (Stratified access) | Outputs | Missing | | No explicit regional/equity outcome stratification. |
| Strategic stability (Utilities) | Outputs | Implemented | `src/nhra_gt/solvers_jax.py` | Convergence residuals and stability metrics. |

## 6. Validation & Reproducibility (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-target calibration | Validation | Implemented | `src/nhra_gt/calibration/differentiable.py` | Fits to Spend, NWAU, and Wait Times. |
| Out-of-sample validation | Validation | Implemented | `scripts/validation/validate_mechanism.py` | Structural validation suite. |
| Structural sensitivity | Validation | Implemented | `src/nhra_gt/sensitivity.py` | Sobol/Morris analysis. |
| Scenario library | Validation | Implemented | `scenario_library/` | YAML scenario catalogue. |
| Modular architecture | Validation | Implemented | `src/nhra_gt/rules.py` | Pluggable rule objects. |
| Determinism & traceability | Validation | Implemented | `src/nhra_gt/engine.py` | Fixed PRNG keys and config logging. |
| Explainability hooks | Validation | Implemented | `src/nhra_gt/agents/jax.py` | Utility decomposition logging. |
| Sanity/integrity tests | Validation | Implemented | `tests/test_jax_parity.py` | Mass-balance and invariant checks. |

---

## 7. Discovered "Hidden" Features (Undocumented)

| Feature | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- |
| JAX-native QRE Solver | Implemented | `src/nhra_gt/solvers_jax.py` | Quantal Response Equilibrium solver for bounded rationality. |
| Asymmetric Capacity Friction | Implemented | `src/nhra_gt/engine.py` | Separate lags for expansion vs contraction. |
| Persistent Disk Caching (XLA) | Implemented | `src/nhra_gt/engine.py` | Automatic caching of compiled kernels in `~/.cache/jax_cache`. |
| Constitutional Game Layer | Implemented | `src/nhra_gt/hierarchical_jax.py` | Cth -> State -> LHN hierarchical coordination. |
