#!/usr/bin/env python3

"""Tests the attributes and methods of the Player class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br


def test_info(
    expected_player_data: Path,
    players_list: list[br.Player],
    updated_players_list: list[br.Player],
) -> None:
    """Tests the contents of the info DataFrame."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = player.info.compare(expected_df)
        assert compared.empty

    for player in updated_players_list:
        file = expected_player_data / "updated" / player.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = player.info.compare(expected_df)
        assert compared.empty


def test_batting(expected_player_data: Path, players_list: list[br.Player]) -> None:
    """Tests the contents of the batting DataFrame."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = player.batting.compare(expected_df)
        assert compared.empty


def test_pitching(
    expected_player_data: Path,
    players_list: list[br.Player],
    updated_players_list: list[br.Player],
) -> None:
    """Tests the contents of the pitching DataFrame."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = player.pitching.compare(expected_df)
        assert compared.empty

    for player in updated_players_list:
        file = expected_player_data / "updated" / player.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = player.pitching.compare(expected_df)
        assert compared.empty


def test_fielding(expected_player_data: Path, players_list: list[br.Player]) -> None:
    """Tests the contents of the fielding DataFrame."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = player.fielding.compare(expected_df)
        assert compared.empty


def test_bling(expected_player_data: Path, players_list: list[br.Player]) -> None:
    """Tests the contents of the bling DataFrame."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "bling.csv"
        expected_df = pd.read_csv(file)
        compared = player.bling.compare(expected_df)
        assert compared.empty


def test_relatives(expected_player_data: Path, players_list: list[br.Player]) -> None:
    """Tests the contents of the relatives dictionary."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "relatives.json"
        expected_dict = json.loads(file.read_bytes())
        assert player.relatives == expected_dict


def test_teams(expected_player_data: Path, players_list: list[br.Player]) -> None:
    """Tests the contents of the teams list."""
    for player in players_list:
        file = expected_player_data / "original" / player.id / "teams.json"
        expected_list = json.loads(file.read_bytes())
        expected_list = [tuple(t) for t in expected_list]
        assert player.teams == expected_list
