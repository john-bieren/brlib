#!/usr/bin/env python3

"""Tests the attributes and methods of the Team class."""

import json
from pathlib import Path

import pandas as pd

import brlib as br

teams_data = Path(__file__).parent.resolve() / "expected" / "teams"

def test_info(teams_list: list[br.Team], updated_teams_list: list[br.Team]) -> None:
    """Tests the contents of the info DataFrame."""
    for team in teams_list:
        file = teams_data / "original" / team.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = team.info.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = teams_data / "updated" / team.id / "info.csv"
        expected_df = pd.read_csv(file)
        compared = team.info.compare(expected_df)
        assert compared.empty

def test_batting(teams_list: list[br.Team], updated_teams_list: list[br.Team]) -> None:
    """Tests the contents of the batting DataFrame."""
    for team in teams_list:
        file = teams_data / "original" / team.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = team.batting.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = teams_data / "updated" / team.id / "batting.csv"
        expected_df = pd.read_csv(file)
        compared = team.batting.compare(expected_df)
        assert compared.empty

def test_pitching(teams_list: list[br.Team], updated_teams_list: list[br.Team]) -> None:
    """Tests the contents of the pitching DataFrame."""
    for team in teams_list:
        file = teams_data / "original" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = team.pitching.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = teams_data / "updated" / team.id / "pitching.csv"
        expected_df = pd.read_csv(file)
        compared = team.pitching.compare(expected_df)
        assert compared.empty

def test_fielding(teams_list: list[br.Team], updated_teams_list: list[br.Team]) -> None:
    """Tests the contents of the fielding DataFrame."""
    for team in teams_list:
        file = teams_data / "original" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = team.fielding.compare(expected_df)
        assert compared.empty

    for team in updated_teams_list:
        file = teams_data / "updated" / team.id / "fielding.csv"
        expected_df = pd.read_csv(file)
        compared = team.fielding.compare(expected_df)
        assert compared.empty

def test_players(teams_list: list[br.Team]) -> None:
    """Tests the contents of the players list."""
    for team in teams_list:
        file = teams_data / "original" / team.id / "players.json"
        expected_list = json.loads(file.read_bytes())
        assert team.players == expected_list
