# Implementation Plan (Round 1 → v16)

**Date:** 21 December 2025

## Goal

Deliver v16 as a management- and manuscript-ready package: correct terminology, improve reproducibility, and produce comprehensive narrative reporting with figure/table captions.

## Work items

1. **Quality & reproducibility**: enforce per-file coverage ≥95%; add CI check; add install validation steps.
2. **Reporting**: generate a comprehensive report with sections (baseline, equilibria, sensitivity, scenarios), captions, abbreviations, and section syntheses.
3. **Policy intervention scenarios**: add scenario set that maps to negotiation packages (funding-only vs governance package vs pooled pilots).
4. **Communications outputs**: add a 1-page briefing note and plain-text narrative summary.

## Acceptance criteria

- `pytest` passes; per-file coverage check passes.
- `scripts/run_v16_all.py` produces outputs and `reports/v16_report_20251221.md/html`.
- Figures and tables have titles, captions, abbreviations, and narrative interpretation.
