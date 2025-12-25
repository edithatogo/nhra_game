from __future__ import annotations
import pytest
from beartype import beartype
from typeguard import typechecked

@beartype
def bear_function(x: int) -> int:
    return x

@typechecked
def guard_function(x: int) -> int:
    return x

def test_beartype_success():
    assert bear_function(1) == 1

def test_beartype_failure():
    # Beartype raises BeartypeCallHintViolation
    with pytest.raises(Exception): 
        bear_function("not an int") # type: ignore

def test_typeguard_success():
    assert guard_function(1) == 1

def test_typeguard_failure():
    # Typeguard raises TypeCheckError
    with pytest.raises(Exception):
        guard_function("not an int") # type: ignore
