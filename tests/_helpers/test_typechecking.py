"""Tests the typechecking utilities in typechecking.py."""

from typing import Any

from brlib._helpers.typechecking import is_type


def test_is_type() -> None:
    """Tests the outputs of the `is_type` function."""
    assert is_type("foo", Any)
    assert is_type("bar", str)
    assert not is_type("baz", int)
    assert not is_type(3.14, int)
    assert is_type(["1", 1], list)
    assert not is_type(["1", 1], tuple)
    assert is_type(["foo", "bar", "baz"], list[str])
    assert not is_type(["foo", "bar", 3], list[str])
    assert is_type(("foo", "bar", "baz"), tuple[str, ...])
    assert is_type(("foo", "bar", "baz"), tuple[str, str, str])
    assert not is_type(("foo", "bar", "baz"), tuple[str])
    assert is_type({"a": 1, "b": 2, "c": 3}, dict[str, int])
    assert not is_type({"a": 1, "b": 2, "c": "3"}, dict[str, int])
    assert is_type(None, str | None)
    assert is_type(1, int | list[int])
    assert is_type([1, 2, 3], int | list[int])
    assert not is_type([1, 2, "3"], int | list[int])
