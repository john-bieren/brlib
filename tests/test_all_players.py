"""Tests the output of the `all_players` function."""

import pandas as pd


def test_shape(ap_filtered: pd.DataFrame) -> None:
    """Tests that the filtered DataFrame has the right shape."""
    assert len(ap_filtered) == 20547
    assert ap_filtered.columns.tolist() == [
        "Player ID",
        "Name",
        "Career Start",
        "Career End",
        "Active",
    ]


def test_data(ap_filtered: pd.DataFrame) -> None:
    """Tests that the filtered DataFrame contains the expected data."""
    assert ap_filtered["Player ID"].iloc[:5].values.tolist() == [
        "aardsda01",
        "aaronha01",
        "aaronto01",
        "aasedo01",
        "abadan01",
    ]
    assert ap_filtered["Name"].iloc[:5].values.tolist() == [
        "David Aardsma",
        "Henry Aaron",
        "Tommie Aaron",
        "Don Aase",
        "Andy Abad",
    ]
    assert ap_filtered["Career Start"].iloc[:5].values.tolist() == [2004, 1954, 1962, 1977, 2001]
    assert ap_filtered["Career End"].iloc[:5].values.tolist() == [2015, 1976, 1971, 1990, 2006]
    assert ap_filtered["Active"].iloc[:5].values.tolist() == [False, False, False, False, False]
