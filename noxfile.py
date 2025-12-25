from __future__ import annotations

import nox

nox.options.sessions = ["lint", "type", "tests"]


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
    session.run("ruff", "format", "src", "scripts", "tests", "--check")


@nox.session(name="type")
def type_check(session: nox.Session) -> None:
    """Run static type checking using mypy and pyright."""
    session.install(".[dev,opt]")
    session.install("mypy", "pyright")
    session.run("mypy", "src")
    session.run("pyright", "src")


@nox.session
def security(session: nox.Session) -> None:
    """Run security checks using bandit."""
    session.install("bandit")
    session.run("bandit", "-r", "src", "-ll")


@nox.session
def coverage(session: nox.Session) -> None:
    """Run tests and generate coverage report."""
    session.install(".[dev,opt]")
    session.install("pytest-cov")
    session.run("pytest", "--cov=src", "--cov-report=term-missing", "--cov-report=xml", "--cov-report=html")


@nox.session
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.install(".[dev]")
    session.run("mkdocs", "build")


@nox.session
def bench(session: nox.Session) -> None:
    """Run benchmarks using pytest-benchmark."""
    session.install(".[dev]")
    # Expecting benchmarks in benchmarks/ or tests/benchmarks/
    session.run("pytest", "benchmarks", "--benchmark-only", *session.posargs)


@nox.session
def asv_quick(session: nox.Session) -> None:
    """Run quick ASV benchmarks."""
    session.install("asv", "virtualenv") 
    # asv requires virtualenv often
    session.run("asv", "run", "--quick", "--show-stderr", external=True)

@nox.session(name="type_runtime")
def type_runtime(session: nox.Session) -> None:
    """Run tests with runtime type checking enabled."""
    session.install(".[dev,opt]")
    session.install("beartype", "typeguard")
    session.run("pytest", "tests/test_runtime_typecheck_smoke.py")
