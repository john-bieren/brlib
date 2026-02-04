#!/usr/bin/env python3

"""Tests the output of the find_teams function."""

from brlib import find_teams


def test_teams():
    """Tests that teams argument is handled correctly."""
    # reject alias
    assert len(find_teams("KC1", "ALL")) == 0
    # list, test case insensitivity
    assert find_teams(["col", "BAL"], "2020") == [("COL", "2020"), ("BAL", "2020")]
    # "all"
    assert find_teams(seasons="1901") == [
        ("BLA", "1901"),
        ("BOS", "1901"),
        ("BRO", "1901"),
        ("BSN", "1901"),
        ("CHC", "1901"),
        ("CHW", "1901"),
        ("CIN", "1901"),
        ("CLE", "1901"),
        ("DET", "1901"),
        ("MLA", "1901"),
        ("NYG", "1901"),
        ("PHA", "1901"),
        ("PHI", "1901"),
        ("PIT", "1901"),
        ("STL", "1901"),
        ("WSH", "1901"),
    ]
    # segregation-era identifiers, further test case insensitivity
    assert find_teams(["BML", "WML"]) == find_teams("ALL")
    assert find_teams("bml", "1920") == [
        ("ABC", "1920"),
        ("CAG", "1920"),
        ("COG", "1920"),
        ("CSW", "1920"),
        ("DM", "1920"),
        ("DS", "1920"),
        ("KCM", "1920"),
        ("SLG", "1920"),
    ]
    assert find_teams("wml", "1920") == [
        ("BOS", "1920"),
        ("BRO", "1920"),
        ("BSN", "1920"),
        ("CHC", "1920"),
        ("CHW", "1920"),
        ("CIN", "1920"),
        ("CLE", "1920"),
        ("DET", "1920"),
        ("NYG", "1920"),
        ("NYY", "1920"),
        ("PHA", "1920"),
        ("PHI", "1920"),
        ("PIT", "1920"),
        ("SLB", "1920"),
        ("STL", "1920"),
        ("WSH", "1920"),
    ]


def test_seasons():
    """Tests that seasons argument is handled correctly."""
    # range
    assert find_teams("LAA", "2017-2019") == [("LAA", "2017"), ("LAA", "2018"), ("LAA", "2019")]
    # reversed range
    assert find_teams("LAA", "2019-2017") == [("LAA", "2017"), ("LAA", "2018"), ("LAA", "2019")]
    # list
    assert find_teams("CIN", ["2017", "2018-2019"]) == [
        ("CIN", "2017"),
        ("CIN", "2018"),
        ("CIN", "2019"),
    ]
    # "all"
    assert find_teams("BLA") == [("BLA", "1901"), ("BLA", "1902")]
