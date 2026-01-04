# Round 2 Review — Professor of Medicine

**Date:** 2025-12-21  
**Scope:** Clinical plausibility, interpretability for clinicians/leaders, and safety framing.

## Summary

v16 is a strong step toward a clinically legible mechanism model, but it still risks losing medical audiences if results are not explicitly translated into safety-critical implications (access block, handover risk, delayed definitive care). The model should explicitly separate “risk proxy” from true harm outcomes and avoid any suggestion of quantitative prediction.

## Major points

1. **Clinical endpoints vs proxies:** Make explicit that offload and within-4-hours are proxies; add a clear clinical interpretation block and a limitations paragraph that rules out misuse for benchmarking.
2. **Intervention framing:** Add a decision table mapping interventions to expected directional impact, and note plausible unintended effects (e.g., audit blitz increasing admin burden).
3. **Equilibria communication:** Show why multiple equilibria matter clinically (“regimes”) and relate to real operational failure modes.

## Minor points

- Add an abbreviations list at the start of the report.
- Ensure NEP language is always “$/NWAU annually”.

## Recommendation

**Minor revision.**

## v17 response / implementation

Implemented in v17 via:

- A new narrative report with explicit proxy framing, abbreviations, and clinical interpretation (reports/v17_report_20251221.md).
- Policy intervention scenarios including an “audit_blitz” trade-off scenario and delta reporting (outputs/v17/tables/intervention_*.csv).
- Equilibria over time and regime interpretation (outputs/v17/tables/equilibria_by_year.csv; report section 2).
