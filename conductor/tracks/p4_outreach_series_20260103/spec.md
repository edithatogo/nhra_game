# Track Spec: P4 Outreach Series (NHRA-centred, Game Theory Explained)

## Overview
Create a public-facing publication series (LinkedIn articles + covering LinkedIn posts + covering X/Twitter threads) that explains real-world NHRA scenarios using paired, simple game-theoretic models. The series is understandable to an interested public audience (explicitly including a 14-year-old reader), while remaining faithful to the codebase’s mechanisms and policy evidence.

Deliverables live in `publications/P4_Outreach_Series/` (peer to P1/P2/P3), with Markdown drafts, diagram sources, and rendered assets.

## Audience & Tone
- Primary audience: Interested public / general readers (14yo-friendly).
- Style: minimal jargon, short definitions, concrete analogies, light humour where appropriate.
- Voice: NHRA-centred narrative first; game theory as the explanatory tool (paired format).

## Functional Requirements

### 1) Outreach workspace in repo (structure + naming)
Create `publications/P4_Outreach_Series/` with:
- `00_series_meta/` (global templates, specs, manifests, shared styles)
- Ordered bundle folders: `01_<bundle_slug>/`, `02_<bundle_slug>/`, …

Each bundle folder contains:
- `article/` (LinkedIn long-form)
- `social/` (LinkedIn cover post + X/Twitter thread)
- `images/src/` (diagram sources: `.mmd`, `.dot`)
- `images/out/` (exports: `.svg` master + `.png` upload targets)
- `feedback/` (stakeholder feedback + consensus decisions)

### 2) Series manifest (source of truth)
Add `publications/P4_Outreach_Series/00_series_meta/series_manifest.yaml` defining:
- Bundle order, slugs, titles
- “NHRA scenario ↔ model/solution concept” pairing per bundle
- Code pointers (e.g., `src/nhra_gt/game_theory/content.py` IDs; relevant modules/functions)
- Required outputs per bundle (article/post/thread, required images)
- Key evidence references (central IDs + per-bundle links)

All automation (scaffold/render/validate/index) uses this manifest to avoid repo-wide directory scans.

### 3) Bundle outputs (per NHRA scenario / model pair)
Per bundle, produce:
- LinkedIn article draft (Markdown)
- Covering LinkedIn post draft (Markdown)
- Covering X/Twitter thread draft (Markdown; tweet-by-tweet)
- Images:
  1) NHRA context diagram(s),
  2) game model / solution concept diagram(s),
  3) a “summary/cover” image.

### 4) Initial series scope (“every model”)
Initial bundle list includes:
- Scenario-games curated in `src/nhra_gt/game_theory/content.py` (Definition, Bargaining, Cost Shifting, Discharge, Governance, Compliance, Internal LHN Competition, Electoral).
- `src/nhra_gt/subgames/sequential.py` (Rubinstein alternating offers; Stackelberg).
- `src/nhra_gt/subgames/queuing.py` (Wardrop/queuing equilibrium framing).
- Additional bundles:
  - Hybrid/Ensemble: how models combine in the codebase’s approach.
  - Streamlit dashboard: how to explore scenarios + interpret outputs.

### 5) Versioning convention
All drafts are versioned using `v#_YYYYMMDD` and created as new files (no overwriting).

### 6) Simulated stakeholder feedback cycles + consensus updates
Simulate a mixed panel (public-first + policy-first), explicitly including a 14yo reader perspective.
For each bundle:
- Record feedback: `feedback/feedback_v#_YYYYMMDD.md`
- Record consensus priorities: `feedback/consensus_v#_YYYYMMDD.md`
- Apply prioritized changes into new draft versions.

Iteration strategy (hybrid):
- Full multi-cycle iteration on the first 2–3 bundles.
- Single-cycle feedback pass on each remaining bundle.

Include a lightweight scoring rubric for repeatability:
- Clarity, accuracy, humour appropriateness, “14yo ok?”, policy usefulness (1–5), plus “top 3 fixes”.

### 7) Citations and “validated” links
Hybrid approach:
- Core references centralized in `publications/shared/references/library.yaml` where possible.
- Each bundle includes a short “Further reading / Evidence” section with inline Markdown links.
- No invented citations: every cited claim maps to real policy documents, official reports, or peer-reviewed analysis.
- Include a link-validation step in implementation (may require explicit network approval).

### 8) Diagram + image production (mmdc + Graphviz) and LinkedIn image specs
Tooling:
- `mmdc` (Mermaid) and Graphviz (`dot`) are used for publication-quality renders.

Deterministic styling:
- Store Mermaid theme/config in `00_series_meta/mermaid-config.json`.
- Store Graphviz defaults in `00_series_meta/graphviz_style.dot` (or equivalent).
- Consistent palette, fonts, and spacing across the series.

Outputs and naming:
- Every visual has a “master” export (SVG preferred) plus exact-dimension PNG targets.
- Filenames encode platform + dimensions, e.g.:
  - `cover_linkedin_article_1200x644.png`, `cover_linkedin_article_2400x1288.png`
  - `cover_linkedin_post_square_1200x1200.png`, `cover_linkedin_post_square_2400x2400.png`

Platform targets (to be documented + confirmed in `00_series_meta/platform_image_specs.md`):
- LinkedIn article cover (landscape): `1200x644` (1x) and `2400x1288` (2x)
- LinkedIn feed cover (square): `1200x1200` (1x) and `2400x2400` (2x)

“Pixel density” requirement:
- Treat 2x exports as the high-density standard (retina-safe).
- Scripts must validate exact pixel dimensions for every PNG target.

### 9) Automated validations
Provide automation to validate:
- Bundle completeness (required files exist per manifest)
- Image dimensions (PNG pixel size matches targets)
- Social constraints (e.g., X/Twitter tweet length ≤ 280 chars per tweet)
- Readability heuristics (target: smart non-specialist / 14yo-friendly)

## Non-Functional Requirements
- Accessibility: avoid red/green-only encoding; ensure readable contrast; diagrams legible on mobile; include captions + alt text.
- Professional humour: light, never dismissive of patient impact.
- Reproducibility: diagrams and checks can be rerun from source files.
- Robustness: workflows should avoid repo-wide directory scans and rely on the manifest (helps in sync-backed filesystems).

## Acceptance Criteria
- [ ] `publications/P4_Outreach_Series/` exists with ordered bundle folders and standard sub-structure.
- [ ] A `00_series_meta/series_manifest.yaml` exists and drives scaffolding/render/validation.
- [ ] Every bundle contains versioned article/post/thread drafts (`v#_YYYYMMDD`).
- [ ] Every bundle contains explanatory diagrams plus cover images exported to LinkedIn targets (1x + 2x) with validated pixel dimensions.
- [ ] Stakeholder feedback + consensus decisions are documented, with multiple cycles on the first 2–3 bundles and at least one cycle on the rest.
- [ ] Each bundle includes policy-relevant implications and real reference links; core references centralized where appropriate.
- [ ] Language passes the 14yo “understandable” bar (explicitly checked via stakeholder simulation).

## Out of Scope
- Actually publishing/scheduling content on LinkedIn/X.
- Legal advice or definitive claims about intent beyond cited evidence.
- Guaranteeing platform specs beyond what’s documented and validated at implementation time.
