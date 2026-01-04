# Changelog

This page tracks major changes to the NHRA Game Theory toolkit.

---

## v26.0.1 — 2025-12-27

### Documentation

- **Comprehensive documentation expansion**: Added guides (usage, models), project (requirements), and reference sections
- **Game theory models reference**: Documented all 9 stage games with payoff formulas
- **Architecture diagrams**: Added Mermaid diagrams for system architecture and data flow

### CI/CD

- Fixed isort/ruff conflict by consolidating on ruff I001
- Added `.gitattributes` for LF line endings (Windows fix)
- Updated deptry ignores for dependency hygiene

---

## v23 — 2025-12-24

### Features

- **Dashboard Enhancements**: Added Effective Share Drift analysis and Ranked Intervention Table (with uncertainty)
- **Reporting**: Automated generation of Methods Appendix and Manuscript Parameter Table (STRESS compliant)
- **Documentation**: Restructured reporting scripts into `scripts/reporting/`

---

## v22 — 2025-12-24

### Features

- **Empirical Spine**: Integrated historical NEP (IHACPA) and WPI (ABS) series to drive efficiency gap drift dynamically
- **Mechanism Refinement**: Overhauled Cost Shifting game to correct inert parameter sensitivity
- **Stability Analysis**: Added tipping point heatmap and PSA distribution analysis
- **Validation**: Implemented Recursive Backtesting Engine (rolling horizon) and Mechanism Validation Suite

---

## v21 — 2025-12-21

### Features

- Added Kiro-style project context artifacts: requirements.md, design.md, tasks.md
- Updated context pack builder to include project docs and parameter registry
- Migrated parameter registry schema and strengthened public-only grounding checks

---

## v17 — 2025-12-21

### Features

- Round 2 review + implementation: decision-oriented intervention scenarios
- Extended equilibria exports
- Expanded narrative report with figure captions and abbreviations
- Added run/plot/report scripts for v17 outputs

---

## v16 — 2025-12-21

### Features

- Round 1 review + implementation
- Per-file coverage enforcement (>=95%)
- Expanded reporting and summaries
- Diagram sync outputs

---

## v15 — 2025-12-20

### Features

- Initial equilibria solver implementation (pure + mixed where applicable)
- Scenario and sensitivity analysis additions

---

## Earlier Versions

For the complete changelog, see the [CHANGELOG.md](https://github.com/edithatogo/nhra_game/blob/main/CHANGELOG.md) in the repository root.
