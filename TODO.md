# TODO: Documentation Expansion and CI Completion

## Status: All Enhancements Complete ✅

Latest commits:

- `fde586b` — Initial documentation expansion  
- `2231a0f` — Changelog, contributing guide, enhanced dev docs
- `pending` — FAQ, validation, policy scenarios

---

## 1. DISC Game Re-integration ✅ COMPLETE

The `discharge_coordination_game` is **already integrated**:

- Import at `src/nhra_gt/agents/base.py:17`
- Usage at `src/nhra_gt/agents/base.py:277`
- Definition at `src/nhra_gt/subgames/games.py:135`

---

## 2. Documentation Overhaul ✅ COMPLETE

### Core Structure

- [x] `guides/` — index, usage, models (9 games)
- [x] `project/` — index, requirements
- [x] `reference/` — API reference
- [x] `diagrams.md` — Mermaid architecture diagrams
- [x] `changelog.md` — Version history (v15-v26)
- [x] `contributing.md` — PR process, code style
- [x] `dev.md` — Tooling, testing, profiling, CI/CD

### Enhancements

- [x] `faq.md` — Frequently asked questions
- [x] `validation.md` — Testing and validation documentation
- [x] `scenarios.md` — Policy comparison tables

### Fixes

- [x] Fixed `context.md` — `nhra_gt.v9.Params` → `nhra_gt.engine.Params`
- [x] Fixed `index.md` — Correct links to new directories
- [x] Updated `mkdocs.yml` — Explicit nav with all new pages
- [x] Removed redundant `api.md`

---

## 3. Future Improvements (Deferred)

- [ ] Add examples/ with Jupyter notebooks (requires real data)
- [ ] Create video walkthrough (requires screen recording)
