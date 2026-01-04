# Testing Procedures & Infrastructure

This project uses a multi-layered testing strategy to ensure the fidelity, performance, and robustness of the NHRA game-theory models.

## 1. Test Layers

### Unit Tests

- **Location:** `tests/`
- **Tool:** `pytest`
- **Scope:** Individual functions and classes in `src/`.
- **Requirement:** Every core module must have a corresponding test file.

### Property-Based Testing (PBT)

- **Location:** `tests/properties/`
- **Tools:** `hypothesis`, `hypothesis-auto`
- **Scope:** Verifying invariants across a wide range of generated inputs.
- **Example:** Ensuring bargaining probabilities always sum to 1.0.

### Fuzz Testing

- **Location:** `tests/fuzz/`
- **Tool:** `atheris`
- **Scope:** Stress-testing core solver logic with malicious/edge-case binary data.
- **Run:** `nox -s fuzz`

### Load Testing

- **Location:** `tests/load/`
- **Tool:** `locust`
- **Scope:** Benchmarking the Streamlit dashboard and (hypothetical) API endpoints.
- **Run:** `nox -s load`

### End-to-End (E2E) Pipeline Tests

- **Location:** `tests/e2e/`
- **Tool:** `snakemake`
- **Scope:** Verifying the full execution of the simulation pipeline from raw data to validated results.
- **Run:** `pytest tests/e2e/test_pipeline.py`

## 2. Coverage Requirements

- **Threshold:** Individual file coverage must be **> 95%**.
- **Enforcement:** Enforced in `pyproject.toml` and verified in CI.
- **Run:** `nox -s coverage`

## 3. Runtime Verification

- **Tools:** `beartype`, `typeguard`, `icontract`
- **Scope:** Enforcing type safety and logical invariants at runtime during development and testing.
- **Run:** `nox -s type_runtime`

## 4. Continuous Integration

- All tests (Unit, Type, Lint, Pipeline) run on every push to `main` via GitHub Actions.
