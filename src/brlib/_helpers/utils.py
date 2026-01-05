#!/usr/bin/env python3

"""Defines utility functions used throughout the codebase."""

import functools
from collections.abc import Callable
from datetime import datetime
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints

import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi.requests import Response
from tqdm import tqdm


def report_on_exc(resp_index: int = 1) -> Callable[..., Any]:
    """
    Prints the URL of a page which causes an exception.
    `resp_index` is the index of the decorated function's Response arugment which
    corresponds to the offending page.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            if not isinstance(args[resp_index], Response):
                raise TypeError(f"argument at resp_index must have type {repr(Response)}")
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                tqdm.write(f"exception thrown while processing {args[resp_index].url}")
                raise exc
        return wrapper
    return decorator

def runtime_typecheck(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Raises a TypeError at runtime if values passed to the function
    do not match its type annotations.
    """
    hints = get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # combine args and kwargs into one dictionary
        all_args = {**dict(zip(func.__code__.co_varnames, args)), **kwargs}

        for param, expected_type in hints.items():
            if param not in all_args:
                continue
            value = all_args[param]
            if not is_type(value, expected_type):
                raise TypeError(f"{param} argument must have type {expected_type}, not {type(value)}")
        return func(*args, **kwargs)
    return wrapper

def is_type(value: Any, expected_type: type) -> bool:
    """Checks whether `value` is an instance of `expected_type`, including parameterized generics."""
    if expected_type == Any:
        return True

    origin = get_origin(expected_type)
    if origin is None:
        return isinstance(value, expected_type)

    args = get_args(expected_type)
    if origin is UnionType:
        return any(is_type(value, arg) for arg in args)

    if not isinstance(value, origin):
        return False

    if origin is list:
        # args can only have length 1
        return all(is_type(item, *args) for item in value)

    if origin is tuple:
        # variable-length homogeneous tuple, e.g. Tuple[int, ...]
        if len(args) == 2 and args[1] is Ellipsis:
            return all(is_type(item, args[0]) for item in value)

        # fixed-length potentially heterogeneous tuple, e.g. Tuple[str, int, float]
        if len(value) != len(args):
            return False
        return all(is_type(item, typ) for item, typ in zip(value, args))

    if origin is dict:
        key_type, value_type = args
        return all(is_type(k, key_type) and is_type(v, value_type) for k, v in value.items())

    return isinstance(value, origin)

def str_between(string: str, start: str, end: str, anchor: str = "start") -> str:
    """
    Returns the substring of `string` which appears between `start` and `end`.
    `string` must contain `start` and `end`.

    If `anchor` == "start", the substring between the first occurrence of `start`
    and the first subsequent occurrence of `end` will be returned.

    If `anchor` == "end", the substring between the final occurrence of `end`
    and the final prior occurrence of `start` will be returned.
    """
    if start not in string:
        raise ValueError("start value not in string")
    if end not in string:
        raise ValueError("end value not in string")

    if anchor == "start":
        return string.split(start, maxsplit=1)[1].split(end, maxsplit=1)[0]
    if anchor == "end":
        return string.rsplit(end, maxsplit=1)[0].rsplit(start, maxsplit=1)[1]
    raise ValueError('anchor value must be "start" or "end"')

def str_remove(string: str, *substrings: str) -> str:
    """Removes instances of `substrings` from `string`."""
    for substring in substrings:
        string = string.replace(substring, "")
    return string

def reformat_date(string_date: str) -> str:
    """
    Converts `string_date` of "MM DD, YYYY" to "YY-MM-DD" for formatting consistency.
    If `string_date` does not match this format, and empty string will be returned.
    """
    try:
        date = datetime.strptime(string_date, "%B %d, %Y")
    except ValueError:
        # input doesn't match format, cannot be reformatted, and should be discarded
        return ""
    day, month = date.day, date.month
    month = f"0{month}" if month < 10 else month
    day = f"0{day}" if day < 10 else day
    return f"{date.year}-{month}-{day}"

def soup_from_comment(tag: Tag, only_if_table: bool = False) -> bs | Tag:
    """
    Returns contents from the first comment within `tag`.
    If `tag` does not include a table and `only_if_table` == True, returns `tag`.
    """
    try:
        comment_contents = str_between(tag.decode_contents(), "<!--", "-->").strip()
        # check that there is a table in the comment
        if not only_if_table or "<col><col><col>" in comment_contents:
            return bs(comment_contents, "lxml")
        return tag
    except (IndexError, ValueError):
        return tag

def scrape_player_ids(table: bs) -> list[str]:
    """Returns player IDs from anchor tags in `table`."""
    player_id_column = []
    for row in table.find_all("a", href=True):
        link = row.get("href", "")
        if "players" not in link:
            continue
        # [11:21] includes the period in ".shtml" so rsplit works if ID is short or has a period
        player_id = link[11:21]
        player_id_column.append(player_id.rsplit(".", maxsplit=1)[0])
    return player_id_column

def change_innings_notation(innings: str) -> str:
    """Replaces box score notation with the correct numerical value so that they sum correctly."""
    # could be np.nan, leave that alone since the column will eventually be converted to floats
    if not isinstance(innings, str):
        return innings
    return innings.replace(".1", ".333334").replace(".2", ".666667")

def convert_numeric_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Converts the numeric columns of `df` to correct dtypes using pd.to_numeric."""
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise")
        except (ValueError, TypeError):
            # skip columns which cannot be converted
            pass
    return df
