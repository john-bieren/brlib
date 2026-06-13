"""Tests the attributes and methods of the `Team` class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br
from brlib._helpers.constants import (
    TEAM_BATTING_DTYPES,
    TEAM_BLING_DTYPES,
    TEAM_FIELDING_DTYPES,
    TEAM_INFO_DTYPES,
    TEAM_PITCHING_DTYPES,
)


def test_info(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `info` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "info.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_INFO_DTYPES)
        pd.testing.assert_frame_equal(team.info, expected_df)  # to handle win % precision

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "info.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_INFO_DTYPES)
        pd.testing.assert_frame_equal(team.info, expected_df)  # to handle win % precision


def test_bling(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `bling` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "bling.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_BLING_DTYPES)
        pd.testing.assert_frame_equal(team.bling, expected_df)  # to handle win % precision

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "bling.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_BLING_DTYPES)
        pd.testing.assert_frame_equal(team.bling, expected_df)  # to handle win % precision


def test_batting(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `batting` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "batting.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_BATTING_DTYPES)
        pd.testing.assert_frame_equal(team.batting, expected_df)

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "batting.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_BATTING_DTYPES)
        pd.testing.assert_frame_equal(team.batting, expected_df)


def test_pitching(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_PITCHING_DTYPES)
        pd.testing.assert_frame_equal(team.pitching, expected_df)

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_PITCHING_DTYPES)
        pd.testing.assert_frame_equal(team.pitching, expected_df)


def test_fielding(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_FIELDING_DTYPES)
        pd.testing.assert_frame_equal(team.fielding, expected_df)

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file, dtype=TEAM_FIELDING_DTYPES)
        pd.testing.assert_frame_equal(team.fielding, expected_df)


def test_players(expected_team_data: Path, teams_list: list[br.Team]) -> None:
    """Tests the contents of the `players` list."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "players.json"
        expected_list = json.loads(file.read_bytes())
        assert team.players == expected_list
