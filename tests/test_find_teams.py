"""Tests the output of the `find_teams` function."""

from brlib import find_teams


def test_teams():
    """Tests that the `teams` argument is handled correctly."""
    # reject alias
    assert len(find_teams("KC1", "ALL")) == 0
    # list, test case insensitivity
    assert find_teams(["col", "BAL"], "2020") == ["COL2020", "BAL2020"]
    # "all"
    assert find_teams(seasons="1901") == [
        "BLA1901",
        "BOS1901",
        "BRO1901",
        "BSN1901",
        "CHC1901",
        "CHW1901",
        "CIN1901",
        "CLE1901",
        "DET1901",
        "MLA1901",
        "NYG1901",
        "PHA1901",
        "PHI1901",
        "PIT1901",
        "STL1901",
        "WSH1901",
    ]
    # segregation-era identifiers, further test case insensitivity
    assert find_teams(["BML", "WML"]) == find_teams("ALL")
    assert find_teams("bml", "1920") == [
        "ABC1920",
        "CAG1920",
        "COG1920",
        "CSW1920",
        "DM1920",
        "DS1920",
        "KCM1920",
        "SLG1920",
    ]
    assert find_teams("wml", "1920") == [
        "BOS1920",
        "BRO1920",
        "BSN1920",
        "CHC1920",
        "CHW1920",
        "CIN1920",
        "CLE1920",
        "DET1920",
        "NYG1920",
        "NYY1920",
        "PHA1920",
        "PHI1920",
        "PIT1920",
        "SLB1920",
        "STL1920",
        "WSH1920",
    ]


def test_seasons():
    """Tests that the `seasons` argument is handled correctly."""
    # range
    assert find_teams("LAA", "2017-2019") == ["LAA2017", "LAA2018", "LAA2019"]
    # reversed range
    assert find_teams("LAA", "2019-2017") == ["LAA2017", "LAA2018", "LAA2019"]
    # list
    assert find_teams("CIN", ["2017", "2018-2019"]) == [
        "CIN2017",
        "CIN2018",
        "CIN2019",
    ]
    # "all"
    assert find_teams("BLA") == ["BLA1901", "BLA1902"]
