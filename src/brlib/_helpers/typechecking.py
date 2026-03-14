"""Defines typechecking utilities used throughout the codebase."""

import functools
import typing
from collections.abc import Callable
from types import UnionType
from typing import Any


def runtime_typecheck(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Raises a `TypeError` at runtime if the arguments passed to the function do not match its type
    annotations.
    """
    hints = typing.get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Internal wrapper for the typechecking logic."""
        # combine args and kwargs into one dictionary
        # noinspection PyUnresolvedReferences TODO
        all_args = {**dict(zip(func.__code__.co_varnames, args)), **kwargs}

        for param, expected_type in hints.items():
            if param not in all_args:
                continue
            value = all_args[param]
            if not is_type(value, expected_type):
                raise TypeError(
                    f"{param} argument must have type {expected_type}, not {type(value)}"
                )
        return func(*args, **kwargs)

    return wrapper


def is_type(value: Any, expected_type: type | UnionType) -> bool:
    """
    Checks whether `value` is an instance of `expected_type`, including parameterized generics.
    """
    if expected_type == Any:
        return True

    origin = typing.get_origin(expected_type)
    if origin is None:
        return isinstance(value, expected_type)

    args = typing.get_args(expected_type)
    if origin is UnionType or origin is typing.Union:  # typing.Union for 3.10 support
        return any(is_type(value, arg) for arg in args)

    if not isinstance(value, origin):
        return False

    if origin is list:
        value: list
        # args can only have length 1
        return all(is_type(item, *args) for item in value)

    if origin is tuple:
        value: tuple
        # variable-length homogeneous tuple, e.g. Tuple[int, ...]
        if len(args) == 2 and args[1] is Ellipsis:
            return all(is_type(item, args[0]) for item in value)

        # fixed-length potentially heterogeneous tuple, e.g. Tuple[str, int, float]
        if len(value) != len(args):
            return False
        return all(is_type(item, typ) for item, typ in zip(value, args))

    if origin is dict:
        value: dict
        key_type, value_type = args
        return all(is_type(k, key_type) and is_type(v, value_type) for k, v in value.items())

    return isinstance(value, origin)
