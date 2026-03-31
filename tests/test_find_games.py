"""Tests the output of the `find_games` function."""

from brlib.find_games import _find_year_list, find_games


def test_teams():
    """Tests that the `teams` argument is handled correctly."""
    # reject alias
    assert len(find_games("KC1", "1957")) == 0
    # accept abbreviation that is also an alias
    assert len(find_games("KCA", "1957")) == 154
    # list, test case insensitivity
    assert len(find_games(["col", "BAL"], "1993")) == 324
    # "ALL"
    assert len(find_games(seasons="1903")) == 1122
    # skip Negro League teams, which lack box score coverage
    assert len(find_games("BBB")) == 0
    # era adjustment
    assert find_games("BAL", "1915", dates="825-826") == [
        "BAL191508251",
        "BAL191508252",
        "SLB191508250",
        "BAL191508260",
        "SLB191508260",
    ]


def test_seasons():
    """Tests that the `seasons` argument is handled correctly."""
    # range
    assert len(find_games("LAA", "2016-2017")) == 324
    # reversed range
    assert find_games(seasons="1929-1930") == find_games(seasons="1930-1929")
    # list
    assert len(find_games("WSN", ["2008", "2009-2010"])) == 485
    # "ALL"
    assert len(find_games("BLA")) == 274
    # invalid inputs
    assert len(find_games(seasons="year")) == 0
    assert len(find_games(seasons="1-9")) == 0  # triggers check for range arguments containing "-"
    # impossible team and season combo
    assert len(find_games("SEA", "1970")) == 0
    # before FIRST_GAMES_YEAR
    assert len(find_games("NAN", "1870")) == 0


def test_opponents():
    """Tests that the `opponents` argument is handled correctly."""
    # reject alias
    assert len(find_games(seasons="1957", opponents="KC1")) == 0
    # with a teams argument (the expected use case)
    assert find_games("SEA", "2025", "MIL") == [
        "SEA202507210",
        "SEA202507220",
        "SEA202507230",
    ]
    # should work without a teams argument as well (though this usage is dubious)
    assert find_games(seasons="1985", opponents="BOS") == find_games(teams="BOS", seasons="1985")
    # list, test case insensitivity
    assert find_games("LAD", "2020", opponents=["oak", "TEX"]) == [
        "TEX202008280",
        "TEX202008290",
        "TEX202008300",
        "LAD202009220",
        "LAD202009230",
        "LAD202009240",
    ]


def test_dates():
    """
    Tests that the `dates` argument (presumed valid) is handled correctly.
    Validation of dates is tested in test_inputs.py.
    """
    # single date
    assert find_games(seasons="2024", dates="321") == ["LAD202403210"]
    # range/reversed range
    assert find_games("BAL", "2015", dates="501-503") == find_games("BAL", "2015", dates="503-501")
    # list
    assert find_games("SEA", "2019", dates=["320-321", "328"]) == [
        "OAK201903200",
        "OAK201903210",
        "SEA201903280",
    ]


def test_home_away():
    """Tests that the `home_away` argument is handled correctly."""
    # away
    assert len(find_games("BOS", "2020", home_away="away")) == 29
    # home, test case insensitivity
    assert len(find_games("BOS", "2020", home_away="HOME")) == 31
    # invalid input
    assert len(find_games("BOS", "2020", home_away="both")) == 0


def test_game_type():
    """Tests that the `game_type` argument is handled correctly."""
    # reg
    assert len(find_games("SEA", "2022", game_type="reg")) == 162
    # post, test case insensitivity
    assert find_games("SEA", "2022", game_type="POST") == [
        "TOR202210070",
        "TOR202210080",
        "HOU202210110",
        "HOU202210130",
        "SEA202210150",
    ]
    # invalid input
    assert len(find_games("SEA", "2022", game_type="both")) == 0
    # season with no postseason
    assert len(find_games(seasons="1994", game_type="post")) == 0


def test_find_year_list():
    """Tests that the  `_find_year_list` method filters seasons based on other arguments."""
    # trim based on teams
    assert len(_find_year_list(["SEA"], ["1800-2016"], ["ALL"], "ALL")) == 40
    # trim based on teams + opponents
    assert len(_find_year_list(["SEA"], ["1800-2016"], ["TBD"], "ALL")) == 19
    # trim seasons without postseasons
    assert len(_find_year_list(["SEA"], ["1800-2016"], ["ALL"], "POST")) == 39
