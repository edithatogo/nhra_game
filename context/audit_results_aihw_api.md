# Audit Report: AIHW API & Data Flow
**Date:** 2025-12-26

## 1. AIHW API Implementation
*   **Client:** `src/nhra_gt/domain/aihw_api.py::AIHWClient`
*   **Status:** Functional. Implements a standard REST client for `myhospitalsapi.aihw.gov.au/api/v1`.
*   **Endpoints used:** `/datasets`, `/measures/{code}/data-items`.

## 2. Current Data Flow (Observed)

### A. Automated Path (Incomplete)
1.  **Ingestion:** `scripts/data/ingest_aihw_api.py` fetches `MYH0005` (ED Performance) from AIHW.
2.  **Output:** Saves to `data/raw/historical_aihw_api.csv`.

### B. Baseline Path (Active)
1.  **Source:** `data/raw/historical_aihw_ed.csv` (Static/Manual file).
2.  **Processing:** `scripts/data/preprocess_historical.py` reads `...ed.csv`.
3.  **Normalization:** Outputs `data/calibration/historical_normalized.csv`.
4.  **Usage:** `historical_normalized.csv` is consumed by:
    -   `scripts/dashboard.py` (Historical vs. Simulated comparison).
    -   `scripts/validation/recursive_backtest.py` (Validation loop).

## 3. Findings & Disconnects
*   **The "Shadow" Path:** The automated API ingestion (`...api.csv`) is currently **decoupled** from the rest of the pipeline. The preprocessing script still targets the manual `...ed.csv` file.
*   **Data Integrity:** The automated ingestion filters for `NAT` (National) aggregate and `MYH-RM0015` (All patients). This matches the intended "Within 4 Hours" metric used in the model.
*   **Automation Gap:** To fully automate the "Historical Data" pipeline, `preprocess_historical.py` should be updated to prioritize `historical_aihw_api.csv` or a combined registry.

## 4. Recommendations
1.  **Link Ingestion to Preprocessing:** Update `scripts/data/preprocess_historical.py` to use `data/raw/historical_aihw_api.csv` as its primary source.
2.  **Diagram Generation:** Create a Mermaid diagram (delivered in Deliverable 2) showing this flow.
