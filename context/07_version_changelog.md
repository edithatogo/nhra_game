# Version changelog

## v20 (2025-12-21)

- Added **local context system** (`context/`) including project intent, policy questions, model overview, abbreviations, and reporting checklist guidance.
- Added **parameter registry** (`context/04_parameter_registry.csv`) and automated checks to ensure every input is either sourced to a public reference or explicitly justified with a plausible range.
- Added automated **context pack builder** for local workflows (`scripts/build_context_pack.py`).
- CI updated to run context + parameter checks.

## Prior versions

See repository `reports/` and `outputs/` folders for earlier numbered versions (v8–v19) and incremental model changes.
