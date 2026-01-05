#!/usr/bin/env python3

"""Defines Games class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import (RANGE_TEAM_REPLACEMENTS, RECORDS_COLS,
                                 TEAM_REPLACEMENTS, VENUE_REPLACEMENTS)
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .game import Game


class Games():
    @runtime_typecheck
    def __init__(self, games: list[Game]) -> None:
        self._contents = tuple(game.id for game in games)
        if len(self._contents) == 0:
            return

        self.info = pd.concat([g.info for g in games], ignore_index=True)
        self.batting = pd.concat([g.batting for g in games], ignore_index=True)
        self.pitching = pd.concat([g.pitching for g in games], ignore_index=True)
        self.fielding = pd.concat([g.fielding for g in games], ignore_index=True)
        self.team_info = pd.concat([g.team_info for g in games], ignore_index=True)
        self.ump_info = pd.concat([g.ump_info for g in games], ignore_index=True)

        self.players = list(chain.from_iterable(g.players for g in games))
        self.teams = list(chain.from_iterable(g.teams for g in games))
        self.players = list(dict.fromkeys(self.players))
        self.teams = list(dict.fromkeys(self.teams))

        self._gather_records()

    def __len__(self) -> int:
        return len(self._contents)

    def __str__(self) -> str:
        return f"{self.__len__()} games"

    def __repr__(self) -> str:
        display_games = []
        for game in self._contents:
            if "allstar" in game:
                team = "allstar"
                date = game[:4]
                dh = game[-1] if game[-1] != "e" else "0"
            else:
                team = game[:3]
                date = game[3:-1]
                dh = game[-1]
            display_games.append(f"Game('{team}', '{date}', '{dh}')")
        return f"Games({", ".join((g for g in display_games))})"

    def _gather_records(self) -> None:
        """Populates `self.records`."""
        prep_df = self.team_info.copy()
        # All-Star teams have no team ID, so they are excluded
        non_asg_rows = ~prep_df["Team ID"].isna()
        prep_df.loc[non_asg_rows, "Franchise"] = prep_df.loc[non_asg_rows, "Team ID"].apply(
            lambda x: abv_man.franchise_abv(x[:-4], int(x[-4:]))
        )
        # fill in All-Star team names
        prep_df.loc[~non_asg_rows, "Franchise"] = prep_df.loc[~non_asg_rows, "Team"]

        self.records = prep_df.groupby("Franchise")["Result"].value_counts()
        self.records = self.records.unstack(fill_value=0).reset_index()
        self.records.columns.name = None
        self.records = self.records.rename({"Win": "Wins", "Loss": "Losses", "Tie": "Ties"}, axis=1)
        if "Ties" not in self.records.columns:
            self.records["Ties"] = 0

        self.records = self.records.reindex(columns=RECORDS_COLS)
        self.records["Games"] = self.records[["Wins", "Losses", "Ties"]].sum(axis=1).astype(int)
        self.records["Win %"] = self.records["Wins"] / (self.records["Wins"]+self.records["Losses"])

    def update_team_names(self) -> None:
        # replace old team names
        self.info.replace({"Game": TEAM_REPLACEMENTS}, regex=True, inplace=True)
        self.info.replace({
                "Home Team": TEAM_REPLACEMENTS,
                "Away Team": TEAM_REPLACEMENTS,
                "Winning Team": TEAM_REPLACEMENTS,
                "Losing Team": TEAM_REPLACEMENTS
            }, inplace=True
        )
        self.batting.replace(
            {"Team": TEAM_REPLACEMENTS, "Opponent": TEAM_REPLACEMENTS}, inplace=True
        )
        self.pitching.replace(
            {"Team": TEAM_REPLACEMENTS, "Opponent": TEAM_REPLACEMENTS}, inplace=True
        )
        self.fielding.replace(
            {"Team": TEAM_REPLACEMENTS, "Opponent": TEAM_REPLACEMENTS}, inplace=True
        )

        # if all the games are All-Star Games, the Team ID column is all NaN, so .str doesn't work
        info_year_col = self.info["Home Team ID"].astype("object").str[-4:].astype("float64")
        batting_year_col = self.batting["Team ID"].astype("object").str[-4:].astype("float64")
        pitching_year_col = self.pitching["Team ID"].astype("object").str[-4:].astype("float64")
        fielding_year_col = self.fielding["Team ID"].astype("object").str[-4:].astype("float64")
        team_info_year_col = self.team_info["Team ID"].astype("object").str[-4:].astype("float64")

        # replace old team names within a given range
        for start_year, end_year, old_name, new_name in RANGE_TEAM_REPLACEMENTS:
            years = range(start_year, end_year+1)
            name_dict = {old_name: new_name}
            info_mask = info_year_col.isin(years)
            batting_mask = batting_year_col.isin(years)
            pitching_mask = pitching_year_col.isin(years)
            fielding_mask = fielding_year_col.isin(years)
            team_info_mask = team_info_year_col.isin(years)

            cols = ["Home Team", "Away Team", "Winning Team", "Losing Team"]
            self.info.loc[info_mask, cols] =\
                self.info.loc[info_mask, cols].replace(name_dict)
            self.info.loc[info_mask, "Game"] =\
                self.info.loc[info_mask, "Game"].replace(name_dict, regex=True)

            cols = ["Team", "Opponent"]
            self.batting.loc[batting_mask, cols] =\
                self.batting.loc[batting_mask, cols].replace(name_dict)
            self.pitching.loc[pitching_mask, cols] =\
                self.pitching.loc[pitching_mask, cols].replace(name_dict)
            self.fielding.loc[fielding_mask, cols] =\
                self.fielding.loc[fielding_mask, cols].replace(name_dict)

            cols = ["Team"]
            self.team_info.loc[team_info_mask, cols] =\
                self.team_info.loc[team_info_mask, cols].replace(name_dict)

    def update_venue_names(self) -> None:
        self.info.replace({"Venue": VENUE_REPLACEMENTS}, inplace=True)

    def add_no_hitters(self) -> None:
        success = nhd.populate()
        if not success:
            return
        self.pitching.loc[:, ["NH", "PG", "CNH"]] = 0

        # find the games which include no-hitters
        nh_games = set()
        nh_games.update(nhd.game_inh_dict.keys())
        nh_games.update(nhd.game_pg_dict.keys())
        nh_games.update(nhd.game_cnh_dict.keys())
        nh_games = set(self._contents).intersection(nh_games)

        for game_id in list(nh_games):
            inh_player_id = nhd.game_inh_dict.get(game_id, "")
            pg_player_id = nhd.game_pg_dict.get(game_id, "")
            cnh_list = nhd.game_cnh_dict.get(game_id, [])
            game_mask = self.pitching["Game ID"] == game_id

            # add individual no-hitters
            for col, player_id in (
                ("NH", inh_player_id),
                ("PG", pg_player_id)
                ):
                if player_id == "":
                    continue
                player_mask = (self.pitching["Player ID"] == player_id) & (game_mask)
                nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
                self.pitching.loc[
                    (player_mask) |
                    ((game_mask) &
                     (self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Team ID"] == nh_team_id)),
                    col
                ] = 1

            # add combined no-hitters
            for player_id in cnh_list:
                player_mask = (self.pitching["Player ID"] == player_id) & (game_mask)
                nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
                self.pitching.loc[
                    (player_mask) |
                    ((game_mask) &
                     (self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Team ID"] == nh_team_id)),
                    "CNH"
                ] = 1
