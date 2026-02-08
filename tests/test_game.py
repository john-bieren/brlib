#!/usr/bin/env python3

"""Tests the attributes and methods of the Game class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br


def test_info(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the info DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = game.info.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = game.info.compare(expected_df)
        assert compared.empty


def test_batting(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the batting DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = game.batting.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = game.batting.compare(expected_df)
        assert compared.empty


def test_pitching(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the pitching DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = game.pitching.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = game.pitching.compare(expected_df)
        assert compared.empty


def test_fielding(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the fielding DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = game.fielding.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = game.fielding.compare(expected_df)
        assert compared.empty


def test_linescore(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the linescore DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "linescore.csv"
        expected_df = pd.read_csv(file)
        compared = game.linescore.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "linescore.csv"
        expected_df = pd.read_csv(file)
        compared = game.linescore.compare(expected_df)
        assert compared.empty


def test_team_info(
    expected_game_data: Path,
    games_list: list[br.Game],
    updated_games_list: list[br.Game],
) -> None:
    """Tests the contents of the team_info DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "team_info.csv"
        expected_df = pd.read_csv(file)
        compared = game.team_info.compare(expected_df)
        assert compared.empty

    for game in updated_games_list:
        file = expected_game_data / "updated" / game.id / "team_info.csv"
        expected_df = pd.read_csv(file)
        compared = game.team_info.compare(expected_df)
        assert compared.empty


def test_ump_info(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the ump_info DataFrame."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "ump_info.csv"
        expected_df = pd.read_csv(file)
        compared = game.ump_info.compare(expected_df)
        assert compared.empty


def test_players(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the players list."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "players.json"
        expected_list = json.loads(file.read_bytes())
        assert game.players == expected_list


def test_teams(expected_game_data: Path, games_list: list[br.Game]) -> None:
    """Tests the contents of the teams list."""
    for game in games_list:
        file = expected_game_data / "original" / game.id / "teams.json"
        expected_list = json.loads(file.read_bytes())
        expected_list = [tuple(t) for t in expected_list]
        assert game.teams == expected_list
