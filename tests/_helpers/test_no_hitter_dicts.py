#!/usr/bin/env python3

"""Tests the attributes of the NoHitterDicts singleton."""

import copy

import numpy as np

from brlib._helpers.no_hitter_dicts import nhd


def test_cache() -> None:
    """Tests that contents are the same when loaded from cache and the web."""
    # make sure the data has been loaded from the web by the CI runner
    # locally, you'll have to delete the cache file to replicate this behavior
    assert nhd.populate()

    expected_gi = copy.deepcopy(nhd.game_inh_dict)
    expected_gp = copy.deepcopy(nhd.game_pg_dict)
    expected_gc = copy.deepcopy(nhd.game_cnh_dict)
    expected_pi = copy.deepcopy(nhd.player_inh_dict)
    expected_pp = copy.deepcopy(nhd.player_pg_dict)
    expected_pc = copy.deepcopy(nhd.player_cnh_dict)
    expected_ti = copy.deepcopy(nhd.team_inh_dict)
    expected_tp = copy.deepcopy(nhd.team_pg_dict)
    expected_tc = copy.deepcopy(nhd.team_cnh_dict)

    # reset contents and load data from cache
    assert nhd._has_valid_cache
    nhd.__init__()
    assert nhd.populate()

    assert nhd.game_inh_dict == expected_gi
    assert nhd.game_pg_dict == expected_gp
    assert nhd.game_cnh_dict == expected_gc
    assert nhd.player_inh_dict == expected_pi
    assert nhd.player_pg_dict == expected_pp
    assert nhd.player_cnh_dict == expected_pc
    assert nhd.team_inh_dict == expected_ti
    assert nhd.team_pg_dict == expected_tp
    # some game ids are np.nan which does not equal itself, so numpy tooling is required
    np.testing.assert_equal(nhd.team_cnh_dict, expected_tc)

def test_game_dicts() -> None:
    """Tests the contents of the game dictionaries."""
    assert nhd.game_inh_dict["CIN202408020"] == "snellbl01"
    assert nhd.game_inh_dict["NYA195610080"] == "larsedo01"

    assert nhd.game_pg_dict.get("CIN202408020") is None
    assert nhd.game_pg_dict["NYA195610080"] == "larsedo01"

    assert nhd.game_cnh_dict.get("NYA195610080") is None
    assert nhd.game_cnh_dict["SEA201206080"] == [
        "millwke01", "pryorst01", "furbuch01", "luetglu01", "leagubr01", "wilheto01"
    ]
    assert nhd.game_cnh_dict["DET202307080"] == ["mannima02", "foleyja01", "langeal01"]

def test_player_dicts() -> None:
    """Tests the contents of the player dictionaries."""
    assert nhd.player_inh_dict.get("pressry01") is None
    assert nhd.player_inh_dict["hallaro01"] == [["2010", "PHI", "P"], ["2010", "PHI", "R"]]
    # checks that Negro League no-hitters aren't all marked as postseason
    assert nhd.player_inh_dict["dayle99"] == [["1946", "NE", "R"]]
    # ...except for Red Grier's no-hitter
    assert nhd.player_inh_dict["griercl01"] == [["1926", "AC", "P"]]

    assert nhd.player_pg_dict.get("paxtoja01") is None
    assert nhd.player_pg_dict["hernafe02"] == [["2012", "SEA", "R"]]
    assert nhd.player_pg_dict["larsedo01"] == [["1956", "NYY", "P"]]

    assert nhd.player_cnh_dict.get("dayle99") is None
    assert nhd.player_cnh_dict["sanchaa01"] == [["2019", "HOU", "R"]]
    assert nhd.player_cnh_dict["pressry01"] == [["2022", "HOU", "P"], ["2022", "HOU", "R"]]

def test_team_dicts() -> None:
    """Tests the contents of the team dictionaries."""
    assert nhd.team_inh_dict.get("LAD2018") is None
    # checks that pre-1901 no-hitters are marked as regular season
    assert nhd.team_inh_dict["BRO1886"] == [["terryad01", "R"]]
    assert nhd.team_inh_dict["PHI2010"] == [["hallaro01", "P"], ["hallaro01", "R"]]

    assert nhd.team_pg_dict.get("BRO1886") is None
    assert nhd.team_pg_dict["CHW2012"] == [["humbeph01", "R"]]
    assert nhd.team_pg_dict["NYY1956"] == [["larsedo01", "P"]]

    assert nhd.team_cnh_dict.get("SEA2018") is None
    assert nhd.team_cnh_dict["LAD2018"] == [
        ["buehlwa01", "R", "SDN201805040"], ["cingrto01", "R", "SDN201805040"],
        ["garciyi01", "R", "SDN201805040"], ["liberad01", "R", "SDN201805040"]
    ]
    assert nhd.team_cnh_dict["HOU2022"] == [
        ["javiecr01", "P", "PHI202211020"], ["abreubr01", "P", "PHI202211020"],
        ["montera01", "P", "PHI202211020"], ["pressry01", "P", "PHI202211020"],
        ["javiecr01", "R", "NYA202206250"], ["nerishe01", "R", "NYA202206250"],
        ["pressry01", "R", "NYA202206250"]
    ]
    # check game id value for combined no-hitters without a box score
    assert nhd.team_cnh_dict["KCM1923"] == [
        ["roganbu99", "R", np.nan], ["mendejo99", "R", np.nan]
    ]
