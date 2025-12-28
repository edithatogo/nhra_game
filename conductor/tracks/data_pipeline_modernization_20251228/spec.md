# Specification: Data Pipeline & Infrastructure Modernization

## 1. Overview
This track automates the final link in the data pipeline: the "Data Spine". It ensures that fresh data from AIHW and IHACPA APIs automatically updates the simulation's `EconomicSpineJax` and `ParamsJax` without requiring manual source-code or dictionary edits.

## 2. Functional Requirements

### FR1: Automated Economic Spine (JAX)
- Link `preprocess_historical.py` output directly to `EconomicSpineJax`.
- The engine must load the latest normalized data from `data/calibration/historical_normalized.csv` at runtime.

### FR2: Evidence Registry Sync
- Extend `EvidenceRegistry` to automatically promote "Live" API data to active simulation parameters.
- Implement a "Schema Enforcement" layer to prevent corrupt API data from breaking the model.

### FR3: Persistent Parameter Registry
- Move hardcoded assumptions in `ParamsJax` to a managed YAML configuration file (`configs/base_params.yaml`).
- Allow the dashboard to overwrite these defaults via the registry UI.

## 3. Technical Constraints
- **Format:** Use Polars for all intermediate data processing to maintain performance.
- **Validation:** All incoming data must pass `Pandera` schema validation before being promoted to the "Active" spine.

## 4. Acceptance Criteria
- Running `scripts/ingest_all.sh` (or equivalent) results in an immediate update to the "Live" metrics in the dashboard.
- Verification that `ParamsJax` defaults are now loaded from a configuration file rather than hardcoded in the class.
