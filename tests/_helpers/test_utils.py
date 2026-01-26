#!/usr/bin/env python3

"""Tests some of the functions in utils.py; the rest are covered by the end-to-end tests."""

from typing import Any

import pytest

from brlib._helpers.utils import (clean_spaces, is_type, reformat_date,
                                  str_between, str_remove)


def test_is_type() -> None:
    """Tests the outputs of the is_type function."""
    assert is_type("foo", Any)
    assert is_type("bar", str)
    assert not is_type("baz", int)
    assert not is_type(3.14, int)
    assert is_type(["foo", "bar", "baz"], list[str])
    assert not is_type(["foo", "bar", 3], list[str])
    assert is_type(("foo", "bar", "baz"), tuple[str, str, str])
    assert not is_type(("foo", "bar", "baz"), tuple[str])
    assert is_type({"a": 1, "b": 2, "c": 3}, dict[str, int])
    assert not is_type({"a": 1, "b": 2, "c": "3"}, dict[str, int])
    assert is_type(1, int | list[int])
    assert is_type([1, 2, 3], int | list[int])
    assert not is_type([1, 2, "3"], int | list[int])

def test_str_between() -> None:
    """Tests the outputs of the str_between function."""
    assert str_between("first.second.last", ".", ".") == "second"
    assert str_between("first.second.last", "first", "last") == ".second."
    assert str_between("a/b.c.d/e", "/", ".", anchor="start") == "b"
    assert str_between("a/b.c.d/e", ".", "/", anchor="start") == "c.d"
    assert str_between("a/b.c.d/e", ".", "/", anchor="end") == "d"
    with pytest.raises(ValueError):
        str_between("foo", "/", "o")
    with pytest.raises(ValueError):
        str_between("foo", "f", "/")
    with pytest.raises(ValueError):
        str_between("foo", "o", "f", anchor="last")

def test_str_remove() -> None:
    """Tests the outputs of the str_remove function."""
    assert str_remove("f.o.o.b.a.z", ".") == "foobaz"
    assert str_remove("f.o/o,b`a'z", ".", "/", ",", "`", "'") == "foobaz"

def test_clean_spaces() -> None:
    """Tests the outputs of the clean_spaces function."""
    assert clean_spaces(" foo bar baz ") == "foo bar baz"
    assert clean_spaces("     foo         bar  baz  ") == "foo bar baz"

def test_reformat_date() -> None:
    """Tests the outputs of the reformat_date function."""
    assert reformat_date("October 02, 2022") == "2022-10-02"
    assert reformat_date("May 2, 2018") == "2018-05-02"
    assert reformat_date("2020") == ""
