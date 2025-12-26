# Audit Report: Data Verification (Manual Cross-Reference)
**Date:** 2025-12-26

## 1. Summary
A sample-based manual cross-reference was performed to verify the accuracy of the data ingested from the AIHW API and the hardcoded IHACPA parameters.

## 2. Verification Results

### A. AIHW MyHospitals ED Performance
- **Metric:** Percentage of patients seen within 4 hours (National Aggregate).
- **Year:** 2023-24 (Financial Year).
- **Repo Value:** `0.55` (55%) in `data/raw/historical_aihw_api.csv`.
- **Source Value:** `55%` (Source: AIHW Emergency Department Care 2023–24 report).
- **Status:** **MATCHED**.

### B. IHACPA National Efficient Price (NEP)
- **Metric:** National Efficient Price ($ per NWAU).
- **Year:** 2025-26 (Determination).
- **Repo Value:** `7258.0` in `scripts/data/ingest_economic_spine.py`.
- **Source Value:** `$7,258` (Source: IHACPA National Efficient Price Determination 2025–26).
- **Status:** **MATCHED**.

## 3. Conclusion
The core economic and operational baseline data in the repository is accurate and reflects official sources for the sampled points.
