# Data Source Status Table

**Date:** 2025-12-26

| Data Source | Type | Status | Ingestion Path | Grounding Level |
| :--- | :--- | :--- | :--- | :--- |
| **ED Care ≤ 4h** | Operational | **Automated** | AIHW MyHospitals API | High (Official API) |
| **NEP सीरीज** | Economic | **Manual** | Hardcoded in `ingest_economic_spine.py` | High (Determination 25-26) |
| **WPI Health** | Economic | **Manual** | Hardcoded in `ingest_economic_spine.py` | Medium (Synthetic trends) |
| **IHACPA NWAU Tables** | Operational | **Orphaned** | Files present in `data/raw/` but unused | N/A (Out of scope) |
| **Moris Screening** | Sensitivity | **Static** | `data/raw/morris_screening.csv` | Medium (Historical sample) |
| **Policy Asks** | Strategic | **Static** | `data/raw/policy_asks.csv` | Low (Model Assumption) |

**Note on "NWAU Tables":** The detailed service-level Excel calculators are present in the repo but the model correctly defaults to the aggregate NEP index to maintain a policy-level abstraction.
