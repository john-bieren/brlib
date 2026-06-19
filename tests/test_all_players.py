"""Tests the output of the `all_players` function."""

import pandas as pd

from brlib._helpers.constants import ALL_PLAYERS_DTYPES


def test_shape(ap_filtered: pd.DataFrame) -> None:
    """Tests that the filtered DataFrame has the right shape."""
    assert len(ap_filtered) == 20705
    assert ap_filtered.columns.tolist() == [
        "Player",
        "Career Start",
        "Career End",
        "Active",
        "Player ID",
    ]


def test_data(ap_filtered: pd.DataFrame) -> None:
    """Tests that the filtered DataFrame contains the expected data."""
    for col, expected_dtype in ALL_PLAYERS_DTYPES.items():
        assert ap_filtered[col].dtype == expected_dtype
    assert ap_filtered["Player ID"].iloc[:5].tolist() == [
        "aardsda01",
        "aaronha01",
        "aaronto01",
        "aasedo01",
        "abadan01",
    ]
    assert ap_filtered["Player"].iloc[:5].tolist() == [
        "David Aardsma",
        "Henry Aaron",
        "Tommie Aaron",
        "Don Aase",
        "Andy Abad",
    ]
    assert ap_filtered["Career Start"].iloc[:5].tolist() == [2004, 1954, 1962, 1977, 2001]
    assert ap_filtered["Career End"].iloc[:5].tolist() == [2015, 1976, 1971, 1990, 2006]
    assert ap_filtered["Active"].iloc[:5].tolist() == [False, False, False, False, False]
