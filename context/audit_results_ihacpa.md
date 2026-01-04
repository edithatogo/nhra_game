# Audit Report: IHACPA NWAU Pricing Tables

**Date:** 2025-12-26

## 1. Summary of Usage

The repository currently uses **Aggregate National Efficient Price (NEP)** values for its economic backbone but ignores the detailed service-level pricing tables provided by IHACPA.

## 2. Findings

### A. Hardcoded Economic Spine

- **File:** `scripts/data/ingest_economic_spine.py`
- **Logic:** The National Efficient Price (NEP) series for 2011–2025 is hardcoded in a Python dictionary (`NEP_SERIES`).
- **Impact:** While accurate for the years provided, it requires manual code updates for each new Determination release and lacks automated provenance from the source documents.

### B. Orphaned Detailed Calculators

- **Location:** `data/raw/`
- **Files:** Multiple `.xlsb` files (e.g., `nwau25_calculator_for_ED_activity_AECC.xlsb`, `nwau25_calculator_for_acute_activity.xlsb`).
- **Status:** These files have been downloaded to the repository but are **not used** by any ingestion script or the simulation engine.
- **Answer to User Query:** No, the model is not using the available detailed NWAU pricing tables. It uses a stylised aggregate index ($/NWAU) instead.

### C. Methodological Choice

- **Documentation:** `scripts/archive/build_report_v19.py` explicitly states: *"The model does not implement IHACPA’s detailed NWAU calculators; NEP is included to keep the valuation story disciplined."*
- **Finding:** This is an intentional design choice to keep the model at a "Policy/Negotiation" scale rather than an "Operational/Billing" scale.

## 3. Recommendations

1. **Automate Economic Spine Ingestion:** Create a script to extract the annual NEP directly from the IHACPA National Efficient Price Determination PDF or summary tables, rather than hardcoding in `scripts/data/ingest_economic_spine.py`.
2. **Formalize Scope:** Update the `README.md` or `product.md` to clarify that the model targets *aggregate negotiation dynamics* and that detailed NWAU calculation (DRG level) is out of scope.
3. **Cleanup:** If the `.xlsb` files are not intended for use, they should be moved to an `archive/` or `data/raw/ihacpa_detailed/` folder to reduce clutter in the main `data/raw/` directory.
