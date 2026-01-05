#!/usr/bin/env python3

"""Tests methods of the abbreviations_manager singleton."""

from brlib._helpers.abbreviations_manager import abv_man

def test_correct_abvs():
    assert abv_man.correct_abvs("OAK", 2025, era_adjustment=True) == ["ATH"]
    assert abv_man.correct_abvs("OAK", 2025, era_adjustment=False) == []
    assert abv_man.correct_abvs("BAL", 1915, era_adjustment=True) == ["SLB", "BAL"]
    assert abv_man.correct_abvs("BAL", 1915, era_adjustment=False) == ["BAL"]
    assert abv_man.correct_abvs("LAA", 1977, era_adjustment=False) == ["CAL"]
    assert abv_man.correct_abvs("LAA", 1907, era_adjustment=False) == []
    assert abv_man.correct_abvs("SER", 2025, era_adjustment=False) == []

def test_franchise_abv():
    assert abv_man.franchise_abv("ATH", 1876) == "ATH"
    assert abv_man.franchise_abv("BAL", 1915) == "BLT"
    assert abv_man.franchise_abv("OAK", 2025) == ""
    assert abv_man.franchise_abv("SER", 2025) == ""

def test_all_team_abvs():
    assert abv_man.all_team_abvs("ATH", 2025) == ["ATH", "KCA", "OAK", "PHA"]
    assert abv_man.all_team_abvs("OAK", 2025) == []
    assert abv_man.all_team_abvs("SER", 2025) == []

def test_to_alias():
    assert abv_man.to_alias("SEA", 2025) == "SEA"
    assert abv_man.to_alias("KCA", 1963) == "KC1"
    assert abv_man.to_alias("PBS", 2025) == "PBS"
    assert abv_man.to_alias("SER", 2025) == "SER"

def test_to_regular():
    assert abv_man.to_regular("SEA", 2025) == "SEA"
    assert abv_man.to_regular("KCA", 1999) == "KCR"
    assert abv_man.to_regular("KC1", 2025) == "KC1"
    assert abv_man.to_regular("SER", 2025) == "SER"
