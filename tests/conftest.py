#!/usr/bin/env python3

"""Sets reusable objects for testing."""

import copy

import pytest

import brlib as br


@pytest.fixture(scope="session")
def games_list():
    """The Game outputs to be tested, before any public methods are run."""
    br.options.add_no_hitters = False
    return [
        # renamed venue, renamed team, relocated team
        br.Game("FLO", "19940729", "0"),
        # player with 2 DPs, U L Washington tests parsing, 2 identical POCS, renamed venue, dh != 0
        br.Game("SEA", "19780523", "1"),
        # SB cycle with multiple pitcher/catcher combos, a balk
        br.Game("SEA", "20190527", "0"),
        # triple play, renamed venue, outfield assists
        br.Game("SEA", "20180419", "0"),
        # unassisted triple play
        br.Game("NYN", "20090823", "0"),
        # perfect game, renamed venue
        br.Game("SEA", "20120815", "0"),
        # combined no-hitter, WS game (matters for name)
        br.Game("PHI", "20221102", "0"),
        # non-WS postseason game (matters for name), 18 innings
        br.Game("SEA", "20221015", "0"),
        # tripleheader, 6 innings, 2 CGs with IP<9
        br.Game("PIT", "19201002", "3"),
        # both teams share names with later ones, limited stats (especially SB info)
        br.Game("MLA", "19010530", "1"),
        # illegal substitution with two positions and split stats, error by pitcher who did not hit
        br.Game("BOS", "20170825", "0"),
        # ASG, tons of subtitutions, tie, illegal(?) substitution with one position and split stats
        br.Game("allstar", "2025", "0"),
        # ASG with dh != 0, 10 innings
        br.Game("allstar", "1961", "1")
    ]

@pytest.fixture(scope="session")
def updated_games_list(games_list):
    """The Game outputs to be tested, after all public methods are run."""
    games_list_copy = copy.deepcopy(games_list)
    for game in games_list_copy:
        game.add_no_hitters()
        game.update_team_names()
        game.update_venue_name()
    return games_list_copy
