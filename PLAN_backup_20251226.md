# Plan: Systematic MkDocs Documentation Improvement

## 1. Goal
Significantly improve the quality, maintainability, and depth of the documentation by leveraging `docstrings`, automating API reference generation, and utilizing advanced `mkdocs-material` features.

## 2. Analysis
- **Current State**: Flat `docs_mkdocs/` directory, manual `api.md`, minimal `mkdocs.yml` config.
- **Missing Features**: Deep API reference, structured navigation, wealthy markdown features (tabs, annotations, diagrams).
- **Missing Plugins**: `mkdocs-literate-nav` (for structure), `mkdocs-section-index` (for UX), `mkdocs-gen-files` (configured for recursion).

## 3. Implementation Steps

### 3.1. Infrastructure & Dependencies
- [ ] **Add Plugins**: Add `mkdocs-literate-nav`, `mkdocs-section-index`, `mkdocs-jupyter`, and `mike` (for versioning) to `pyproject.toml`.
- [ ] **Update Configuration**: Overhaul `mkdocs.yml` to:
    -   **Versioning**: Configure `mike` to serve multiple versions (e.g., `latest`, `v26.0`) allowing users to browse docs for older releases.
    -   **Scientific Typesetting**: Enable `pymdownx.arithmatex` (MathJax) for proper rendering of game theory equations (e.g., $ \sigma^* $).
    -   **Code Integrity**: Enable `pymdownx.snippets` to embed code directly from `src/` into docs, preventing examples from becoming stale.
    -   **Material Features**: Navigation tabs, search, code copying, dark mode toggle, admonitions, pymdownx extensions (highlight, superfences, details, tabbed).
    -   Configure `mkdocstrings` with `python` handler options (show source, headings).
    -   Configure `nav` to use `literate-nav` (file-system based navigation).

### 3.2. Automated API Reference (`gen-files`)
- [ ] **Create Script**: Implement `scripts/gen_ref_pages.py`.
    -   Recursively walk `src/nhra_game_theory/`.
    -   Generate ephemeral `.md` files for each module containing `::: path.to.module`.
    -   Map these files into the `reference/` section of the documentation.

### 3.3. Structural Reorganization
- [ ] **Refactor `docs_mkdocs/`**:
    -   Move project docs (requirements, design, tasks) to `docs_mkdocs/project/`.
    -   Move guides (usage, profiling, dev) to `docs_mkdocs/guides/`.
    -   Create `docs_mkdocs/reference/` (virtual, populated by script).
    -   Create `docs_mkdocs/SUMMARY.md` (if using literate-nav) or rely on implicit folder structure.

### 3.4. Content Enhancement
- [ ] **Landing Page**: Improve `index.md` to be a proper entry point with cards/links to sections.
- [ ] **Validation**: Run `mkdocs build` to ensure all docstrings are resolving and links are valid.

## 4. Verification
- **Automated**:
    - `mkdocs build --strict` (treat warnings as errors).
    - `mike deploy --dry-run` to test versioning logic.
- **Manual**:
    - Verify MathJax renders complex equations correctly.
    - Verify Plotly/HTML interactive figures render within the Material theme boundaries.
    - Inspect the generated site locally to verify the API reference hierarchy and docstring rendering.

## 5. Deployment Upgrade
- [ ] **Workflow Update**: Modify `deploy_docs.yml` to use `mike deploy` instead of `mkdocs gh-deploy`. This preserves history.
