#!/usr/bin/env python3

"""Tests the attributes and methods of the `Team` class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br


def test_info(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `info` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = team.info.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = team.info.compare(expected_df)
        assert compared.empty


def test_batting(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `batting` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = team.batting.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = team.batting.compare(expected_df)
        assert compared.empty


def test_pitching(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = team.pitching.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = team.pitching.compare(expected_df)
        assert compared.empty


def test_fielding(
    expected_team_data: Path,
    teams_list: list[br.Team],
    updated_teams_list: list[br.Team],
) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = team.fielding.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = expected_team_data / "updated" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = team.fielding.compare(expected_df)
        assert compared.empty


def test_players(expected_team_data: Path, teams_list: list[br.Team]) -> None:
    """Tests the contents of the `players` list."""
    for team in teams_list:
        file = expected_team_data / "original" / team.id / "players.json"
        expected_list = json.loads(file.read_bytes())
        assert team.players == expected_list
