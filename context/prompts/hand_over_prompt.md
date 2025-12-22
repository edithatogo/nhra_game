# Local handover prompt (for your own assistant)

You are maintaining the NHRA mechanism-model repo. Your tasks:
- Use `context/` as the single source of truth for intent, questions, and parameter provenance.
- Do not introduce non-public data.
- If you change any model parameter, update `context/04_parameter_registry.csv` and regenerate the context pack.

Run:
- `just test` (or `tox -q`) before committing.
- `just context` to regenerate context artefacts.
