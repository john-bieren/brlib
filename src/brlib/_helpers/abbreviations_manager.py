#!/usr/bin/env python3

"""Defines and instantiates AbbreviationsManager singleton."""

import functools
import os
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup as bs
from curl_cffi import Response

from ..options import write
from .constants import (BML_FRANCHISE_ABVS, CACHE_DIR, CACHE_TIMEZONE,
                        CURRENT_YEAR, CY_BASEBALL, FIRST_GAMES_YEAR,
                        SEASON_START_DATE, TEAM_ALIASES)
from .requests_manager import req_man
from .singleton import Singleton
from .utils import report_on_exc


class AbbreviationsManager(Singleton):
    """
    A wrapper for a DataFrame which contains information on all historical team and
    franchise abbreviations used by Baseball Reference. Manages retrieval and caching of the data,
    loads data on import of brlib. Has methods for working with these abbreviations.
    """
    def __init__(self) -> None:
        self._cache_file = CACHE_DIR / "abv_data_v1.csv"
        self.df = pd.DataFrame()

        if self._has_valid_cache:
            self._load()
        else:
            self._get()

    @property
    def _has_valid_cache(self) -> bool:
        """
        Whether cached abv_data.csv is valid, remove invalid cached files.
        The cache is valid if it was created since the start of the current/most recent season.
        """
        if not self._cache_file.exists():
            return False

        last_save = os.path.getmtime(self._cache_file)
        last_save_time = datetime.fromtimestamp(last_save).astimezone(CACHE_TIMEZONE)

        cy_refresh_date = f"{CURRENT_YEAR}-{SEASON_START_DATE}"
        refresh_time = datetime.strptime(cy_refresh_date, "%Y-%m-%d").astimezone(CACHE_TIMEZONE)

        current_time = datetime.now(CACHE_TIMEZONE)
        if current_time > refresh_time > last_save_time:
            self._cache_file.unlink()
            return False
        return True

    def _load(self) -> None:
        """Loads abbreviations data from cache."""
        self.df = pd.read_csv(self._cache_file)
        self.df["Alias"] = self.df["Alias"].astype(str)
        self.df.loc[self.df["Alias"] == "nan", "Alias"] = ""

    def _get(self) -> None:
        """Gets abbreviations data from Baseball Reference."""
        write("brlib: gathering team abbreviations")
        page = req_man.get_page("/about/team_IDs.shtml")
        self._gather_abbreviations(page)
        self.df.to_csv(self._cache_file, index=False)
        self.df.rename({"Team ID": "Team", "Franchise ID": "Franchise"}, axis=1, inplace=True)

    @report_on_exc()
    def _gather_abbreviations(self, page: Response) -> None:
        """Scrapes team_IDs page and create `self.df`."""
        soup = bs(page.content, "lxml")
        content = soup.find(id="content")
        table = content.find("div", {"class": "section_wrapper"}, recursive=False)
        table_text = table.decode_contents().strip()
        table_soup = bs(table_text, "lxml")

        records = []
        for i, row in enumerate(table_soup.find_all("tr")):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            if record[4] == "Present":
                record[4] = str(CURRENT_YEAR + CY_BASEBALL - 1)
            del record[2] # remove the column of full team names

            # create indicator column for major Negro League teams
            if i == 0:
                record.append("BML")
            else:
                record.append(record[0] in BML_FRANCHISE_ABVS)
            records.append(record)

        # set up self.df
        self.df = pd.DataFrame(records[1:], columns=records[0])
        self.df.rename({"Team ID": "Team", "Franchise ID": "Franchise"}, axis=1, inplace=True)
        self.df["First Year"] = self.df["First Year"].astype(int)
        self.df["Last Year"] = self.df["Last Year"].astype(int)

        # create alias column
        self.df["Alias"] = self.df["Team"].apply(lambda x: TEAM_ALIASES.get(x, ""))
        # Baltimore Terrapins have abv BAL and alias but the Orioles are also BAL and have no alias
        self.df.loc[self.df["Franchise"] == "BLT", "Alias"] = "BLF"
        # some teams with aliases overlap with earlier teams with same team abv, but in all cases
        # (excluding the above) these earlier teams existed before box scores, so this is tidier
        self.df.loc[self.df["Last Year"] < FIRST_GAMES_YEAR, "Alias"] = ""

    def is_valid(self, abbreviation: str) -> bool:
        """Checks whether `abbreviation` is a valid team abbreviation."""
        return abbreviation in self.df["Team"].values

    @functools.cache
    def _find_correct_teams(
            self,
            abbreviation: str,
            season: int,
            era_adjustment: bool
            ) -> pd.DataFrame:
        """
        Returns the team row associated with `abbreviation` during `season`.
        Can return an empty DataFrame if there is no match.

        If `era_adjustment` is True, the return DataFrame will contain the row associated with
        `abbrevation`'s franchise during `season` even if the abbreviation is not correct.
        For example, `self._find_correct_teams("FLA", 2025, True)` returns the `MIA` team row.
        There can be multiple rows in the return DataFrame if an abbreviation, e.g. `BAL`,
        is valid during a season, e.g. 1915, and is also associated with a franchise that
        is active during that year, e.g. `SLB` which uses `BAL` in later years. In this case,
        `self._find_correct_teams("BAL", 1915, True)`, the `BAL` and `SLB` team rows are returned.
        """
        abv_rows = self.df.loc[self.df["Team"] == abbreviation]

        if era_adjustment:
            potential_franchises = abv_rows["Franchise"].values
            franchise_rows = self.df.loc[self.df["Franchise"].isin(potential_franchises)]
            mask = ((franchise_rows["First Year"] <= season) &
                    (franchise_rows["Last Year"] >= season))
            matching_franchises = franchise_rows.loc[mask]["Franchise"]
            correct_rows = abv_rows.loc[abv_rows["Franchise"].isin(matching_franchises)]
            return self._fix_discontinuities(correct_rows, season)

        mask = (abv_rows["First Year"] <= season) & (abv_rows["Last Year"] >= season)
        correct_row = abv_rows.loc[mask]
        assert len(correct_row) <= 1
        return self._fix_discontinuities(correct_row, season)

    def _fix_discontinuities(self, team_rows: pd.DataFrame, season: int) -> pd.DataFrame:
        """
        For each row in `team_rows`, returns the team row with the shortest year range that
        includes `season` within the same franchise.
        For example, `LAA` is listed as 1961-present, but `CAL` and `ANA` were also used
        during that time. The rows returned should reflect the abbreviation used during `season`.
        It is assumed that all year ranges in `team_rows` include `season`.
        """
        team_rows.reset_index(drop=True, inplace=True)
        for i, row in team_rows.iterrows():
            franchise_rows = self.df.loc[self.df["Franchise"] == row["Franchise"]]
            mask = ((franchise_rows["First Year"] <= season) &
                    (franchise_rows["Last Year"] >= season))
            franchise_rows = franchise_rows.loc[mask]
            years_col = franchise_rows["Last Year"] - franchise_rows["First Year"]
            correct_row = franchise_rows.loc[years_col == years_col.min()]
            team_rows.iloc[i] = correct_row.reset_index(drop=True).iloc[0]
        return team_rows

    def correct_abvs(
            self,
            abbreviation: str,
            season: int,
            era_adjustment: bool
            ) -> list[str]:
        """Returns the team abbreviations from `self._find_correct_teams`."""
        team_rows = self._find_correct_teams(abbreviation, season, era_adjustment)
        return team_rows["Team"].values.tolist()

    def franchise_abv(
            self,
            abbreviation: str,
            season: int
            ) -> str:
        """Returns the franchise abbreviation for the team at `abbreviation` and `season`."""
        team_row = self._find_correct_teams(abbreviation, season, era_adjustment=False)
        if team_row.empty:
            return ""
        return team_row["Franchise"].values[0]

    def all_team_abvs(self, abbreviation: str, season: int) -> list[str]:
        """
        Returns all team abbreviations used by the franchise which is associated with the team at
        `abbreviation` and `season`, e.g. ("ATH", 2025) returns ["PHA", "KCA", "OAK", "ATH"].
        """
        franchise_abv = self.franchise_abv(abbreviation, season)
        franchise_df = self.df.loc[self.df["Franchise"] == franchise_abv]
        return franchise_df["Team"].values.tolist()

    def to_alias(self, abbreviation: str, season: int) -> str:
        """
        Returns the abbreviation that is used in box score URLs for home games of the team at
        `abbreviation` and `season`, as this will not always match the team's usual abbreviation.
        Will return `abbreviation` if there is no team at `abbreviation` and `season`.
        """
        # some team abvs, e.g. KCA, are also valid aliases, but should be converted to their alias
        team_row = self._find_correct_teams(abbreviation, season, era_adjustment=False)
        if not team_row.empty:
            alias = team_row["Alias"].values[0]
            if alias != "":
                return alias
        return abbreviation

    def to_regular(self, abbreviation: str, season: int) -> str:
        """
        Returns the true abbreviation for the team whose home game box score URLs during `season`
        use `abbreviation`. Will return `abbreviation` if no alias is applicable or if there is no
        team at `abbreviation` and `season`.
        """
        # some aliases, e.g. KCA, are valid team abvs, these should be left alone
        team_row = self._find_correct_teams(abbreviation, season, era_adjustment=False)
        if not team_row.empty: # this is a valid team abbreviation for season
            return team_row["Team"].values[0]

        # otherwise, convert alias to team abv
        alias_rows = self.df.loc[self.df["Alias"] == abbreviation]
        years_mask = (alias_rows["First Year"] <= season) & (alias_rows["Last Year"] >= season)
        correct_row = alias_rows.loc[years_mask]
        if correct_row.empty:
            return abbreviation
        return correct_row["Team"].values[0]

abv_man = AbbreviationsManager()
