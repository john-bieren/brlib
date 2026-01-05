#!/usr/bin/env python3

"""Tests contents of the NoHitterDicts singleton."""

from brlib._helpers.no_hitter_dicts import nhd


def test_nhd():
    assert not nhd._populated
    requested_data = nhd._get()
    assert not requested_data.empty
    nhd._generate_dicts(requested_data)
    suite()

    # re-load data from cache and test again
    nhd.game_inh_dict, nhd.game_pg_dict, nhd.game_cnh_dict = ({} for _ in range(3))
    nhd.player_inh_dict, nhd.player_pg_dict, nhd.player_cnh_dict = ({} for _ in range(3))
    nhd.team_inh_dict, nhd.team_pg_dict, nhd.team_cnh_dict = ({} for _ in range(3))
    assert nhd._has_valid_cache
    cached_data = nhd._load()
    assert not cached_data.empty
    nhd._generate_dicts(cached_data)
    suite()

def suite():
    game_dicts()
    player_dicts()
    team_dicts()

def game_dicts():
    assert nhd.game_inh_dict["CIN202408020"] == "snellbl01"
    assert nhd.game_inh_dict["NYA195610080"] == "larsedo01"

    assert nhd.game_pg_dict.get("CIN202408020") is None
    assert nhd.game_pg_dict["NYA195610080"] == "larsedo01"

    assert nhd.game_cnh_dict.get("NYA195610080") is None
    assert nhd.game_cnh_dict["SEA201206080"] == [
        "millwke01", "pryorst01", "furbuch01", "luetglu01", "leagubr01", "wilheto01"
    ]
    assert nhd.game_cnh_dict["DET202307080"] == ["mannima02", "foleyja01", "langeal01"]

def player_dicts():
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

def team_dicts():
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
