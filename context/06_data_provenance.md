# Data provenance

This repository aims to use **publicly retrievable sources only**.

## Sources used in this repo

Detailed citations are maintained in [`data/bibliography/sources.bib`](../data/bibliography/sources.bib).

1. **NHRA documents** (agreements, addenda, schedules) hosted on:
   - Federal Financial Relations website
   - Australian Government Department of Health, Disability and Ageing
   - National Health Funding Body (NHFB)
2. **Hospital performance indicators** (e.g. ED≤4h) from AIHW public dashboards.
   - *Dataset:* `data/raw/historical_aihw_api.csv` (Source: AIHW MyHospitals API)
   - *Dataset:* `data/raw/historical_aihw_ed.csv` (Source: AIHW Historical Data)
3. **Price/index indicators** for cost drift (e.g. wages inflation) from ABS.
   - *Dataset:* `data/raw/abs_wpi_health_raw.csv` (Source: ABS Wage Price Index, Health Industry)
4. **Efficiency Pricing** from IHACPA Determinations.
   - *Dataset:* `data/calibration/economic_spine.csv` (Source: IHACPA NEP Determinations 2011-2025)

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

## Historical validation

The published ED time-spent series supplies four-hour completion observations.
The current repository extract has no source-qualified annual occupancy
series for the same scope. The older normalization interpolated occupancy
between two unverified endpoints. Those interpolated values cannot supply
observed holdouts.

`snakemake --cores 1 validate` requires the complete historical inputs for
the empirical report. The CI report test runs the report rules in a
temporary directory with six years of synthetic observations. Its missing
occupancy case verifies that the workflow stops before producing any
holdout or report. The test outputs stay in the temporary directory.

Earlier drafts cite a 2021 Stephen Duckett article on hospital bed block.
Bibliography record 102 linked to a case report on epipericardial fat
necrosis. The DOI used in the manuscript drafts identifies a letter on
respirator fit testing. The bed-block citation requires source
identification before it can support a claim. [Bibliography DOI record](https://pubmed.ncbi.nlm.nih.gov/33792067/) ·
[Manuscript DOI record](https://pubmed.ncbi.nlm.nih.gov/33837543/)
