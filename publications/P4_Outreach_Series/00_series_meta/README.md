# P4 Outreach Series

This folder contains draft LinkedIn articles, covering LinkedIn posts, and X/Twitter threads that explain NHRA scenarios using simple, paired game-theory models.

## Source of Truth

- `00_series_meta/series_manifest.yaml` is the inventory for bundles, required outputs, code pointers, and required image targets.

## Structure

- `00_series_meta/` shared templates, styling, and validation targets.
- `01_*/` .. `13_*/` one bundle per NHRA scenario/model pair.

## Key workflow rules

- Avoid repo-wide directory scans in scripts; rely on `series_manifest.yaml`.
- Drafts are versioned with `v#_YYYYMMDD` and never overwritten.

## Validation (run every time)

Bundle-level (recommended during drafting):

- `python scripts/outreach/render_all.py --bundle <slug> --strict-sources`
- `python scripts/outreach/validate_images.py --bundle <slug>`
- `python scripts/outreach/validate_bundle_completeness.py --bundle <slug>`

Series-level (for release readiness):

- `python scripts/outreach/validate_bundle_completeness.py`
- `python scripts/outreach/validate_social.py --root publications/P4_Outreach_Series`
- `python scripts/outreach/validate_readability.py --root publications/P4_Outreach_Series --max-grade 9.5`
- `python scripts/outreach/validate_links.py --root publications/P4_Outreach_Series` (treats 403/429 as warnings by default)
