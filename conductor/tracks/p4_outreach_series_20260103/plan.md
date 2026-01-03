# Implementation Plan: P4 Outreach Series (NHRA-centred, Public-first)

## Phase 1: Foundations (Manifest, Scaffold, Templates, Rendering, Validators)
- [x] Task: Define authoritative series manifest (`series_manifest.yaml`)
  - [x] Create `publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml`
  - [x] Include bundle ordering, slugs, pairings, code pointers, required outputs, required image targets, key evidence links
- [x] Task: Create outreach scaffold (manifest-driven)
  - [x] Create `publications/P4_Outreach_Series/00_series_meta/` docs:
        `README.md`, `stakeholder_panel.md`, `diagram_style.md`,
        `platform_image_specs.md`, `image_targets.yaml`
  - [x] Add a scaffold script (manifest → folders) to avoid directory-wide scanning
- [x] Task: Deterministic diagram styling
  - [x] Add `00_series_meta/mermaid-config.json` (theme, fonts, colours)
  - [x] Add `00_series_meta/graphviz_style.dot` (style defaults)
- [x] Task: Rendering pipeline (mmdc + Graphviz) + strict filenames
  - [x] Write tests for render script behavior (mock subprocess; ensure puppeteer config used)
  - [x] Implement `scripts/outreach/render_all.py` (reads manifest; renders `.mmd`/`.dot` → SVG master + PNG targets)
  - [x] Implement exact-size PNG exports for each target (1x + 2x), using the most reliable available local tools
- [x] Task: Validators (automated QA)
  - [x] Write failing tests for validators
  - [x] Implement `scripts/outreach/validate_bundle_completeness.py` (manifest required outputs)
  - [x] Implement `scripts/outreach/validate_images.py` (PNG pixel dimensions match targets)
  - [x] Implement `scripts/outreach/validate_social.py` (X tweet lengths; optional LinkedIn length heuristics)
  - [x] Implement `scripts/outreach/validate_readability.py` (simple heuristics/grade target)
- [x] Task: Templates + checklists + stakeholder rubric
  - [x] Add templates for article/post/thread + image captions/alt text
  - [x] Add “14yo readability checklist”
  - [x] Add stakeholder scoring rubric (clarity/accuracy/humour/14yo/policy usefulness)
- [x] Task: References workflow (hybrid)
  - [x] Curate recurring “core” references into `publications/shared/references/library.yaml`
  - [x] Define per-bundle “Evidence / Further reading” format (inline links + core IDs)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundations (Manifest, Scaffold, Templates, Rendering, Validators)' (Protocol in workflow.md)

## Phase 2: Full-cycle iteration (first 3 bundles; multi-round feedback) [checkpoint: 3223376]
- [x] Task: Bundle 01 — v1 drafts + images + renders + validations + feedback/consensus
- [x] Task: Bundle 01 — iterate to v2/v3 until “public + 14yo” pass (rubric-based)
- [x] Task: Bundle 02 — v1 → iterate to v2/v3 until “public + 14yo” pass
- [x] Task: Bundle 03 — v1 → iterate to v2/v3 until “public + 14yo” pass (1b461ec)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Full-cycle Iteration (First 3 Bundles)' (Protocol in workflow.md)

## Phase 3: Remaining scenario bundles (single feedback cycle each) [checkpoint: 5764810]
- [x] Task: Bundle 04 — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 05 — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 06 — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 07 — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 08 — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 09 (Rubinstein) — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 10 (Stackelberg) — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Bundle 11 (Queuing equilibrium) — v1 → feedback/consensus → v2 (run validators)
- [x] Task: Conductor - User Manual Verification 'Phase 3: Remaining Scenario Bundles (Single-cycle Each)' (Protocol in workflow.md)

## Phase 4: Hybrid/Ensemble + Streamlit dashboard bundles
- [ ] Task: Bundle 12 (Hybrid/Ensemble) — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 13 (Streamlit dashboard) — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Hybrid/Ensemble + Dashboard Bundles' (Protocol in workflow.md)

## Phase 5: Series QA, index, and link validation
- [ ] Task: Generate/refresh series index from manifest (links + recommended reading order)
- [ ] Task: Run offline validations (completeness + images + social + readability) and fix issues
- [ ] Task: Run online link validation for all referenced URLs (requires network approval) and fix broken/unstable links
- [ ] Task: Final consistency pass (tone, humour, accessibility, policy implications, evidence)
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Series QA, Index, Link Validation' (Protocol in workflow.md)
