# Repository Guidelines

This repository combines research artifacts with the latest working tree for the NHRA game-theory models. Use the
structure and commands below to stay consistent with the existing workflow.

## Project Structure & Module Organization

- Top level: reference assets, CSVs, images, and archived bundles. The active codebase lives in
  `nhra_game_theory_repo_v21_20251221/`.
- `nhra_game_theory_repo_v21_20251221/src/nhra_game_theory/` — core Python package.
- `nhra_game_theory_repo_v21_20251221/scripts/` — runnable pipelines and one-off analysis entrypoints.
- `nhra_game_theory_repo_v21_20251221/tests/` — unit and scenario tests.
- `nhra_game_theory_repo_v21_20251221/context/` — evidence registry, provenance, and context packs.
- `nhra_game_theory_repo_v21_20251221/diagrams/`, `reports/`, `outputs/` — generated visuals and reports.
- `nhra_game_theory_repo_v21_20251221/docs/` and `docs_mkdocs/` — documentation sources.

## Build, Test, and Development Commands

Run these from `nhra_game_theory_repo_v21_20251221/` unless noted.

- `python -m pip install -e ".[dev]"` — install development dependencies.
- `just run` — run the core pipeline, diagrams, and D3 output.
- `python scripts/run_v8_all.py` — build the v8 outputs into `outputs/v8/`.
- `just grounded` — validate that inputs are publicly sourced or justified.
- `pytest -q` or `just test` — run the test suite.
- `tox` — run ruff, mypy, and pytest in one pass.
- `mkdocs serve` or `just docs` — build docs locally.

## Coding Style & Naming Conventions

- Python, 4-space indentation, line length 100.
- Formatting with `ruff format`; linting with `ruff check`; type checks via `mypy --strict`.
- Naming: `snake_case` for modules/functions, `CapWords` for classes, `UPPER_SNAKE` for constants.
- Tests should be named `test_*.py` and live under `tests/`.

## Testing Guidelines

- Primary framework: `pytest` with `hypothesis` for property-based tests.
- Keep tests deterministic; store large outputs under `outputs/`, not in `tests/`.
- Before sharing results, run `pytest -q` or `tox`.

## Commit & Pull Request Guidelines

- Use concise, imperative commit subjects; include version tags when updating model iterations
  (e.g., `v21: refresh outputs`).
- Keep commits focused; avoid committing regenerated artifacts unless they are required deliverables.
- PRs should describe purpose, list reproducibility commands, and link to generated artifacts
  (e.g., `reports/` HTML or `outputs/` plots). Include screenshots for new visualizations.

## Security & Configuration Notes

- Validate sourcing with `python scripts/check_parameters_grounded.py` before release.
- Avoid committing sensitive data; prefer references in `context/` to external public sources.
