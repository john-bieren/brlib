#!/usr/bin/env python3

"""Defines Players class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import TEAM_REPLACEMENTS
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .player import Player


class Players():
    @runtime_typecheck
    def __init__(self, players: list[Player]) -> None:
        self._contents = tuple(player.id for player in players)
        if len(self._contents) == 0:
            return

        self.info = pd.concat([p.info for p in players], ignore_index=True)
        self.bling = pd.concat([p.bling for p in players], ignore_index=True)
        self.batting = pd.concat([p.batting for p in players], ignore_index=True)
        self.pitching = pd.concat([p.pitching for p in players], ignore_index=True)
        self.fielding = pd.concat([p.fielding for p in players], ignore_index=True)

        self.teams = list(chain.from_iterable(p.teams for p in players))
        self.teams = list(dict.fromkeys(self.teams))

    def __len__(self) -> int:
        return len(self._contents)

    def __str__(self) -> str:
        return f"{self.__len__()} players"

    def __repr__(self) -> str:
        return f"Players({", ".join((f"Player({p})" for p in self._contents))})"

    def update_team_names(self) -> None:
        self.info.replace({"Draft Team": TEAM_REPLACEMENTS}, inplace=True)

    def add_no_hitters(self) -> None:
        success = nhd.populate()
        if not success:
            return
        # set zeros for calculable rows
        self.pitching.loc[
            (self.pitching["Season"] != "162 Game Avg") &
            ~((self.pitching["Season"] == "Career Totals") &
              (~self.pitching["League"].isna())),
            ["NH", "PG", "CNH"]
        ] = 0

        # find the players who've pitched in no-hitters
        nh_players = set()
        nh_players.update(nhd.player_inh_dict.keys())
        nh_players.update(nhd.player_pg_dict.keys())
        nh_players.update(nhd.player_cnh_dict.keys())
        nh_players = set(self._contents).intersection(nh_players)

        for player_id in list(nh_players):
            inh_list = nhd.player_inh_dict.get(player_id, [])
            pg_list = nhd.player_pg_dict.get(player_id, [])
            cnh_list = nhd.player_cnh_dict.get(player_id, [])
            player_mask = self.pitching["Player ID"] == player_id

            # add no-hitters to season stats
            for col, nh_list in (
                ("NH", inh_list),
                ("PG", pg_list),
                ("CNH", cnh_list)
                ):
                for year, team, game_type in nh_list:
                    # spahnwa01 threw no-hitters for MLN, but the applicable total row is for BSN
                    # not only are these different, but BSN isn't even the franchise abv (ATL is)
                    # so we check for career rows for any of the franchise's abbreviations
                    all_team_abvs = abv_man.all_team_abvs(team, int(year))
                    self.pitching.loc[
                        (player_mask) &
                        # team and season row
                        (((self.pitching["Season"] == year) &
                          (self.pitching["Team"] == team) &
                          (self.pitching["Game Type"].str.startswith(game_type))) |
                        # multi-team season row
                         ((self.pitching["Season"] == year) &
                          (self.pitching["Team"].str.fullmatch("[1-9]TM"))) |
                        # career totals row, team career totals row
                         ((self.pitching["Season"] == "Career Totals") &
                          ((self.pitching["Team"].isna()) |
                           (self.pitching["Team"].isin(all_team_abvs))) &
                          (self.pitching["League"].isna()) &
                          (self.pitching["Game Type"].str.startswith(game_type)))),
                        col
                    ] += 1
