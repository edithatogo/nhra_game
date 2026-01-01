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
| High-Performance Sensitivity & Calibration (JAX) | product.md | | | |
| Strategic Scenario Analysis | product.md | | | |
| Interactive Web Dashboard (Streamlit) | product.md | | | |
| Automated Data Pipelines (AIHW/ABS) | product.md | | | |
| Extensive Form Game Explorer (GTE-style) | product.md | | | |
| Prescription & Policy Optimization (Gradients) | product.md | | | |
| Real-time Simulation Visualization | product.md | | | |
| Performance Modernization Reporting | product.md | | | |
| Automated Quality & Security Audits | product.md | | | |
| Scenario Library & Interactive Interpretation | product.md | | | |

## 2. Model Inputs & Parameters (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Players/Institutions (Cth, States, LHNs) | Inputs | | | |
| Agreement period & schedules | Inputs | | | |
| Funding streams (ABF, Block, PubHealth) | Inputs | | | |
| Pricing & classification (NEP/NEC, NWAU) | Inputs | | | |
| Policy parameters (Cap, Rec rules) | Inputs | | | |
| One-off adjustments / Schedule K | Inputs | | | |
| Demand drivers & shocks | Inputs | | | |
| Capacity & adjustment frictions | Inputs | | | |
| Cost structure (Fixed/Variable) | Inputs | | | |
| Cross-system substitution | Inputs | | | |
| Information structure (Lags, Error) | Inputs | | | |
| Integrity/compliance regime (Audit) | Inputs | | | |
| Political/reputational constraints | Inputs | | | |
| Mid-term review / scrutiny pressure | Inputs | | | |

## 3. Mechanisms & Rules Engine (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| ABF payment rule | Mechanism | | | |
| Block funding eligibility + payment | Mechanism | | | |
| Tri-stream choice | Mechanism | | | |
| Efficient growth accounting | Mechanism | | | |
| National growth cap + kinked payoffs | Mechanism | | | |
| Monthly payments + annual recon loop | Mechanism | | | |
| Dispute resolution & data matching | Mechanism | | | |
| Renegotiation / extension bargaining | Mechanism | | | |
| Audit / integrity "arms race" | Mechanism | | | |
| Transparency as public signals | Mechanism | | | |

## 4. Operational Dynamics (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Queues & congestion (ED, elective) | Operations | | | |
| Capacity with adjustment costs | Operations | | | |
| Substitution rules | Operations | | | |
| Quality as endogenous | Operations | | | |
| Threshold-triggered political loss | Operations | | | |

## 5. Outputs & Reporting (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Funding flows (by stream/state) | Outputs | | | |
| Activity & case-mix (NWAU, coding) | Outputs | | | |
| Efficiency & cost (Cost per NWAU) | Outputs | | | |
| Access & timeliness (Waiting lists) | Outputs | | | |
| Quality & safety (Readmissions) | Outputs | | | |
| Equity (Stratified access) | Outputs | | | |
| Strategic stability (Utilities) | Outputs | | | |

## 6. Validation & Reproducibility (nhra_all_in_spec.md)

| Feature | Category | Status | File/Line Reference | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-target calibration | Validation | | | |
| Out-of-sample validation | Validation | | | |
| Structural sensitivity | Validation | | | |
| Scenario library | Validation | | | |
| Modular architecture | Validation | | | |
| Determinism & traceability | Validation | | | |
| Explainability hooks | Validation | | | |
| Sanity/integrity tests | Validation | | | |
