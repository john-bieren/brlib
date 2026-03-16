"""Tests the typechecking utilities in typechecking.py."""

from collections import defaultdict
from typing import Any

import pytest

from brlib._helpers.typechecking import is_type, runtime_typecheck


@runtime_typecheck
def foo(bar: str) -> None:
    """Dummy function for testing the `runtime_typecheck` decorator."""
    pass


def test_runtime_typecheck() -> None:
    """Tests the `runtime_typecheck` decorator."""
    foo("bar")
    with pytest.raises(TypeError):
        foo(0)


def test_is_type() -> None:
    """Tests the outputs of the `is_type` function."""
    assert is_type("foo", Any)
    assert is_type("bar", str)
    assert not is_type("baz", int)
    assert not is_type(3.14, int)
    assert is_type(["foo", "bar", "baz"], list[str])
    assert not is_type(["foo", "bar", "baz"], tuple[str])
    assert not is_type(["foo", "bar", 3], list[str])
    assert not is_type(("foo", "bar", "baz"), tuple[str])
    assert is_type(("foo", "bar", "baz"), tuple[str, ...])
    assert is_type(("foo", "bar", "baz"), tuple[str, str, str])
    assert is_type({1, 2, 3}, set[int])
    assert not is_type({1, "2", 3}, set[int])
    assert is_type({1, "2", 3}, set[int | str])
    assert is_type({"a": 1, "b": 2, "c": 3}, dict[str, int])
    assert not is_type({"a": 1, "b": 2, "c": "3"}, dict[str, int])
    assert is_type(None, str | None)
    assert is_type(1, int | list[int])
    assert is_type([1, 2, 3], int | list[int])
    assert not is_type([1, 2, "3"], int | list[int])
    # a hint that is_type cannot handle
    with pytest.raises(TypeError):
        is_type(defaultdict(int), defaultdict[int, str])
