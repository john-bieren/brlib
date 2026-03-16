"""Tests the attributes and methods of the `PlayerSet` class."""

import pytest
from get_expected import get_expected_df, get_expected_list

import brlib as br


def test_empty_rejection() -> None:
    """Tests that empty PlayerSets cannot be created."""
    with pytest.raises(ValueError):
        br.PlayerSet([])


def test_dunders(players_list: list[br.Player], player_set: br.PlayerSet) -> None:
    """Tests the outputs of dunder methods."""
    assert len(player_set) == len(players_list)
    assert str(player_set) == f"{len(players_list)} players"
    player_reprs = [repr(player) for player in players_list]
    assert (
        repr(player_set) == f'PlayerSet({", ".join(player_reprs)})'
    )  # single quotes for <3.12 support


def test_info(player_set: br.PlayerSet, updated_player_set: br.PlayerSet) -> None:
    """Tests the contents of the `info` DataFrame."""
    expected_df = get_expected_df("players", "info", False)
    compared = player_set.info.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("players", "info", True)
    compared = updated_player_set.info.compare(expected_df)
    assert compared.empty


def test_batting(player_set: br.PlayerSet) -> None:
    """Tests the contents of the `batting` DataFrame."""
    expected_df = get_expected_df("players", "batting", False)
    compared = player_set.batting.compare(expected_df)
    assert compared.empty


def test_pitching(player_set: br.PlayerSet, updated_player_set: br.PlayerSet) -> None:
    """Tests the contents of the `pitching` DataFrame."""
    expected_df = get_expected_df("players", "pitching", False)
    compared = player_set.pitching.compare(expected_df)
    assert compared.empty

    expected_df = get_expected_df("players", "pitching", True)
    compared = updated_player_set.pitching.compare(expected_df)
    assert compared.empty


def test_fielding(player_set: br.PlayerSet) -> None:
    """Tests the contents of the `fielding` DataFrame."""
    expected_df = get_expected_df("players", "fielding", False)
    compared = player_set.fielding.compare(expected_df)
    assert compared.empty


def test_bling(player_set: br.PlayerSet) -> None:
    """Tests the contents of the `bling` DataFrame."""
    expected_df = get_expected_df("players", "bling")
    compared = player_set.bling.compare(expected_df)
    assert compared.empty


def test_teams(player_set: br.PlayerSet) -> None:
    """Tests the contents of the `teams` list."""
    expected_list = get_expected_list("players", "teams")
    assert player_set.teams == expected_list
