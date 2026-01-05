#!/usr/bin/env python3

"""Defines Teams class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import RECORDS_COLS
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .team import Team


class Teams():
    @runtime_typecheck
    def __init__(self, teams: list[Team]) -> None:
        self._contents = tuple(team.id for team in teams)
        if len(self._contents) == 0:
            return

        self.info = pd.concat([t.info for t in teams], ignore_index=True)
        self.batting = pd.concat([t.batting for t in teams], ignore_index=True)
        self.pitching  = pd.concat([t.pitching for t in teams], ignore_index=True)
        self.fielding = pd.concat([t.fielding for t in teams], ignore_index=True)

        self.players = list(chain.from_iterable(t.players for t in teams))
        self.players = list(dict.fromkeys(self.players))

        self._gather_records()

    def __len__(self) -> int:
        return len(self._contents)

    def __str__(self) -> str:
        return f"{self.__len__()} teams"

    def __repr__(self) -> str:
        display_teams = [f"Team('{t[:-4]}', '{t[-4:]}')" for t in self._contents]
        return f"Teams({", ".join(display_teams)})"

    def _gather_records(self) -> None:
        """Populates `self.records`."""
        prep_df = self.info.copy()
        # All-Star teams have no team ID, so they are excluded
        non_asg_rows = ~prep_df["Team ID"].isna()
        prep_df.loc[non_asg_rows, "Franchise"] = prep_df.loc[non_asg_rows, "Team ID"].apply(
            lambda x: abv_man.franchise_abv(x[:-4], int(x[-4:]))
        )
        prep_df.loc[~non_asg_rows, "Franchise"] = prep_df.loc[~non_asg_rows, "Team"]
        self.records = prep_df.groupby("Franchise")[["Wins", "Losses", "Ties"]].sum()

        self.records.reset_index(inplace=True)
        self.records["Games"] = self.records[["Wins", "Losses", "Ties"]].sum(axis=1).astype(int)
        self.records["Win %"] = self.records["Wins"] / (self.records["Games"]-self.records["Ties"])
        self.records = self.records.reindex(columns=RECORDS_COLS)

    def add_no_hitters(self) -> None:
        success = nhd.populate()
        if not success:
            return
        self.pitching.loc[:, ["NH", "PG", "CNH"]] = 0

        # find the team with no-hitters
        nh_teams = set()
        nh_teams.update(nhd.team_inh_dict.keys())
        nh_teams.update(nhd.team_pg_dict.keys())
        nh_teams.update(nhd.team_cnh_dict.keys())
        nh_teams = set(self._contents).intersection(nh_teams)

        for team_id in list(nh_teams):
            individual_nh_list = nhd.team_inh_dict.get(team_id, [])
            perfect_game_list = nhd.team_pg_dict.get(team_id, [])
            combined_nh_list = nhd.team_cnh_dict.get(team_id, [])
            team_mask = self.pitching["Team ID"] == team_id

            # add individual no-hitters
            for col, inh_list in (
                ("NH", individual_nh_list),
                ("PG", perfect_game_list)
                ):
                for player, game_type in inh_list:
                    self.pitching.loc[
                        (team_mask) &
                        # player totals
                        (((self.pitching["Player ID"] == player) &
                          (self.pitching["Game Type"].str.startswith(game_type))) |
                        # team totals row
                         ((self.pitching["Name"] == "Team Totals") &
                          (self.pitching["Game Type"].str.startswith(game_type)))),
                        col
                    ] += 1

            # add combined no-hitters
            games_logged = []
            for player, game_type, game_id in combined_nh_list:
                # player totals
                self.pitching.loc[
                    (self.pitching["Team ID"] == team_id) &
                    ((self.pitching["Player ID"] == player) &
                     (self.pitching["Game Type"].str.startswith(game_type))),
                    "CNH"
                ] += 1
                # team totals row (only increment total once per game)
                if game_id not in games_logged:
                    self.pitching.loc[
                        (self.pitching["Team ID"] == team_id) &
                        ((self.pitching["Player"] == "Team Totals") &
                         (self.pitching["Game Type"].str.startswith(game_type))),
                        "CNH"
                    ] += 1
                    games_logged.append(game_id)
