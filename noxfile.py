from __future__ import annotations

import os

import nox

nox.options.sessions = ["lint", "type"]

# Ensure PYTHONPATH includes src and root for script discovery
PYTHONPATH = {"PYTHONPATH": f"src{os.pathsep}."}


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def tests(session: nox.Session) -> None:
    """Run the test suite across multiple Python versions."""
    session.install("-e", ".[dev,opt]")
    session.install(
        "pytest",
        "pytest-mock",
        "hypothesis>=6.112.0",
        "importlib_metadata>=8.0.0",
        "jaxtyping",
        "flax",
        "jaxopt",
        "polars",
        "icontract",
    )
    session.run("pytest", *session.posargs, env=PYTHONPATH)


@nox.session
def lint(session: nox.Session) -> None:
    """Run linting checks using ruff."""
    session.install("ruff")
    session.run("ruff", "check", "src", "scripts", "tests")
    session.run("ruff", "format", "src", "scripts", "tests", "--check")


@nox.session(name="type")
def type_check(session: nox.Session) -> None:
    """Run static type checking using pyright."""
    session.install("-e", ".[dev,opt]")
    session.install("pyright")
    session.run("pyright", "src", env=PYTHONPATH)


@nox.session
def security(session: nox.Session) -> None:
    """Run security checks using bandit."""
    session.install("bandit")
    session.run("bandit", "-r", "src", "-ll")


@nox.session
def coverage(session: nox.Session) -> None:
    """Run tests and generate coverage report."""
    session.install("-e", ".[dev,opt]")
    session.install(
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "hypothesis>=6.112.0",
        "importlib_metadata>=8.0.0",
        "icontract",
        "beartype",
        "typeguard",
    )
    session.run(
        "pytest",
        "--cov=src",
        "--cov=scripts",
        "--cov-config=.coveragerc",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-report=html",
        env=PYTHONPATH,
    )


@nox.session
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.install(".[dev]")
    session.run("mkdocs", "build")


@nox.session
def bench(session: nox.Session) -> None:
    """Run benchmarks using pytest-benchmark."""
    session.install(".[dev]")
    session.run("pytest", "benchmarks", "--benchmark-only", *session.posargs, env=PYTHONPATH)


@nox.session
def asv_quick(session: nox.Session) -> None:
    """Run quick ASV benchmarks."""
    session.install("asv", "virtualenv")
    session.run("asv", "run", "--quick", "--show-stderr", external=True)


@nox.session(name="type_runtime")
def type_runtime(session: nox.Session) -> None:
    """Run tests with runtime type checking enabled."""
    session.install(".[dev,opt]")
    session.install("beartype", "typeguard")
    session.run("pytest", "tests/test_runtime_typecheck_smoke.py", env=PYTHONPATH)


@nox.session
def fuzz(session: nox.Session) -> None:
    """Run fuzz testing using Atheris."""
    session.install(".[dev]")
    session.install("atheris")
    # Expecting fuzz targets in tests/fuzz/
    session.run("python", "tests/fuzz/fuzz_target.py", *session.posargs, env=PYTHONPATH)


@nox.session
def load(session: nox.Session) -> None:
    """Run load testing using Locust."""
    session.install(".[dev]")
    session.install("locust")
    session.run(
        "locust", "-f", "tests/load/locustfile.py", "--headless", "--run-time", "1m", env=PYTHONPATH
    )
