#!/usr/bin/env python3

"""Tests the attributes and methods of the `TeamSet` class."""

from pathlib import Path

import pandas as pd
from get_expected import get_expected_df, get_expected_list

import brlib as br


def test_info(team_set: br.TeamSet, updated_team_set: br.TeamSet) -> None:
    """Tests the contents of the `info` DataFrame."""
    expected_df = get_expected_df("teams", "info", False)
    compared = team_set.info.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("teams", "info", True)
    compared = updated_team_set.info.compare(expected_df)
    assert compared.empty


def test_batting(team_set: br.TeamSet, updated_team_set: br.TeamSet) -> None:
    """Tests the contents of the `batting` DataFrame."""
    expected_df = get_expected_df("teams", "batting", False)
    compared = team_set.batting.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("teams", "batting", True)
    compared = updated_team_set.batting.compare(expected_df)
    assert compared.empty


def test_pitching(team_set: br.TeamSet, updated_team_set: br.TeamSet) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    expected_df = get_expected_df("teams", "pitching", False)
    compared = team_set.pitching.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("teams", "pitching", True)
    compared = updated_team_set.pitching.compare(expected_df)
    assert compared.empty


def test_fielding(team_set: br.TeamSet, updated_team_set: br.TeamSet) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    expected_df = get_expected_df("teams", "fielding", False)
    compared = team_set.fielding.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("teams", "info", True)
    compared = updated_team_set.info.compare(expected_df)
    assert compared.empty


def test_records(expected_team_data: Path, team_set: br.TeamSet) -> None:
    """Tests the contents of the `records` DataFrame."""
    file = expected_team_data / "records.csv"
    expected_df = pd.read_csv(file)
    pd.testing.assert_frame_equal(team_set.records, expected_df)  # to handle win % precision


def test_players(team_set: br.TeamSet) -> None:
    """Tests the contents of the `players` list."""
    expected_list = get_expected_list("teams", "players")
    assert team_set.players == expected_list
