# Data provenance

This repository aims to use **publicly retrievable sources only**.

## Sources used in this repo

1. **NHRA documents** (agreements, addenda, schedules) hosted on:
   - Federal Financial Relations website
   - Australian Government Department of Health, Disability and Ageing
   - National Health Funding Body (NHFB)
2. **Hospital performance indicators** (e.g. ED≤4h) from AIHW public dashboards.
3. **Price/index indicators** for cost drift (e.g. wages inflation) from ABS.

## What is *not* included

- Proprietary datasets
- Hospital-identifiable line-level data
- Restricted consultation documents

## How to update sources

Add new sources to `context/04_parameter_registry.csv` with a stable URL and a locator (page/table/section) and rerun:

```bash
just context
```

## Technical Implementation Details

The following automated and semi-automated ingestion paths are implemented:

| Data Type | Source | Implementation | Output Artifact |
| :--- | :--- | :--- | :--- |
| **ED Performance** | AIHW MyHospitals API | `scripts/data/ingest_aihw_api.py` | `data/raw/historical_aihw_api.csv` |
| **Economic Spine** | IHACPA Determinations | `scripts/data/ingest_economic_spine.py` | `data/calibration/economic_spine.csv` |

*Note: The Economic Spine (NEP/WPI) currently uses hardcoded series in the ingestion script and requires manual updates for new Determinations. AIHW ingestion is fully automated via the public API.*
