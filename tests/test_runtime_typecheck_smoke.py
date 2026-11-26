"""Tests for runtime typecheck smoke."""

from __future__ import annotations

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from typeguard import TypeCheckError, typechecked


@beartype
def bear_function(x: int) -> int:
    """Return an input subject to Beartype's runtime type check."""
    return x


@typechecked
def guard_function(x: int) -> int:
    """Return an input subject to Typeguard's runtime type check."""
    return x


def test_beartype_success():
    """Check beartype success."""
    assert bear_function(1) == 1


def test_beartype_failure():
    # Beartype raises BeartypeCallHintViolation
    """Check beartype failure."""
    with pytest.raises(BeartypeCallHintParamViolation):
        bear_function("not an int")  # type: ignore


def test_typeguard_success():
    """Check typeguard success."""
    assert guard_function(1) == 1


def test_typeguard_failure():
    # Typeguard raises TypeCheckError
    """Check typeguard failure."""
    with pytest.raises(TypeCheckError):
        guard_function("not an int")  # type: ignore
