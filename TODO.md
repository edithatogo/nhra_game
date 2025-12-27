# TODO: Documentation Expansion and CI Completion

## Status: Documentation Overhaul In Progress

Latest commit: `fde586b` - comprehensive documentation expansion

---

## 1. DISC Game Re-integration ✅ COMPLETE

The `discharge_coordination_game` is **already integrated**:
- Import at `src/nhra_gt/agents/base.py:17`
- Usage at `src/nhra_gt/agents/base.py:277`
- Definition at `src/nhra_gt/subgames/games.py:135`

---

## 2. Documentation Overhaul `[docs]`

### Structure (✅ Complete)
- [x] Create `docs_mkdocs/guides/` directory
  - [x] `index.md` — Guides landing page
  - [x] `usage.md` — Installation, quickstart, CLI examples
  - [x] `models.md` — Game theory models (all 9 games with payoffs)
- [x] Create `docs_mkdocs/project/` directory
  - [x] `index.md` — Project landing page
  - [x] `requirements.md` — Project scope, roadmap, limitations
- [x] Create `docs_mkdocs/reference/` directory
  - [x] `index.md` — API reference with mkdocstrings

### Content Fixes (✅ Complete)
- [x] Populate `diagrams.md` with Mermaid architecture diagrams
- [x] Fix `context.md` — `nhra_gt.v9.Params` → `nhra_gt.engine.Params`
- [x] Fix `index.md` — correct broken links
- [x] Update `mkdocs.yml` — add explicit nav structure

### Remaining Enhancements
- [ ] Create `changelog.md` or link to CHANGELOG.md
- [ ] Add examples/ section with Jupyter notebooks
- [ ] Enhance API reference with more modules
- [ ] Add contributing.md guide
- [ ] Add FAQ section
- [ ] Review and enhance dev.md
- [ ] Add validation/testing documentation

---

## 3. CI Status `[pending]`

- [ ] Verify CI passes after documentation push
- [ ] Check Deploy Docs workflow succeeds

---

## 4. Future Improvements

- [ ] Add interactive examples with Jupyter
- [ ] Create video walkthrough
- [ ] Add comparison tables for policy scenarios
- [ ] Document calibration workflow
