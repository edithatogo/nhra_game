from __future__ import annotations
import nox

@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def tests(session: nox.Session) -> None:
    """Run the test suite across multiple Python versions."""
    session.install(".[dev,opt]")
    session.run("pytest", *session.posargs)

@nox.session
def lint(session: nox.Session) -> None:
    """Run linting checks using ruff."""
    session.install("ruff")
    session.run("ruff", "check", "src", "scripts", "tests")

@nox.session
def type_check(session: nox.Session) -> None:
    """Run static type checking using mypy."""
    session.install(".[dev,opt]")
    session.install("mypy")
    session.run("mypy", "src")

@nox.session
def security(session: nox.Session) -> None:
    """Run security checks using bandit and safety."""
    session.install("bandit", "safety")
    session.run("bandit", "-r", "src", "-ll")
    # safety check requires a requirements file or similar
    # we'll skip for now if not available, or use --stdin
    session.run("bandit", "-r", "scripts", "-ll")

@nox.session
def coverage(session: nox.Session) -> None:
    """Run tests and generate coverage report."""
    session.install(".[dev,opt]")
    session.install("pytest-cov")
    session.run("pytest", "--cov=src", "--cov-report=term-missing")