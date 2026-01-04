# Contributing to NHRA Game Theory

Thank you for your interest in contributing! This project follows [pyOpenSci](https://www.pyopensci.org/) standards.

## Development Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/edithatogo/nhra_game.git
    cd nhra_game
    ```

2. **Install dependencies (using uv or pip):**

    ```bash
    pip install -e ".[dev]"
    # or
    uv pip install -e ".[dev]"
    ```

3. **Run tests:**

    ```bash
    nox
    # or
    pytest
    ```

## Pull Request Process

1. Create a feature branch.
2. Ensure `pytest` passes.
3. Ensure `ruff check .` passes.
4. Submit a PR with a description of changes.

## Code Style

- **Formatting:** We use `ruff format`.
- **Linting:** We use `ruff check` and `mypy`.
- **Testing:** We require 95% test coverage for new features.
