#!/usr/bin/env python3

"""Defines and instantiates NoHitterDicts singleton."""

import os
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi import Response

from ..options import write
from .constants import (BML_TEAM_ABVS, CACHE_DIR, CACHE_TIMEZONE, CURRENT_YEAR,
                        CY_BASEBALL, FIRST_GAMES_YEAR, SEASON_END_DATE)
from .requests_manager import req_man
from .singleton import Singleton
from .utils import report_on_exc, soup_from_comment, str_between


class NoHitterDicts(Singleton):
    """
    A wrapper for several dictionaries which contain information about no-hitters.
    Contains dictionaries for individual no-hitters, perfect games, or combined no-hitters
    oriented by game, player, or team. Manages retrieval and caching of the data upon use of the
    `populate` method. Until this method is called, the dictionaries are empty.
    """
    def __init__(self) -> None:
        self._cache_file = CACHE_DIR / "nh_data_v1.csv"
        self._populated = False

        self.game_inh_dict, self.game_pg_dict, self.game_cnh_dict = ({} for _ in range(3))
        self.player_inh_dict, self.player_pg_dict, self.player_cnh_dict = ({} for _ in range(3))
        self.team_inh_dict, self.team_pg_dict, self.team_cnh_dict = ({} for _ in range(3))

    def populate(self) -> bool:
        """Loads no-hitter dicts from cache or web, returns True if successful."""
        if self._populated:
            return True
        if self._has_valid_cache:
            data_df = self._load()
        else:
            data_df = self._get()

        if data_df.empty:
            return False
        self._generate_dicts(data_df)
        self._populated = True
        return True

    @property
    def _has_valid_cache(self) -> bool:
        """
        Whether cached nh_data.csv is valid, remove invalid cached files.
        If it is the offseason, the cache is valid if it was created during said offseason.
        If it is during the season, the cache is valid if it was created today.
        """
        if not self._cache_file.exists():
            return False

        last_save = os.path.getmtime(self._cache_file)
        last_save_time = datetime.fromtimestamp(last_save).astimezone(CACHE_TIMEZONE)
        current_time = datetime.now(CACHE_TIMEZONE)

        if CY_BASEBALL:
            season_end = datetime.strptime(f"{CURRENT_YEAR}-{SEASON_END_DATE}", "%Y-%m-%d")
        else:
            season_end = datetime.strptime(f"{CURRENT_YEAR-1}-{SEASON_END_DATE}", "%Y-%m-%d")
        season_end = season_end.astimezone(CACHE_TIMEZONE)

        # check whether the previous refresh was today
        if (current_time-last_save_time).days == 0 and last_save_time.hour <= current_time.hour:
            return True
        # check whether it's the offseason
        if not CY_BASEBALL or last_save_time > season_end:
            return True
        self._cache_file.unlink()
        return False

    def _load(self) -> pd.DataFrame:
        """Loads no-hitter data from cache."""
        data_df = pd.read_csv(self._cache_file)
        return data_df

    def _get(self) -> pd.DataFrame:
        """Gets no-hitter data from Baseball Reference."""
        write("gathering no-hitters")
        page = req_man.get_page("/friv/no-hitters-and-perfect-games.shtml")
        data_df = self._gather_data_df(page)
        data_df.to_csv(self._cache_file, index=False)
        return data_df

    @report_on_exc()
    def _gather_data_df(self, page: Response) -> pd.DataFrame:
        """Scrapes no-hitters page and generate `self.data_df`."""
        soup = bs(page.content, "lxml")
        content = soup.find(id="content")

        # scrape individual table
        individual_table = content.find("div", {"id": "all_no_hitters_individual"})
        individual_df = self._process_individual_df(individual_table)
        individual_df["Combined"] = "N"

        # scrape combined table
        combined_table = content.find("div", {"id": "all_no_hitters_combined"})
        combined_table = soup_from_comment(combined_table, only_if_table=True)
        combined_df = self._process_combined_df(combined_table)
        combined_df["Combined"] = "Y"
        return pd.concat([individual_df, combined_df])

    @staticmethod
    def _process_individual_df(individual_table: Tag) -> pd.DataFrame:
        """Turns `individual_table` into a DataFrame."""
        records = []
        for row in individual_table.find_all("tr"):
            record = [ele.text.strip("*") for ele in row.find_all(["th", "td"])]
            records.append(record[:8])
        individual_df = pd.DataFrame(
            records,
            columns=("Rk", "Name", "Perfect", "Gcar", "Gtm", "Year", "Date", "Team")
        )
        # remove the header rows which appear every 25 rows
        individual_df = individual_df.loc[individual_df["Name"] != "Name"].reset_index(drop=True)
        individual_df["Game Type"] = "R"
        postseason_mask = ((individual_df["Gcar"] == "") &
                           (individual_df["Year"].astype(int) > FIRST_GAMES_YEAR))
        individual_df.loc[postseason_mask, "Game Type"] = "P"
        individual_df.loc[individual_df["Perfect"] == "", "Perfect"] = "N"
        individual_df = individual_df.reindex(
            columns=["Player ID", "Perfect", "Combined", "Year", "Team", "Game ID", "Game Type"]
        )

        # create player id, game id columns
        player_id_column, game_id_column = ([] for _ in range(2))
        for row in individual_table.find_all("a", href=True):
            href = row.get("href", "")
            if href.startswith("/players"):
                player_id = str_between(href, "/", ".", anchor="end")
                player_id_column.append(player_id)
            elif href.startswith("/boxes"):
                game_id = str_between(href, "/", ".", anchor="end")
                game_id_column.append(game_id)

        individual_df["Player ID"] = player_id_column
        individual_df["Game ID"] = individual_df["Game ID"].astype("object")
        individual_df.loc[
            (~individual_df["Team"].isin(BML_TEAM_ABVS)) &
            (individual_df["Year"].astype(int) >= FIRST_GAMES_YEAR),
            "Game ID",
            ] = game_id_column
        return individual_df

    @staticmethod
    def _process_combined_df(combined_table: bs) -> pd.DataFrame:
        """Turns `combined_table` into a DataFrame."""
        records = []
        for row in combined_table.find_all("tr"):
            record = [ele.text.strip("*") for ele in row.find_all(["th", "td"])]
            records.append(record[:11])
        combined_df = pd.DataFrame(
            records,
            columns=("Rk", "Year", "Date", "Team", "Home/Away", "Opp", "Rslt", "Name", "Gcar", "Gtm", "Inngs")
        )
        # remove the header rows which appear every 25 rows
        combined_df = combined_df.loc[combined_df["Name"] != "Name"].reset_index(drop=True)
        combined_df["Game Type"] = "R"
        postseason_mask = ((combined_df["Gcar"] == "") &
                           (combined_df["Inngs"] != ""))
        combined_df.loc[postseason_mask, "Game Type"] = "P"
        combined_df = combined_df.reindex(
            columns=["Player ID", "Perfect", "Combined", "Year", "Team", "Game ID", "Game Type"]
        )
        combined_df["Perfect"] = "N"

        # extend year column, which is only filled for the first listed pitcher
        for i, row in combined_df.iterrows():
            row_is_new_game = row["Year"].isdigit()
            if row_is_new_game:
                year = row["Year"]
                team = row["Team"]
            else:
                combined_df.loc[i, "Year"] = year
                combined_df.loc[i, "Team"] = team

        # create player id, game id columns
        player_id_column, game_id_column = ([] for _ in range(2))
        for row in combined_table.find_all("a", href=True):
            href = row.get("href", "")
            if href.startswith("/players"):
                player_id = str_between(href, "/", ".", anchor="end")
                player_id_column.append(player_id)
            elif href.startswith("/boxes"):
                game_id = str_between(href, "/", ".", anchor="end")
                # filter out links to non-existant pages
                if game_id[:-9] not in BML_TEAM_ABVS:
                    game_id_column.append(game_id)

        combined_df["Player ID"] = player_id_column
        combined_df["Game ID"] = combined_df["Game ID"].astype("object")
        combined_df.loc[
            (~combined_df["Team"].isin(BML_TEAM_ABVS)) &
            (combined_df["Year"].astype(int) >= FIRST_GAMES_YEAR),
            "Game ID",
            ] = game_id_column
        return combined_df

    def _generate_dicts(self, data_df: pd.DataFrame) -> None:
        """Turns raw data in `data_df` into the final dictionaries."""
        data_df["Year"] = data_df["Year"].astype(str)
        data_df["Team ID"] = data_df["Team"] + data_df["Year"]
        inh_df = data_df[data_df["Combined"] == "N"]
        pg_df = inh_df[inh_df["Perfect"] == "Y"]
        cnh_df = data_df[data_df["Combined"] == "Y"]

        self.game_inh_dict = inh_df.groupby("Game ID")["Player ID"].apply(lambda x: x.iloc[0]).to_dict()
        self.game_pg_dict = pg_df.groupby("Game ID")["Player ID"].apply(lambda x: x.iloc[0]).to_dict()
        self.game_cnh_dict = cnh_df.groupby("Game ID")["Player ID"].apply(list).to_dict()

        self.player_inh_dict = inh_df.groupby("Player ID").apply(
            lambda x: [list(t) for t in zip(x["Year"], x["Team"], x["Game Type"])],
            include_groups=False
        ).to_dict()
        self.player_pg_dict = pg_df.groupby("Player ID").apply(
            lambda x: [list(t) for t in zip(x["Year"], x["Team"], x["Game Type"])],
            include_groups=False
        ).to_dict()
        self.player_cnh_dict = cnh_df.groupby("Player ID").apply(
            lambda x: [list(t) for t in zip(x["Year"], x["Team"], x["Game Type"])],
            include_groups=False
        ).to_dict()

        self.team_inh_dict = inh_df.groupby("Team ID").apply(
            lambda x: [list(t) for t in zip(x["Player ID"], x["Game Type"])],
            include_groups=False
        ).to_dict()
        self.team_pg_dict = pg_df.groupby("Team ID").apply(
            lambda x: [list(t) for t in zip(x["Player ID"], x["Game Type"])],
            include_groups=False
        ).to_dict()
        self.team_cnh_dict = cnh_df.groupby("Team ID").apply(
            lambda x: [list(t) for t in zip(x["Player ID"], x["Game Type"], x["Game ID"])],
            include_groups=False
        ).to_dict()

nhd = NoHitterDicts()
