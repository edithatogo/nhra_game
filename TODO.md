# TODO: Documentation Expansion and CI Completion

## Status: CI Fixes Pushed (pending verification)

Commit `26d7b22` includes:
- [x] `.gitattributes` for LF line endings (Windows fix)
- [x] `deptry` ignores updated (DEP001/002/003/004)
- [x] `test_intervention_ranking.py` fix (`dashboard_v21` → `dashboard`)
- [x] `test_pub_structure.py` skip for CI

---

## 1. DISC Game Re-integration ✅ COMPLETE

The `discharge_coordination_game` is **already integrated**:
- Import at `src/nhra_gt/agents/base.py:17`
- Usage at `src/nhra_gt/agents/base.py:277`
- Definition at `src/nhra_gt/subgames/games.py:135`

---

## 2. Documentation Overhaul `[docs]`

### Critical Issues (Broken Links from index.md)
- [ ] Create `docs_mkdocs/guides/` directory <!-- id: 100 -->
  - [ ] `usage.md` — Installation, quickstart, CLI examples
  - [ ] `models.md` — Game theory models master reference
- [ ] Create `docs_mkdocs/project/` directory <!-- id: 110 -->
  - [ ] `requirements.md` — Project scope, roadmap
- [ ] Create `docs_mkdocs/reference/` directory <!-- id: 120 -->
  - [ ] Auto-generated API reference structure

### Content Fixes
- [ ] Populate `diagrams.md` with architecture diagrams <!-- id: 130 -->
- [ ] Fix `context.md` — update `nhra_gt.v9.Params` → `nhra_gt.engine.Params` <!-- id: 131 -->
- [ ] Create `changelog.md` or link to CHANGELOG.md <!-- id: 132 -->

### Game Theory Models Documentation
- [ ] Document all 9 stage games with payoff matrices: <!-- id: 140 -->
  - definition_game
  - bargaining_game
  - cost_shifting_game
  - discharge_coordination_game
  - governance_integration_game
  - aged_care_interface_game
  - ndis_interface_game
  - coding_audit_game
  - compliance_game
