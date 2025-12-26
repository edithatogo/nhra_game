# TODO: Systematic Documentation Improvement

## 1. Infrastructure & Dependencies
- [x] Add `mkdocs-literate-nav` to pyproject.toml <!-- id: 10 -->
- [x] Add `mkdocs-section-index` to pyproject.toml <!-- id: 11 -->
- [x] Add `mkdocs-jupyter` to pyproject.toml <!-- id: 12 -->
- [x] Add `mike` to pyproject.toml <!-- id: 13 -->
- [x] Add `mkdocs-git-revision-date-localized-plugin` to pyproject.toml <!-- id: 101 -->
- [x] Add `pillow` and `cairo` (via `assist` or system) if needed for Social Cards <!-- id: 102 -->
- [x] Install new dependencies (`poetry install` or `pip install`) <!-- id: 14 -->
- [x] Configure `mkdocs.yml`: enable `mike` versioning logic <!-- id: 15 -->
- [x] Configure `mkdocs.yml`: enable `arithmatex` (MathJax) <!-- id: 16 -->
- [x] Configure `mkdocs.yml`: enable `snippets` <!-- id: 17 -->
- [x] Configure `mkdocs.yml`: enable Material features (tabs, search, copy, dark mode) <!-- id: 18 -->
- [x] Configure `mkdocs.yml`: set `mkdocstrings` python handler options <!-- id: 19 -->
- [x] Configure `mkdocs.yml`: set `nav` to use `literate-nav` <!-- id: 20 -->

## 2. Automated API Reference
- [x] Create `scripts/gen_ref_pages.py` <!-- id: 21 -->
  - [x] Implement recursive walk of `src/nhra_game_theory/` <!-- id: 22 -->
  - [x] Implement generation of ephemeral `.md` files <!-- id: 23 -->
  - [x] Map files to `reference/` section <!-- id: 24 -->
- [x] Verify script execution locally <!-- id: 25 -->

## 3. Structural Reorganization
- [x] Create directory `docs_mkdocs/project/` and move requirements, design, tasks <!-- id: 30 -->
- [x] Create directory `docs_mkdocs/guides/` and move usage, profiling, dev <!-- id: 31 -->
- [x] Create directory `docs_mkdocs/reference/` (placeholder) <!-- id: 32 -->
- [x] Create `docs_mkdocs/SUMMARY.md` (if required by literate-nav setup) <!-- id: 33 -->
- [x] Update internal links in moved/existing markdown files <!-- id: 34 -->

## 4. Content Enhancement
- [x] Update `docs_mkdocs/index.md` with landing page cards/links <!-- id: 40 -->
- [x] **[SOTA]** Configure `mkdocs-git-revision-date-localized` (Last Updated dates) <!-- id: 42 -->
- [x] **[SOTA]** Configure `mkdocs-material` Social Cards (Open Graph images) <!-- id: 43 -->
- [x] **[Automation]** Create `docs_mkdocs/changelog.md` that uses `snippets` to pull from root `CHANGELOG.md` <!-- id: 44 -->
- [x] **[Science]** Add `CITATION.cff` and expose it in `docs_mkdocs/citation.md` <!-- id: 45 -->
- [x] Run `mkdocs build` to validate resolving links <!-- id: 41 -->

## 5. Verification
- [x] Run `mkdocs build --strict` <!-- id: 50 -->
- [x] Run `mike deploy --dry-run` <!-- id: 51 -->
- [x] Manual Check: MathJax rendering ($ \sigma^* $) <!-- id: 52 -->
- [x] Manual Check: Interactive Plotly figures <!-- id: 53 -->
- [ ] Manual Check: API reference hierarchy <!-- id: 54 -->
- [x] **[Polish]** Audit and optimize docstrings for `mkdocstrings` rendering <!-- id: 55 -->

## 6. Deployment Upgrade
- [x] Modify `.github/workflows/deploy_docs.yml` to use `mike deploy` <!-- id: 60 -->
