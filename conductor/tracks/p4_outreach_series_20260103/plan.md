# Implementation Plan: P4 Outreach Series (NHRA-centred, Public-first)

## Phase 1: Foundations (Manifest, Scaffold, Templates, Rendering, Validators)
- [ ] Task: Define authoritative series manifest (`series_manifest.yaml`)
  - [ ] Create `publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml`
  - [ ] Include bundle ordering, slugs, pairings, code pointers, required outputs, required image targets, key evidence links
- [ ] Task: Create outreach scaffold (manifest-driven)
  - [ ] Create `publications/P4_Outreach_Series/00_series_meta/` docs:
        `README.md`, `stakeholder_panel.md`, `diagram_style.md`,
        `platform_image_specs.md`, `image_targets.yaml`
  - [ ] Add a scaffold script (manifest → folders) to avoid directory-wide scanning
- [ ] Task: Deterministic diagram styling
  - [ ] Add `00_series_meta/mermaid-config.json` (theme, fonts, colours)
  - [ ] Add `00_series_meta/graphviz_style.dot` (style defaults)
- [ ] Task: Rendering pipeline (mmdc + Graphviz) + strict filenames
  - [ ] Write failing tests for render + output naming + target generation
  - [ ] Implement `scripts/outreach/render_all.py` (reads manifest; renders `.mmd`/`.dot` → SVG master + PNG targets)
  - [ ] Implement exact-size PNG exports for each target (1x + 2x), using the most reliable available local tools
- [ ] Task: Validators (automated QA)
  - [ ] Write failing tests for each validator
  - [ ] Implement `scripts/outreach/validate_bundle_completeness.py` (manifest required outputs)
  - [ ] Implement `scripts/outreach/validate_images.py` (PNG pixel dimensions match targets)
  - [ ] Implement `scripts/outreach/validate_social.py` (X tweet lengths; optional LinkedIn length heuristics)
  - [ ] Implement `scripts/outreach/validate_readability.py` (simple heuristics/grade target)
- [ ] Task: Templates + checklists + stakeholder rubric
  - [ ] Add templates for article/post/thread + image captions/alt text
  - [ ] Add “14yo readability checklist”
  - [ ] Add stakeholder scoring rubric (clarity/accuracy/humour/14yo/policy usefulness)
- [ ] Task: References workflow (hybrid)
  - [ ] Curate recurring “core” references into `publications/shared/references/library.yaml`
  - [ ] Define per-bundle “Evidence / Further reading” format (inline links + core IDs)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundations (Manifest, Scaffold, Templates, Rendering, Validators)' (Protocol in workflow.md)

## Phase 2: Full-cycle iteration (first 3 bundles; multi-round feedback)
- [ ] Task: Bundle 01 — v1 drafts + images + renders + validations + feedback/consensus
- [ ] Task: Bundle 01 — iterate to v2/v3 until “public + 14yo” pass (rubric-based)
- [ ] Task: Bundle 02 — v1 → iterate to v2/v3 until “public + 14yo” pass
- [ ] Task: Bundle 03 — v1 → iterate to v2/v3 until “public + 14yo” pass
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Full-cycle Iteration (First 3 Bundles)' (Protocol in workflow.md)

## Phase 3: Remaining scenario bundles (single feedback cycle each)
- [ ] Task: Bundle 04 — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 05 — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 06 — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 07 — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 08 — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 09 (Rubinstein) — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 10 (Stackelberg) — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Bundle 11 (Queuing equilibrium) — v1 → feedback/consensus → v2 (run validators)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Remaining Scenario Bundles (Single-cycle Each)' (Protocol in workflow.md)

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
