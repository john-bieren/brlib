"""Sets reusable objects for testing."""

import copy
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

import brlib as br
from brlib._helpers.abbreviations_manager import abv_mgr
from brlib._helpers.constants import CACHE_DIR

br.options.add_no_hitters = False
br.options.update_team_names = False
br.options.update_venue_names = False


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
    return br.get_games(
        [
            # ASG with dh != 0, 10 innings
            "1961-allstar-game-1",
            # ASG, essentially a forfeit, illegal(?) substitution with 1 position and split stats
            "2025-allstar-game",
            # Ohtani plays DH and SP
            "ANA202305090",
            # illegal substitution with 2 positions and split stats, error by pitcher who didn't hit
            "BOS201708250",
            # renamed team, wind "in unknown direction", Colt .45s table id special case
            "CHN196207291",
            # renamed venue, renamed team, relocated team
            "FLO199407290",
            # both teams share names with later ones, limited stats (especially SB info), dh != 0
            "MLA190105301",
            # unassisted triple play
            "NYN200908230",
            # combined no-hitter, WS game (matters for name)
            "PHI202211020",
            # dh = 3, 6 innings, 2 CGs with IP<9
            "PIT192010023",
            # player with 2 DP, U L Washington tests parsing, 2 identical POCS, renamed venue, dh != 0
            "SEA197805231",
            # renamed team, renamed venue, game played at away team's venue
            "SEA201106250",
            # perfect game, renamed venue
            "SEA201208150",
            # triple play, renamed venue, outfield assists
            "SEA201804190",
            # SB cycle with multiple pitcher/catcher combos, a balk
            "SEA201905270",
            # non-WS postseason game (matters for name), 18 innings
            "SEA202210150",
            # forfeited by team which finished with the lead, 4 innings, dh != 0
            "SLN190710051",
        ],
        ignore_errors=False,
    )


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
def updated_game_set(games_list: list[br.Game]) -> br.GameSet:
    """A `GameSet` made from the contents of `games_list`, after all public methods are run."""
    gs = br.GameSet(games_list)
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
    return br.get_players(
        [
            # tons of relatives (including a manager), two missing seasons
            "aloumo01",
            # lots of missing data (especially advanced pitching)
            "bendech01",
            # very little information
            "colli05",
            # born and died in Canada (tests province parsing)
            "cormirh01",
            # multiple AS in certain seasons, catcher (more fielding stats)
            "gibsojo99",
            # regular season and postseason no-hitter
            "hallaro01",
            # lots of postseason stats
            "jacksre01",
            # only played in postseason, drafted multiple times
            "kigerma01",
            # multiple combined no-hitters (in one season, even), multiple high schools
            "pressry01",
            # catcher (with modern fielding stats), renamed draft team
            "vogtst01",
        ],
        ignore_errors=False,
    )


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
def updated_player_set(players_list: list[br.Player]) -> br.PlayerSet:
    """A `PlayerSet` made from the contents of `players_list`, after all public methods are run."""
    ps = br.PlayerSet(players_list)
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
    return br.get_teams(
        [
            # four managers, limited data, partial park factors
            "BBB1924",
            # non-AL/NL pennant winner, players with multiple AS
            "BEG1939",
            # team gold glove, pandemic season
            "CHC2020",
            # no player stats available
            "COT1932",
            # WS winner, renamed venue, CNH in regular and postseason
            "HOU2022",
            # renamed team
            "LAA2012",
            # same franchise ID as WSH1904 but different team ID (tests TeamSet.records)
            "MIN2019",
            # perfect game and CNH, renamed venue
            "SEA2012",
            # team shares name with later one
            "WSH1904",
        ],
        ignore_errors=False,
    )


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
def updated_team_set(teams_list: list[br.Team]) -> br.TeamSet:
    """A `TeamSet` made from the contents of `teams_list`, after all public methods are run."""
    ts = br.TeamSet(teams_list)
    ts.add_no_hitters()
    ts.update_team_names()
    ts.update_venue_names()
    return ts
