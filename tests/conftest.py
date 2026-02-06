#!/usr/bin/env python3

"""Sets reusable objects for testing."""

import copy

import pandas as pd
import pytest

import brlib as br

br.options.add_no_hitters = False
br.options.update_team_names = False
br.options.update_venue_names = False


@pytest.fixture(scope="module")
def ap_filtered() -> pd.DataFrame:
    """The output of all_players filtered to a stable subset of retired players."""
    ap = br.all_players()
    ap = ap.loc[ap["Career End"] < 2019]
    return ap


@pytest.fixture(scope="session")
def games_list() -> list[br.Game]:
    """The Game outputs to be tested, before any public methods are run."""
    return br.get_games(
        [
            # ASG, tons of substitutions, tie, illegal(?) substitution with one position and split stats
            ("allstar", "2025", "0"),
            # Ohtani plays DH and SP
            ("ANA", "20230509", "0"),
            # combined no-hitter, WS game (matters for name)
            ("PHI", "20221102", "0"),
            # non-WS postseason game (matters for name), 18 innings
            ("SEA", "20221015", "0"),
            # SB cycle with multiple pitcher/catcher combos, a balk
            ("SEA", "20190527", "0"),
            # triple play, renamed venue, outfield assists
            ("SEA", "20180419", "0"),
            # illegal substitution with two positions and split stats, error by pitcher who did not hit
            ("BOS", "20170825", "0"),
            # perfect game, renamed venue
            ("SEA", "20120815", "0"),
            # unassisted triple play
            ("NYN", "20090823", "0"),
            # renamed venue, renamed team, relocated team
            ("FLO", "19940729", "0"),
            # player with 2 DPs, U L Washington tests parsing, 2 identical POCS, renamed venue, dh != 0
            ("SEA", "19780523", "1"),
            # ASG with dh != 0, 10 innings
            ("allstar", "1961", "1"),
            # dh = 3, 6 innings, 2 CGs with IP<9
            ("PIT", "19201002", "3"),
            # forfeited by team which finished with the lead, 4 innings, dh != 0
            ("SLN", "19071005", "1"),
            # both teams share names with later ones, limited stats (especially SB info), dh != 0
            ("MLA", "19010530", "1"),
        ]
    )


@pytest.fixture(scope="session")
def updated_games_list(games_list: list[br.Game]) -> list[br.Game]:
    """The Game outputs to be tested, after all public methods are run."""
    games_list_copy = copy.deepcopy(games_list)
    for game in games_list_copy:
        game.add_no_hitters()
        game.update_team_names()
        game.update_venue_names()
    return games_list_copy


@pytest.fixture(scope="session")
def players_list() -> list[br.Player]:
    """The Player outputs to be tested, before any public methods are run."""
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
        ]
    )


@pytest.fixture(scope="session")
def updated_players_list(players_list: list[br.Player]) -> list[br.Player]:
    """The Player outputs to be tested, after all public methods are run."""
    players_list_copy = copy.deepcopy(players_list)
    for player in players_list_copy:
        player.add_no_hitters()
        player.update_team_names()
    return players_list_copy


@pytest.fixture(scope="session")
def teams_list() -> list[br.Team]:
    """The Team outputs to be tested, before any public methods are run."""
    return br.get_teams(
        [
            # WS winner, renamed venue, CNH in regular and postseason
            ("HOU", "2022"),
            # team gold glove, pandemic season
            ("CHC", "2020"),
            # renamed team
            ("LAA", "2012"),
            # perfect game and CNH, renamed venue
            ("SEA", "2012"),
            # non-AL/NL pennant winner, players with multiple AS
            ("BEG", "1939"),
            # no player stats available
            ("COT", "1932"),
            # four managers, limited data, partial park factors
            ("BBB", "1924"),
            # team shares name with later one
            ("WSH", "1904"),
        ]
    )


@pytest.fixture(scope="session")
def updated_teams_list(teams_list: list[br.Team]) -> list[br.Team]:
    """The Team outputs to be tested, after all public methods are run."""
    teams_list_copy = copy.deepcopy(teams_list)
    for team in teams_list_copy:
        team.add_no_hitters()
        team.update_team_names()
        team.update_venue_names()
    return teams_list_copy
