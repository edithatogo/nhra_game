# Evidence-Linked Feature Matrix

This matrix tracks the maturity, verification, and empirical grounding of the NHRA Game Theory model's core features.

## 1. Modeling & Simulation (Core Mechanism)

| Feature | Description | Maturity | Verification | Evidence Source |
|---|---|---|---|---|
| **Stochastic Simulation** | Monthly time-step MC rollouts | **STABLE** | `tests/test_engine_smoke.py` | Model Assumption Log (05) |
| **Multi-Game Equilibria** | Nash solvers for BARG, DEF, etc. | **STABLE** | `tests/test_subgames_nash.py` | Game Theory spec (03) |
| **Queuing Dynamics** | M/M/s wait time approximation | **BETA** | `tests/test_engine_smoke.py` | Operations Research Standard |
| **Cognitive DT Engine** | Agent-based decision layer | **ALPHA** | `tests/test_engine_smoke.py` | Strategic Map (02) |

## 2. Analysis & Diagnostics

| Feature | Description | Maturity | Verification | Evidence Source |
|---|---|---|---|---|
| **Sobol GSA** | Global variance decomposition | **STABLE** | `tests/test_sensitivity.py` | SALib Standard |
| **Morris Screening** | Parameter influence ranking | **STABLE** | `tests/test_sensitivity.py` | SALib Standard |
| **Optuna Calibration** | TPE-based parameter matching | **STABLE** | `tests/test_calibration_objective.py` | AIHW Historical Data |
| **Theil Decomposition** | Error source identification | **STABLE** | `tests/test_theil_decomposition.py` | Econometric Standard |

## 3. Operational Integrity

| Feature | Description | Maturity | Verification | Evidence Source |
|---|---|---|---|---|
| **Pydantic Validation** | Type-safe parameter constraints | **STABLE** | `tests/test_pydantic_refactor.py` | Python Best Practices |
| **Visual Regression** | Figure parity via `pytest-mpl` | **STABLE** | `tests/visualization/` | Publication Specs |
| **Security Audits** | Automated `bandit` scanning | **STABLE** | `pre-commit` | Security Standards |
| **Living Documentation** | Automated diagram drift detection | **BETA** | `scripts/verify_docs.py` | Internal Standard |

## 4. Policy & Domain Coverage

| Feature | Description | Maturity | Verification | Evidence Source |
|---|---|---|---|---|
| **45% Cth Share** | Nominal funding target logic | **STABLE** | `context/grounding.ok` | [NHRA Agreement](https://www.publichospitalfunding.gov.au/) |
| **NEP Indexation** | Realism vs Efficiency framing | **STABLE** | `scripts/data/ingest_economic_spine.py` | [IHACPA NEP](https://www.ihacpa.gov.au/) |
| **6.5% Growth Cap** | Hard/Soft cap implementation | **BETA** | `tests/test_mechanism_validation.py` | [NHRA Agreement](https://www.publichospitalfunding.gov.au/) |
| **Rurality Weight** | Peer group cost adjustments | **STABLE** | `context/04_parameter_registry.csv` | [AIHW Hospital Resources](https://www.aihw.gov.au/) |
