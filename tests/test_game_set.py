"""Tests the attributes and methods of the `GameSet` class."""

from pathlib import Path

import pandas as pd
import pytest
from get_expected import get_expected_df, get_expected_list

import brlib as br
from brlib._helpers.constants import (
    GAME_BATTING_DTYPES,
    GAME_FIELDING_DTYPES,
    GAME_INFO_DTYPES,
    GAME_PITCHING_DTYPES,
    GAME_TEAM_INFO_DTYPES,
    GAME_UMP_INFO_DTYPES,
    RECORDS_DTYPES,
)


def test_empty_rejection() -> None:
    """Tests that empty GameSets cannot be created."""
    with pytest.raises(ValueError):
        br.GameSet([])


def test_dunders(games_list: list[br.Game], game_set: br.GameSet) -> None:
    """Tests the outputs of dunder methods."""
    assert len(game_set) == len(games_list)
    assert str(game_set) == f"{len(games_list)} games"
    game_reprs = [repr(game) for game in games_list]
    assert repr(game_set) == f'GameSet({", ".join(game_reprs)})'  # single quotes for <3.12 support


def test_info(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the `info` DataFrame."""
    expected_df = get_expected_df("games", "info", False, GAME_INFO_DTYPES)
    pd.testing.assert_frame_equal(game_set.info, expected_df)

    expected_df = get_expected_df("games", "info", True, GAME_INFO_DTYPES)
    pd.testing.assert_frame_equal(updated_game_set.info, expected_df)


def test_batting(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the `batting` DataFrame."""
    expected_df = get_expected_df("games", "batting", False, GAME_BATTING_DTYPES)
    pd.testing.assert_frame_equal(game_set.batting, expected_df)


def test_pitching(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    expected_df = get_expected_df("games", "pitching", False, GAME_PITCHING_DTYPES)
    pd.testing.assert_frame_equal(game_set.pitching, expected_df)

    expected_df = get_expected_df("games", "pitching", True, GAME_PITCHING_DTYPES)
    pd.testing.assert_frame_equal(updated_game_set.pitching, expected_df)


def test_fielding(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    expected_df = get_expected_df("games", "fielding", False, GAME_FIELDING_DTYPES)
    pd.testing.assert_frame_equal(game_set.fielding, expected_df)


def test_team_info(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the `team_info` DataFrame."""
    expected_df = get_expected_df("games", "team_info", False, GAME_TEAM_INFO_DTYPES)
    pd.testing.assert_frame_equal(game_set.team_info, expected_df)

    expected_df = get_expected_df("games", "team_info", True, GAME_TEAM_INFO_DTYPES)
    pd.testing.assert_frame_equal(updated_game_set.team_info, expected_df)


def test_ump_info(game_set: br.GameSet) -> None:
    """Tests the contents of the `ump_info` DataFrame."""
    expected_df = get_expected_df("games", "ump_info", False, GAME_UMP_INFO_DTYPES)
    pd.testing.assert_frame_equal(game_set.ump_info, expected_df)


def test_records(expected_game_data: Path, game_set: br.GameSet) -> None:
    """Tests the contents of the `records` DataFrame."""
    file = expected_game_data / "records.csv"
    expected_df = pd.read_csv(file, dtype=RECORDS_DTYPES)
    pd.testing.assert_frame_equal(game_set.records, expected_df)


def test_players(game_set: br.GameSet) -> None:
    """Tests the contents of the `players` list."""
    expected_list = get_expected_list("games", "players")
    assert game_set.players == expected_list


def test_teams(game_set: br.GameSet) -> None:
    """Tests the contents of the `teams` list."""
    expected_list = get_expected_list("games", "teams")
    assert game_set.teams == expected_list
