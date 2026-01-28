#!/usr/bin/env python3

"""Tests the functions in inputs.py."""

from brlib._helpers.inputs import (validate_date_list, validate_game_list,
                                   validate_player_list, validate_team_list)


def test_validate_game_list() -> None:
    """Tests the outputs of the validate_game_list function."""
    test_list = [
        # convert team to uppercase
        ("sea", "20150621", "0"),
        # accept aliases
        ("LAN", "20241031", "0"),
        # accept, correct missing aliases
        ("NYY", "20250329", "0"),
        # reject impossible team/season combination
        ("SEP", "19700401", "0"),
        # reject incorrect abbreviation
        ("MLB", "19941020", "0"),
        # reject teams without box scores
        ("KCM", "19230805", "0"),
        # reject invalid date
        ("TOR", "201805080", "0"),
        # reject invalid doubleheader
        ("BRO", "19210704", "4"),
        # reject game before 1901
        ("PHI", "19000712", "0"),
        # reject game in future
        ("OAK", "20990321", "0"),
        # reject malformed ASG input
        ("allstar", "19600713", "0"),
        # reject ASG before 1933
        ("allstar", "1932", "0"),
        # reject ASG in future
        ("allstar", "2099", "0"),
        # reject ASG in year where it was cancelled
        ("allstar", "2020", "0"),
        # convert allstar to uppercase
        ("allstar", "1960", "2")
    ]
    assert validate_game_list(test_list) == [
        ("SEA", "20150621", "0"),
        ("LAN", "20241031", "0"),
        ("NYA", "20250329", "0"),
        ("ALLSTAR", "1960", "2")
    ]

def test_validate_player_list() -> None:
    """Tests the outputs of the validate_player_list function."""
    test_list = [
        # convert to lowercase
        "HERNAFE02",
        # several weird but valid player IDs
        "ohse01",
        "colli05",
        "washiu_01",
        "burnea.01",
        "o'neipa01",
        # too many letters
        "playerid01",
        # too many digits
        "players101",
        # not enough digits
        "invalid0"
    ]
    assert validate_player_list(test_list) == [
        "hernafe02",
        "ohse01",
        "colli05",
        "washiu_01",
        "burnea.01",
        "o'neipa01"
    ]

def test_validate_team_list() -> None:
    """Tests the outputs of the validate_team_list function."""
    test_list = [
        # convert to uppercase
        ("cin", "2017"),
        # reject impossible team/season combination
        ("SEP", "1970"),
        # reject invalid abbreviation
        ("NO", "2019"),
        # reject invalid season
        ("PIT", "123456"),
        # reject season before 1871
        ("TRO", "1870"),
        # reject season in future
        ("MAR", "2099"),
        # reject missing season for team
        ("HG", "1934")
    ]
    assert validate_team_list(test_list) == [
        ("CIN", "2017")
    ]

def test_validate_date_list() -> None:
    """Tests the outputs of the validate_date_list function."""
    test_list = [
        # approve with leading 0
        "0704",
        # approve without leading 0
        "803",
        # reject too short
        "07",
        # reject too long
        "20150615",
        # ranges with 3 and 4 digit bounds
        "0321-401",
        "930-1001",
        # range with full 8 digits
        "1007-1008",
        # reverse backwards range
        "0529-0527"
    ]
    assert validate_date_list(test_list) == [
        "0704",
        "803",
        "0321-401",
        "930-1001",
        "1007-1008",
        "0527-0529"
    ]

    # overwrite all inputs if "ALL" is included
    assert validate_date_list(test_list + ["ALL"]) == ["ALL"]
