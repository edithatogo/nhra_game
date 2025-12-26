# Changelog

## v26.0.1 — 2025-12-26
- **Fix:** Corrected version mismatch in `pyproject.toml` (was 0.20.0, now 26.0.1).
- **Deployment:** Added automated GitHub Release workflow.
- **Maintenance:** Resolved rebase state and consolidated figure refactoring.

## v26.0.0 — 2025-12-24
- **Dashboard Enhancements:** Added Effective Share Drift analysis and Ranked Intervention Table (with uncertainty).
- **Reporting:** Automated generation of Methods Appendix and Manuscript Parameter Table (STRESS compliant).
- **Documentation:** Restructured reporting scripts into `scripts/reporting/`.

## v22 — 2025-12-24
- **Empirical Spine:** Integrated historical NEP (IHACPA) and WPI (ABS) series to drive efficiency gap drift dynamically.
- **Mechanism Refinement:** Overhauled Cost Shifting game to correct inert parameter sensitivity.
- **Stability Analysis:** Added tipping point heatmap and PSA distribution analysis.
- **Validation:** Implemented Recursive Backtesting Engine (rolling horizon) and Mechanism Validation Suite.

## v21 — 2025-12-21
- Added Kiro-style project context artifacts: requirements.md, design.md, tasks.md.
- Updated context pack builder to include project docs and parameter registry.
- Migrated parameter registry schema and strengthened public-only grounding checks.


## v19 (planned) — 2025-12-21
- Final publication polish and additional interactive outputs.

## v18 (planned) — 2025-12-21
- Time-varying NEP vs input-cost drift and expanded calibration hooks.

## v17 — 2025-12-21
- Round 2 review + implementation: decision-oriented intervention scenarios, extended equilibria exports, and an expanded narrative report with figure captions and abbreviations.
- Added run/plot/report scripts for v17 outputs.

## v16 — 2025-12-21
- Round 1 review + implementation: per-file coverage enforcement (>=95%), expanded reporting and summaries, and diagram sync outputs.

## v15 — 2025-12-20
- Equilibria solved (pure + mixed where applicable) and scenario/sensitivity additions.
