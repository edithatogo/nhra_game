# Development

## Quality tooling
- Ruff (lint + format)
- Pytest (+ Hypothesis properties)
- Mypy (strict)
- Pre-commit hooks
- Tox
- Dependabot

## Performance Profiling (Scalene)
We use [Scalene](https://github.com/plasma-umass/scalene) for high-performance CPU, GPU, and memory profiling.

### Profiling the Backtest Loop
To profile the recursive backtest:
```bash
LOGFIRE_SEND_TO_LOGFIRE=false PYTHONPATH=src scalene --cli --profile-all scripts/validation/recursive_backtest.py
```

Scalene will provide a detailed breakdown of time spent in `v9.py` (simulations) vs `validation.py` (logic).
