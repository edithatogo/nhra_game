# Track Plan: WPI Health Data Automation (P2)

**Goal:** Automate the ingestion of ABS Wage Price Index (WPI) data for the Health care and social assistance sector, replacing hardcoded synthetic values.

## Phase 1: Research & API Discovery
- [x] Task: Identify the exact SDMX Dataflow ID and Query Parameters for "WPI - Health care and social assistance". (ID: `ABS,WPI`, Key: `1.THRPEB.7.Q.10.AUS.Q`)
- [x] Task: Test API connectivity and response format (JSON/CSV) using `curl` or a test script. (CSV preferred)

## Phase 2: Implementation (API Client)
- [x] Task: Create `src/nhra_gt/domain/abs_api.py` to handle ABS Data API requests.
- [x] Task: Implement parsing logic to extract the time series (Year, Value).
- [x] Task: Implement caching or local storage for the raw API response to avoid redundant calls.

## Phase 3: Integration (Economic Spine)
- [x] Task: Update `scripts/data/ingest_economic_spine.py` to call the ABS API client.
- [x] Task: Ensure the automated data aligns with the existing historical schema (2011–2025).
- [x] Task: Implement a fallback mechanism to use hardcoded values if the API is unavailable.

## Phase 4: Validation & CI/CD
- [x] Task: Create `tests/test_abs_ingestion.py` to verify the automated pipeline.
- [x] Task: Update the `data_refresh.yml` GitHub Action to include WPI updates.

---
**Track Status:** COMPLETED 2025-12-28
WPI Health data ingestion fully automated via ABS Data API. Integrated into economic spine and CI/CD refresh cycle. Verified with unit tests.
