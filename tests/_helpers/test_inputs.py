"""Tests the functions in inputs.py."""

from brlib._helpers.inputs import (
    validate_date_list,
    validate_game_list,
    validate_player_list,
    validate_team_list,
)


def test_validate_game_list() -> None:
    """Tests the outputs of the `validate_game_list` function."""
    test_list = [
        # convert ID to uppercase
        "sea201506210",
        # accept aliases
        "LAN202410310",
        # accept, correct missing aliases
        "NYY202503290",
        # reject impossible team/season combination
        "SEP197004010",
        # reject incorrect abbreviation
        "MLB199410200",
        # reject teams without box scores
        "KCM192308050",
        # reject invalid date
        "TOR2018050800",
        # reject invalid doubleheader
        "BRO192107044",
        # reject game before 1901
        "PHI190007120",
        # reject game in future
        "OAK209903210",
        # accept digit in team abbreviation
        "NY1195409290",
        # reject malformed ASG input
        "allstar196007130",
        # reject ASG before 1933
        "1932-allstar-game",
        # reject ASG in future
        "2099-allstar-game",
        # reject ASG in year when it was canceled
        "2020-allstar-game",
        # convert ASG ID to lowercase
        "1962-ALLSTAR-GAME-2",
    ]
    assert validate_game_list(test_list) == [
        "SEA201506210",
        "LAN202410310",
        "NYA202503290",
        "NY1195409290",
        "1962-allstar-game-2",
    ]


def test_validate_player_list() -> None:
    """Tests the outputs of the `validate_player_list` function."""
    test_list = [
        # convert ID to lowercase
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
        "invalid0",
    ]
    assert validate_player_list(test_list) == [
        "hernafe02",
        "ohse01",
        "colli05",
        "washiu_01",
        "burnea.01",
        "o'neipa01",
    ]


def test_validate_team_list() -> None:
    """Tests the outputs of the `validate_team_list` function."""
    test_list = [
        # convert ID to uppercase
        "cin2017",
        # reject impossible team/season combination
        "SEP1970",
        # reject invalid abbreviation
        "NO2019",
        # reject invalid season
        "PIT123456",
        # reject season before 1871
        "TRO1870",
        # reject season in future
        "MAR2099",
        # reject missing season for team
        "HG1934",
        # accept digit in team abbreviation
        "SL31939",
    ]
    assert validate_team_list(test_list) == ["CIN2017", "SL31939"]


def test_validate_date_list() -> None:
    """Tests the outputs of the `validate_date_list` function."""
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
        "0529-0527",
    ]
    assert validate_date_list(test_list) == [
        "0704",
        "803",
        "0321-401",
        "930-1001",
        "1007-1008",
        "0527-0529",
    ]

    # overwrite all inputs if "ALL" is included
    assert validate_date_list(test_list + ["ALL"]) == ["ALL"]
