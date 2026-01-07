#!/usr/bin/env python3

"""Tests attributes and methods of Game class."""

import json
from pathlib import Path

import pandas as pd


def test_info(games_list, updated_games_list):
    """Tests the contents of the info DataFrame."""
    for game in games_list:
        expected_df = get_expected("info.csv", game.id, updated=False)
        compared = game.info.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("info.csv", game.id, updated=True)
        compared = game.info.compare(expected_df)
        assert compared.empty

def test_batting(games_list, updated_games_list):
    """Tests the contents of the batting DataFrame."""
    for game in games_list:
        expected_df = get_expected("batting.csv", game.id, updated=False)
        compared = game.batting.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("batting.csv", game.id, updated=True)
        compared = game.batting.compare(expected_df)
        assert compared.empty

def test_pitching(games_list, updated_games_list):
    """Tests the contents of the pitching DataFrame."""
    for game in games_list:
        expected_df = get_expected("pitching.csv", game.id, updated=False)
        compared = game.pitching.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("pitching.csv", game.id, updated=True)
        compared = game.pitching.compare(expected_df)
        assert compared.empty

def test_fielding(games_list, updated_games_list):
    """Tests the contents of the fielding DataFrame."""
    for game in games_list:
        expected_df = get_expected("fielding.csv", game.id, updated=False)
        compared = game.fielding.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("fielding.csv", game.id, updated=True)
        compared = game.fielding.compare(expected_df)
        assert compared.empty

def test_linescore(games_list, updated_games_list):
    """Tests the contents of the linescore DataFrame."""
    for game in games_list:
        expected_df = get_expected("linescore.csv", game.id, updated=False)
        compared = game.linescore.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("linescore.csv", game.id, updated=True)
        compared = game.linescore.compare(expected_df)
        assert compared.empty

def test_team_info(games_list, updated_games_list):
    """Tests the contents of the team_info DataFrame."""
    for game in games_list:
        expected_df = get_expected("team_info.csv", game.id, updated=False)
        compared = game.team_info.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        expected_df = get_expected("team_info.csv", game.id, updated=True)
        compared = game.team_info.compare(expected_df)
        assert compared.empty

def test_ump_info(games_list):
    """Tests the contents of the ump_info DataFrame."""
    for game in games_list:
        expected_df = get_expected("ump_info.csv", game.id)
        compared = game.ump_info.compare(expected_df)
        assert compared.empty

def test_players(games_list):
    """Tests the contents of the players list."""
    for game in games_list:
        expected_list = get_expected("players.json", game.id)
        assert game.players == expected_list

def test_teams(games_list):
    """Tests the contents of the teams list."""
    for game in games_list:
        expected_list = get_expected("teams.json", game.id)
        assert game.teams == expected_list

def get_expected(
        file_name: str, game: str, updated: bool = False
        ) -> pd.DataFrame | list[str] | list[tuple[str, str]]:
    """
    Loads the expected game data from a file and returns it.
    `file_name` is the name of the desired file.
    `game` is the ID of the desired game.
    `updates` is whether to return the updated data, as opposed to the original data.
    """
    which_data = "updated" if updated else "original"
    expected_dir = Path(__file__).parent.resolve() / "expected" / "games" / which_data

    target = expected_dir / game / file_name
    if not target.exists() or not target.is_file():
        raise ValueError(f"cannot find {file_name}")

    if file_name.endswith(".csv"):
        return pd.read_csv(target)
    if file_name.endswith("json"):
        contents = json.loads(target.read_bytes())
        if file_name == "teams.json":
            return [tuple(t) for t in contents] # convert teams from lists to tuples
        return contents
    raise ValueError('invalid file extension given, must be ".csv" or ".json"')
