# Development

## Quality tooling

- Ruff (lint + format)
- Pytest (+ Hypothesis properties)
- Mypy (strict)
- Pre-commit hooks
- Tox
- Dependabot

## Docker

```bash
docker build -t nhra .
docker run --rm -it -v "$PWD":/app nhra
```
