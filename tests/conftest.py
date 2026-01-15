#!/usr/bin/env python3

"""Sets reusable objects for testing."""

import copy

import pytest

import brlib as br

br.options.add_no_hitters = False

@pytest.fixture(scope="session")
def games_list() -> list[br.Game]:
    """The Game outputs to be tested, before any public methods are run."""
    return [
        # ASG, tons of subtitutions, tie, illegal(?) substitution with one position and split stats
        br.Game("allstar", "2025", "0"),
        # combined no-hitter, WS game (matters for name)
        br.Game("PHI", "20221102", "0"),
        # non-WS postseason game (matters for name), 18 innings
        br.Game("SEA", "20221015", "0"),
        # SB cycle with multiple pitcher/catcher combos, a balk
        br.Game("SEA", "20190527", "0"),
        # triple play, renamed venue, outfield assists
        br.Game("SEA", "20180419", "0"),
        # illegal substitution with two positions and split stats, error by pitcher who did not hit
        br.Game("BOS", "20170825", "0"),
        # perfect game, renamed venue
        br.Game("SEA", "20120815", "0"),
        # unassisted triple play
        br.Game("NYN", "20090823", "0"),
        # renamed venue, renamed team, relocated team
        br.Game("FLO", "19940729", "0"),
        # player with 2 DPs, U L Washington tests parsing, 2 identical POCS, renamed venue, dh != 0
        br.Game("SEA", "19780523", "1"),
        # ASG with dh != 0, 10 innings
        br.Game("allstar", "1961", "1"),
        # dh = 3, 6 innings, 2 CGs with IP<9
        br.Game("PIT", "19201002", "3"),
        # both teams share names with later ones, limited stats (especially SB info), dh != 0
        br.Game("MLA", "19010530", "1")
    ]

@pytest.fixture(scope="session")
def updated_games_list(games_list: list[br.Game]) -> list[br.Game]:
    """The Game outputs to be tested, after all public methods are run."""
    games_list_copy = copy.deepcopy(games_list)
    for game in games_list_copy:
        game.add_no_hitters()
        game.update_team_names()
        game.update_venue_name()
    return games_list_copy

@pytest.fixture(scope="session")
def players_list() -> list[br.Player]:
    """The Player outputs to be tested, before any public methods are run."""
    return [
        # tons of relatives (including a manager), two missing seasons
        br.Player("aloumo01"),
        # lots of missing data (especially advanced pitching)
        br.Player("bendech01"),
        # very little information
        br.Player("colli05"),
        # multiple AS in certain seasons, catcher (more fielding stats)
        br.Player("gibsojo99"),
        # regular season and postseason no-hitter
        br.Player("hallaro01"),
        # lots of postseason stats
        br.Player("jacksre01"),
        # only played in postseason, drafted multiple times
        br.Player("kigerma01"),
        # multiple combined no-hitters (in one season, even), multiple high schools
        br.Player("pressry01")
    ]

@pytest.fixture(scope="session")
def updated_players_list(players_list: list[br.Player]) -> list[br.Player]:
    """The Player outputs to be tested, after all public methods are run."""
    players_list_copy = copy.deepcopy(players_list)
    for player in players_list_copy:
        player.add_no_hitters()
        player.update_team_name()
    return players_list_copy

@pytest.fixture(scope="session")
def teams_list() -> list[br.Team]:
    """The Team outputs to be tested, before any public methods are run."""
    return [
        # WS winner, renamed ballpark, CNH in regular and postseason
        br.Team("HOU", "2022"),
        # team gold glove, pandemic season
        br.Team("CHC", "2020"),
        # renamed team
        br.Team("LAA", "2012"),
        # perfect game and CNH, renamed ballpark
        br.Team("SEA", "2012"),
        # non-AL/NL pennant winner, players with multiple AS
        br.Team("BEG", "1939"),
        # four managers, limited data, partial park factors
        br.Team("BBB", "1924"),
        # team shares name with later one
        br.Team("WSH", "1904")
    ]

@pytest.fixture(scope="session")
def updated_teams_list(teams_list: list[br.Team]) -> list[br.Team]:
    """The Team outputs to be tested, after all public methods are run."""
    teams_list_copy = copy.deepcopy(teams_list)
    for team in teams_list_copy:
        team.add_no_hitters()
    return teams_list_copy
