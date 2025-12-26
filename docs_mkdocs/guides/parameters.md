# Parameter registry

All model inputs for `v9.Params` are enumerated in:

- `context/04_parameter_registry.csv`

## Rule
Each input must be either:
1) anchored to a **publicly retrievable source** (`evidence_type`: primary/secondary + URL), or
2) explicitly **justified** with a plausible range (`evidence_type`: assumed/calibrated/normalisation).

The registry is validated in CI:

```bash
python scripts/check_parameters_grounded.py
```

## Updating parameters
If you change `v9.Params`, regenerate the registry template then fill the evidence/jusification columns:

```bash
python scripts/make_parameter_registry_v20.py
```
