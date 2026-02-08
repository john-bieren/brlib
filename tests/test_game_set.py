#!/usr/bin/env python3

"""Tests the attributes and methods of the GameSet class."""

from pathlib import Path

import pandas as pd
from get_expected import get_expected_df, get_expected_list

import brlib as br


def test_info(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the info DataFrame."""
    expected_df = get_expected_df("games", "info", False)
    compared = game_set.info.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("games", "info", True)
    compared = updated_game_set.info.compare(expected_df)
    assert compared.empty


def test_batting(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the batting DataFrame."""
    expected_df = get_expected_df("games", "batting", False)
    compared = game_set.batting.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("games", "batting", True)
    compared = updated_game_set.batting.compare(expected_df)
    assert compared.empty


def test_pitching(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the pitching DataFrame."""
    expected_df = get_expected_df("games", "pitching", False)
    compared = game_set.pitching.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("games", "pitching", True)
    compared = updated_game_set.pitching.compare(expected_df)
    assert compared.empty


def test_fielding(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the fielding DataFrame."""
    expected_df = get_expected_df("games", "fielding", False)
    compared = game_set.fielding.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("games", "info", True)
    compared = updated_game_set.info.compare(expected_df)
    assert compared.empty


def test_team_info(game_set: br.GameSet, updated_game_set: br.GameSet) -> None:
    """Tests the contents of the team_info DataFrame."""
    expected_df = get_expected_df("games", "team_info", False)
    compared = game_set.team_info.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("games", "team_info", True)
    compared = updated_game_set.team_info.compare(expected_df)
    assert compared.empty


def test_ump_info(game_set: br.GameSet) -> None:
    """Tests the contents of the ump_info DataFrame."""
    expected_df = get_expected_df("games", "ump_info")
    compared = game_set.ump_info.compare(expected_df)
    assert compared.empty


def test_records(expected_game_data: Path, game_set: br.GameSet) -> None:
    """Tests the contents of the records DataFrame."""
    file = expected_game_data / "records.csv"
    expected_df = pd.read_csv(file)
    pd.testing.assert_frame_equal(game_set.records, expected_df)  # to handle win % precision


def test_players(game_set: br.GameSet) -> None:
    """Tests the contents of the players list."""
    expected_list = get_expected_list("games", "players")
    assert game_set.players == expected_list


def test_teams(game_set: br.GameSet) -> None:
    """Tests the contents of the teams list."""
    expected_list = get_expected_list("games", "teams")
    assert game_set.teams == expected_list
