# Track Plan: Release Polish & Workflow Integrity

**Goal:** Achieve a "best practice" repository state with error-free workflows, live documentation, and PyPI-ready distribution artifacts.

## Phase 1: Local Workflow Validation & Hardening
- [ ] **Task 1.1: Local CI Simulation (act)**
  - [ ] Sub-task: Install and configure `act` locally.
  - [ ] Sub-task: Run each workflow in `/.github/workflows/` using `act` and resolve any environment or secret-related failures.
- [x] **Task 1.2: Workflow Permissions Audit** ab4cebd
  - [x] Sub-task: Update all GitHub Action YAML files to include explicit `permissions:` blocks at the job or workflow level, following the Principle of Least Privilege.
- [x] **Task 1.3: Quality Tools Audit & Sync** 24365c8
  - [x] Sub-task: Review current `ruff`, `mypy`, and `bandit` configurations for any gaps.
  - [x] Sub-task: Ensure the test suite maintains >95% success and broad coverage.
  - [x] Sub-task: Synchronize `.pre-commit-config.yaml` to match the strictest CI settings (versions and arguments).
  - [ ] Sub-task: Ensure the test suite maintains >95% success and broad coverage.
  - [ ] Sub-task: Synchronize `.pre-commit-config.yaml` to match the strictest CI settings (versions and arguments).
- [ ] **Task: Conductor - User Manual Verification 'Workflow Hardening' (Protocol in workflow.md)**

## Phase 2: Repository Health & Polish
- [x] **Task 2.1: File & Directory Reorganization** b850628
  - [x] Sub-task: Tidy the project root; move any stray artifacts into appropriate subdirectories.
  - [x] Sub-task: Verify presence and correctness of `LICENSE`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.
  - [ ] Sub-task: Verify presence and correctness of `LICENSE`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.
- [ ] **Task 2.2: GitHub Homepage & Metadata Update**
  - [ ] Sub-task: Update the repository "About" section with the live website URL, description, and relevant tags.
- [ ] **Task: Conductor - User Manual Verification 'Repository Health' (Protocol in workflow.md)**

## Phase 3: Documentation Excellence
- [ ] **Task 3.1: Best-Practice README.md Implementation**
  - [ ] Sub-task: Draft a clear project explanation and feature matrix.
  - [ ] Sub-task: Implement a script to auto-generate architecture diagrams (e.g., via `diagrams` or `graphviz`) from code.
  - [ ] Sub-task: Embed the generated diagrams and add live badges for CI status, Coverage, PyPI version, and License.
- [ ] **Task 3.2: Automated Link Checking**
  - [ ] Sub-task: Integrate `lychee` or `markdown-link-check` into the CI pipeline.
  - [ ] Sub-task: Resolve all broken internal/external links identified by the tool.
- [ ] **Task 3.3: MkDocs Deployment Verification**
  - [ ] Sub-task: Trigger and monitor the `deploy_docs.yml` workflow.
  - [ ] Sub-task: Confirm the site is live on GitHub Pages and all navigation works.
- [ ] **Task: Conductor - User Manual Verification 'Documentation Excellence' (Protocol in workflow.md)**

## Phase 4: Distribution & Release Integrity
- [ ] **Task 4.1: Security & Vulnerability Scanning**
  - [ ] Sub-task: Run `pip-audit` or `safety` to scan the locked dependency tree for known vulnerabilities.
- [ ] **Task 4.2: Distribution Artifact Verification**
  - [ ] Sub-task: Execute `poetry build` (or equivalent) to generate `sdist` and `wheel`.
  - [ ] Sub-task: Run `twine check dist/*` to verify PyPI rendering compatibility for the README.
- [ ] **Task 4.3: Final End-to-End Workflow Verification**
  - [ ] Sub-task: Perform a clean run of `just all` or the full `snakemake` pipeline.
  - [ ] Sub-task: Confirm all GitHub Actions show "Green" on the remote repository.
- [ ] **Task: Conductor - User Manual Verification 'Release Integrity' (Protocol in workflow.md)**
