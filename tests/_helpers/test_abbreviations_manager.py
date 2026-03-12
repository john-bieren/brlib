"""Tests the methods of the `AbbreviationsManager` singleton."""

from brlib._helpers.abbreviations_manager import abv_mgr


def test_cache() -> None:
    """Tests that the contents are the same whether loaded from cache or the web."""
    # use data already loaded from the web
    expected_df = abv_mgr.df.copy()
    assert abv_mgr._has_valid_cache

    # reset abv_mgr and load data from cache
    abv_mgr.__init__()
    compared = abv_mgr.df.compare(expected_df)
    assert compared.empty


def test_correct_abvs() -> None:
    """Tests the outputs of the `correct_abvs` method."""
    # abbreviation not used during given season
    assert abv_mgr.correct_abvs("OAK", 2025, era_adjustment=True) == ["ATH"]
    assert abv_mgr.correct_abvs("OAK", 2025, era_adjustment=False) == []
    # abbreviation used by different franchises over the years
    assert abv_mgr.correct_abvs("BAL", 1915, era_adjustment=True) == ["SLB", "BAL"]
    assert abv_mgr.correct_abvs("BAL", 1915, era_adjustment=False) == ["BAL"]
    # abbreviation used discontinuously, not during given season
    assert abv_mgr.correct_abvs("LAA", 1977, era_adjustment=False) == ["CAL"]
    assert abv_mgr.correct_abvs("LAA", 1907, era_adjustment=False) == []
    # abbreviation never used
    assert abv_mgr.correct_abvs("SER", 2025, era_adjustment=False) == []
    # special case
    assert abv_mgr.correct_abvs("PC", 1939, era_adjustment=True) == ["TC", "TC2"]
    assert abv_mgr.correct_abvs("TC", 1939, era_adjustment=True) == ["TC", "TC2"]
    assert abv_mgr.correct_abvs("TC2", 1939, era_adjustment=True) == ["TC", "TC2"]
    assert abv_mgr.correct_abvs("TC", 1939, era_adjustment=False) == ["TC"]
    assert abv_mgr.correct_abvs("TC2", 1939, era_adjustment=False) == ["TC2"]


def test_franchise_abv() -> None:
    """Tests the outputs of the `franchise_abv` method."""
    # correct abbreviation
    assert abv_mgr.franchise_abv("ATH", 1876) == "ATH"
    # abbreviation used by different franchises over the years
    assert abv_mgr.franchise_abv("BAL", 1915) == "BLT"
    # abbreviation not used during given season
    assert abv_mgr.franchise_abv("OAK", 2025) == ""
    # abbreviation never used
    assert abv_mgr.franchise_abv("SER", 2025) == ""


def test_all_team_abvs() -> None:
    """Tests the outputs of the `all_team_abvs` method."""
    # correct abbreviation
    assert abv_mgr.all_team_abvs("ATH", 2025) == ["ATH", "KCA", "OAK", "PHA"]
    # abbreviation not used during given season
    assert abv_mgr.all_team_abvs("OAK", 2025) == []
    # abbreviation never used
    assert abv_mgr.all_team_abvs("SER", 2025) == []


def test_to_alias() -> None:
    """Tests the outputs of the `to_alias` method."""
    # correct abbreviation, has no alias
    assert abv_mgr.to_alias("SEA", 2025) == "SEA"
    # correct abbreviation (that's also a later team's alias), has an alias
    assert abv_mgr.to_alias("KCA", 1963) == "KC1"
    # correct alias never used as an abbreviation
    assert abv_mgr.to_alias("NY1", 1954) == "NY1"
    # abbreviation not used during given season
    assert abv_mgr.to_alias("PBS", 2025) == "PBS"
    # abbreviation never used
    assert abv_mgr.to_alias("SER", 2025) == "SER"
    # correct abbreviation, has an alias
    assert abv_mgr.to_alias("LAA", 2014) == "ANA"
    # same correct abbreviation, has no alias during this era (special case)
    assert abv_mgr.to_alias("LAA", 1963) == "LAA"


def test_to_regular() -> None:
    """Tests the outputs of the `to_regular` method."""
    # correct abbreviation, has no alias
    assert abv_mgr.to_regular("SEA", 2025) == "SEA"
    # correct alias (that's also an earlier team's abbreviation)
    assert abv_mgr.to_regular("KCA", 1999) == "KCR"
    # alias not used during given season
    assert abv_mgr.to_regular("KC1", 2025) == "KC1"
    # alias never used
    assert abv_mgr.to_regular("SER", 2025) == "SER"
    # correct alias
    assert abv_mgr.to_regular("ANA", 2014) == "LAA"
    # same alias, not used during this era (special case)
    assert abv_mgr.to_regular("ANA", 1963) == "ANA"
