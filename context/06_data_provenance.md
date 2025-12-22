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
