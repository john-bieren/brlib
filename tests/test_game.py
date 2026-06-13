"""Tests the attributes and methods of the `Game` class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br
from brlib._helpers.constants import (
    GAME_BATTING_DTYPES,
    GAME_FIELDING_DTYPES,
    GAME_INFO_DTYPES,
    GAME_PITCHING_DTYPES,
    GAME_TEAM_INFO_DTYPES,
    GAME_UMP_INFO_DTYPES,
)


def test_info(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `info` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "info.csv"
        expected_df = pd.read_csv(file, dtype=GAME_INFO_DTYPES)
        pd.testing.assert_frame_equal(game.info, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "info.csv"
        expected_df = pd.read_csv(file, dtype=GAME_INFO_DTYPES)
        pd.testing.assert_frame_equal(game.info, expected_df)


def test_batting(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `batting` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "batting.csv"
        expected_df = pd.read_csv(file, dtype=GAME_BATTING_DTYPES)
        pd.testing.assert_frame_equal(game.batting, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "batting.csv"
        expected_df = pd.read_csv(file, dtype=GAME_BATTING_DTYPES)
        pd.testing.assert_frame_equal(game.batting, expected_df)


def test_pitching(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "pitching.csv"
        expected_df = pd.read_csv(file, dtype=GAME_PITCHING_DTYPES)
        pd.testing.assert_frame_equal(game.pitching, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "pitching.csv"
        expected_df = pd.read_csv(file, dtype=GAME_PITCHING_DTYPES)
        pd.testing.assert_frame_equal(game.pitching, expected_df)


def test_fielding(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "fielding.csv"
        expected_df = pd.read_csv(file, dtype=GAME_FIELDING_DTYPES)
        pd.testing.assert_frame_equal(game.fielding, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "fielding.csv"
        expected_df = pd.read_csv(file, dtype=GAME_FIELDING_DTYPES)
        pd.testing.assert_frame_equal(game.fielding, expected_df)


def test_linescore(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `linescore` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "linescore.csv"
        expected_df = pd.read_csv(file, dtype_backend="numpy_nullable")
        expected_df["Team"] = expected_df["Team"].astype("str")
        pd.testing.assert_frame_equal(game.linescore, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "linescore.csv"
        expected_df = pd.read_csv(file, dtype_backend="numpy_nullable")
        expected_df["Team"] = expected_df["Team"].astype("str")
        pd.testing.assert_frame_equal(game.linescore, expected_df)


def test_team_info(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the `team_info` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "team_info.csv"
        expected_df = pd.read_csv(file, dtype=GAME_TEAM_INFO_DTYPES)
        pd.testing.assert_frame_equal(game.team_info, expected_df)

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "team_info.csv"
        expected_df = pd.read_csv(file, dtype=GAME_TEAM_INFO_DTYPES)
        pd.testing.assert_frame_equal(game.team_info, expected_df)


def test_ump_info(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the `ump_info` DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "ump_info.csv"
        expected_df = pd.read_csv(file, dtype=GAME_UMP_INFO_DTYPES)
        pd.testing.assert_frame_equal(game.ump_info, expected_df)


def test_players(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the `players` list."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "players.json"
        expected_list = json.loads(file.read_bytes())
        assert game.players == expected_list


def test_teams(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the `teams` list."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "teams.json"
        expected_list = json.loads(file.read_bytes())
        assert game.teams == expected_list
