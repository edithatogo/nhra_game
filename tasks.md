# tasks.md — Roadmap and implementation plan (v21)

**Version:** v21  
**Date:** 2025-12-21

## Completed in v21

1. Added **requirements.md**, **design.md**, **tasks.md** as durable context artifacts.
2. Extended the **context pack** to incorporate these artifacts.
3. Tightened the grounding system to enforce **publicly retrievable sources only**.
4. Updated developer workflows (`just`, `snakemake`) to build the context pack and run grounding checks.

## Completed in v23 — Reporting & Scenarios
1. **Negotiation Dashboard:** Added Effective Share Drift analysis and Ranked Intervention Table.
2. **Automated Methods:** Implemented `generate_methods_appendix.py` and academic-style parameter exports.
3. **Refined Mechanisms:** Resolved validation discrepancies; model now aligns with historical Rank #1 driver (Discharge Delay).

## Next (v24) — Automated Evidence & API Integration

### Empirical API Integration
- **MyHospitals API:** Implement `scripts/data/ingest_aihw_api.py` to fetch facility-level and quarterly metrics directly from AIHW {Australian Institute of Health and Welfare, 2024 @AIHW_MyHospitals #101}.
- **Dynamic Calibration:** Automate model re-calibration when API data updates.

### Evidence & Bibliography Engine
- **Automated Citations:** Implement a robust bibliography manager supporting Endnote style `{Author, YYYY @Label #RecordNumber}`.
- **Reference Exports:** Generate `.ris`, `.enw`, and `.bib` files with full metadata and validated DOIs/URLs.
- **Academic Standards:** Ensure all model evidence is linked to high-impact, recent literature (e.g., MJA, Science, J Simulation).

### Audit & Metadata
- **Experiment Logging:** Implement structured metadata recording for every Monte Carlo run (seed, git-hash, compute-time, token-usage).
- **Provenance Tracking:** Automate the 'Data Lineage' tab in the dashboard using the new API ingestor.

## Governance and maintenance

- Maintain a `decisions/` log for major modelling choices.
- Ensure each version update:
  - increments CHANGELOG,
  - regenerates CONTEXT_PACK.md/json,
  - re-runs `just all` in CI.
