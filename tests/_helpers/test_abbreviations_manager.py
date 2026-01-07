#!/usr/bin/env python3

"""Tests methods of the AbbreviationsManager singleton."""

import pandas as pd

from brlib._helpers.abbreviations_manager import abv_man


def test_abv_man():
    """Tests methods of the AbbreviationsManager singleton when loaded from cache and the web."""
    # when run locally, the data will be from cache if the file isn't manually removed beforehand
    # changing this would cause the CI runner to request the data twice
    suite()

    # re-load data from cache and test again
    abv_man.df = pd.DataFrame()
    assert abv_man._has_valid_cache
    abv_man._load()
    suite()

def suite():
    """Runs the tests for all the methods."""
    correct_abvs()
    franchise_abv()
    all_team_abvs()
    to_alias()
    to_regular()

def correct_abvs():
    """Tests the outputs of the correct_abvs method."""
    assert abv_man.correct_abvs("OAK", 2025, era_adjustment=True) == ["ATH"]
    assert abv_man.correct_abvs("OAK", 2025, era_adjustment=False) == []
    assert abv_man.correct_abvs("BAL", 1915, era_adjustment=True) == ["SLB", "BAL"]
    assert abv_man.correct_abvs("BAL", 1915, era_adjustment=False) == ["BAL"]
    assert abv_man.correct_abvs("LAA", 1977, era_adjustment=False) == ["CAL"]
    assert abv_man.correct_abvs("LAA", 1907, era_adjustment=False) == []
    assert abv_man.correct_abvs("SER", 2025, era_adjustment=False) == []

def franchise_abv():
    """Tests the outputs of the franchise_abv method."""
    assert abv_man.franchise_abv("ATH", 1876) == "ATH"
    assert abv_man.franchise_abv("BAL", 1915) == "BLT"
    assert abv_man.franchise_abv("OAK", 2025) == ""
    assert abv_man.franchise_abv("SER", 2025) == ""

def all_team_abvs():
    """Tests the outputs of the all_team_abvs method."""
    assert abv_man.all_team_abvs("ATH", 2025) == ["ATH", "KCA", "OAK", "PHA"]
    assert abv_man.all_team_abvs("OAK", 2025) == []
    assert abv_man.all_team_abvs("SER", 2025) == []

def to_alias():
    """Tests the outputs of the to_alias method."""
    assert abv_man.to_alias("SEA", 2025) == "SEA"
    assert abv_man.to_alias("KCA", 1963) == "KC1"
    assert abv_man.to_alias("PBS", 2025) == "PBS"
    assert abv_man.to_alias("SER", 2025) == "SER"

def to_regular():
    """Tests the outputs of the to_regular method."""
    assert abv_man.to_regular("SEA", 2025) == "SEA"
    assert abv_man.to_regular("KCA", 1999) == "KCR"
    assert abv_man.to_regular("KC1", 2025) == "KC1"
    assert abv_man.to_regular("SER", 2025) == "SER"
