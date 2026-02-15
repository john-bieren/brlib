"""Defines get_expected functions."""

import json
from pathlib import Path

import pandas as pd


def get_expected_df(category_dir: str, target_table: str, updated: bool = False) -> pd.DataFrame:
    """
    Returns the expected value of a Set's `target_table` attribute by combining the relevant
    contents of `category_dir`. If `updated` is `True`, the returned value is for the updated Set.
    """
    updated_original = "updated" if updated else "original"
    cases_dir = Path(__file__).parent / "expected" / category_dir / updated_original

    tables = []
    case_dirs = sorted(cases_dir.iterdir())
    for case_dir in case_dirs:
        data_file = case_dir / f"{target_table}.csv"
        df = pd.read_csv(data_file)
        if not df.empty:
            tables.append(df)

    expected_df = pd.concat(tables, ignore_index=True)
    return expected_df


def get_expected_list(category_dir: str, target_list: str) -> list[str] | list[tuple[str, str]]:
    """
    Returns the expected value of a Set's `target_list` attribute by combining the relevant
    contents of `category_dir`.
    """
    cases_dir = Path(__file__).parent / "expected" / category_dir / "original"

    expected_list = []
    case_dirs = sorted(cases_dir.iterdir())
    for case_dir in case_dirs:
        data_file = case_dir / f"{target_list}.json"
        expected_list.extend(json.loads(data_file.read_bytes()))

    if target_list == "teams":
        expected_list = [tuple(t) for t in expected_list]
    expected_list = list(dict.fromkeys(expected_list))
    return expected_list
