"""Sets reusable objects for testing."""

import copy
from pathlib import Path

import pandas as pd
import pytest
from test_cases import game_test_cases, player_test_cases, team_test_cases

import brlib as br
from brlib._helpers.abbreviations_manager import abv_mgr
from brlib._helpers.constants import CACHE_DIR

# standardize options configuration
br.options._preferences.clear()
br.options._changes.clear()
br.options.dev_alerts = True
br.options.print_pages = True

assert br.test_connection()


@pytest.fixture(scope="session", autouse=True)
def test_clear_cache() -> None:
    """
    Tests the clear_cache function by removing the abv_data cache file, and resets `abv_mgr` to
    re-load its data from the web and re-create its cache file for later testing. Must run before
    all other tests so that the presence or deletion of cached data doesn't affect test results.
    """
    br.options.clear_cache()
    # test clear_cache
    assert len([f for f in CACHE_DIR.iterdir() if f.is_file()]) == 0
    # reset abv_mgr and load data from the web
    abv_mgr.__init__()


@pytest.fixture(scope="module")
def ap_filtered() -> pd.DataFrame:
    """The output of `all_players`, filtered to a stable subset of retired players."""
    ap = br.all_players()
    ap = ap.loc[ap["Career End"] < 2019]
    return ap


@pytest.fixture(scope="session")
def expected_game_data() -> Path:
    """The directory containing the expected game data."""
    return Path(__file__).parent.resolve() / "expected" / "games"


@pytest.fixture(scope="session")
def games_list() -> list[br.Game]:
    """The `Game` outputs to be tested, before any public methods are run."""
    return br.get_games(game_test_cases, ignore_errors=False)


@pytest.fixture(scope="session")
def updated_games_list(games_list: list[br.Game]) -> list[br.Game]:
    """The `Game` outputs to be tested, after all public methods are run."""
    games_list_copy = copy.deepcopy(games_list)
    for game in games_list_copy:
        game.add_no_hitters()
        game.update_team_names()
        game.update_venue_names()
    return games_list_copy


@pytest.fixture(scope="session")
def game_set(games_list: list[br.Game]) -> br.GameSet:
    """A `GameSet` made from the contents of `games_list`, before any public methods are run."""
    return br.GameSet(games_list)


@pytest.fixture(scope="session")
def updated_game_set(game_set: br.GameSet) -> br.GameSet:
    """A `GameSet` made from the contents of `games_list`, after all public methods are run."""
    gs = copy.deepcopy(game_set)
    gs.add_no_hitters()
    gs.update_team_names()
    gs.update_venue_names()
    return gs


@pytest.fixture(scope="session")
def expected_player_data() -> Path:
    """The directory containing the expected player data."""
    return Path(__file__).parent.resolve() / "expected" / "players"


@pytest.fixture(scope="session")
def players_list() -> list[br.Player]:
    """The `Player` outputs to be tested, before any public methods are run."""
    return br.get_players(player_test_cases, ignore_errors=False)


@pytest.fixture(scope="session")
def updated_players_list(players_list: list[br.Player]) -> list[br.Player]:
    """The `Player` outputs to be tested, after all public methods are run."""
    players_list_copy = copy.deepcopy(players_list)
    for player in players_list_copy:
        player.add_no_hitters()
        player.update_team_names()
    return players_list_copy


@pytest.fixture(scope="session")
def player_set(players_list: list[br.Player]) -> br.PlayerSet:
    """A `PlayerSet` made from the contents of `players_list`, before any public methods are run."""
    return br.PlayerSet(players_list)


@pytest.fixture(scope="session")
def updated_player_set(player_set: br.PlayerSet) -> br.PlayerSet:
    """A `PlayerSet` made from the contents of `players_list`, after all public methods are run."""
    ps = copy.deepcopy(player_set)
    ps.add_no_hitters()
    ps.update_team_names()
    return ps


@pytest.fixture(scope="session")
def expected_team_data() -> Path:
    """The directory containing the expected team data."""
    return Path(__file__).parent.resolve() / "expected" / "teams"


@pytest.fixture(scope="session")
def teams_list() -> list[br.Team]:
    """The `Team` outputs to be tested, before any public methods are run."""
    return br.get_teams(team_test_cases, ignore_errors=False)


@pytest.fixture(scope="session")
def updated_teams_list(teams_list: list[br.Team]) -> list[br.Team]:
    """The `Team` outputs to be tested, after all public methods are run."""
    teams_list_copy = copy.deepcopy(teams_list)
    for team in teams_list_copy:
        team.add_no_hitters()
        team.update_team_names()
        team.update_venue_names()
    return teams_list_copy


@pytest.fixture(scope="session")
def team_set(teams_list: list[br.Team]) -> br.TeamSet:
    """A `TeamSet` made from the contents of `teams_list`, before any public methods are run."""
    return br.TeamSet(teams_list)


@pytest.fixture(scope="session")
def updated_team_set(team_set: br.TeamSet) -> br.TeamSet:
    """A `TeamSet` made from the contents of `teams_list`, after all public methods are run."""
    ts = copy.deepcopy(team_set)
    ts.add_no_hitters()
    ts.update_team_names()
    ts.update_venue_names()
    return ts
