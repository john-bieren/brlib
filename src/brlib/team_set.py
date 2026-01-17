#!/usr/bin/env python3

"""Defines TeamSet class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import RECORDS_COLS
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .team import Team


class TeamSet():
    """
    The aggregated contents of multiple `Team` objects.

    ## Parameters

    * `teams`: `list[Team]`

        The list of the teams to aggregate.

    ## Attributes

    * `info`: `pandas.DataFrame`

        Contains information about the teams, their results, and their personnel.

    * `batting`: `pandas.DataFrame`

        Contains the teams' batting and baserunning stats.

    * `pitching`: `pandas.DataFrame`

        Contains the teams' pitching stats.

    * `fielding`: `pandas.DataFrame`

        Contains the teams' fielding stats.

    * `records`: `pandas.DataFrame`

        Contains the teams' regular season records by franchise.

    * `players`: `list[str]`

        A list of the players who played for the teams. Can be an input to `get_players`.

    ## Examples

    Aggregate a list of `Team` objects:

    ```
    >>> t1 = br.Team("SEP", "1969")
    >>> t2 = br.Team("MLA", "1901")
    >>> br.TeamSet([t1, t2])
    TeamSet(Team('SEP', '1969'), Team('MLA', '1901'))
    ```

    Directly pass `get_teams` results:

    ```
    >>> tl = br.get_teams([("SEP", "1969"), ("MLA", "1901")])
    >>> br.TeamSet(tl)
    TeamSet(Team('SEP', '1969'), Team('MLA', '1901'))
    ```

    ## Methods

    * [`TeamSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/TeamSet.add_no_hitters)
    """
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
        return f"TeamSet({", ".join(display_teams)})"

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
        """
        Populates the no-hitter columns in the `TeamSet.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None.

        ## Returns

        `None`

        ## Example

        ```
        >>> t1 = br.Team("BOS", "1917")
        >>> t2 = br.Team("PRO", "1883")
        >>> ts = br.TeamSet([t1, t2])
        >>> ts.pitching[["Player", "NH", "PG", "CNH"]]
                    Player  NH  PG  CNH
        0      Weldon Wyckoff NaN NaN  NaN
        1         Ernie Shore NaN NaN  NaN
        2           Babe Ruth NaN NaN  NaN
        3        Herb Pennock NaN NaN  NaN
        4           Carl Mays NaN NaN  NaN
        5       Dutch Leonard NaN NaN  NaN
        6       Sad Sam Jones NaN NaN  NaN
        7         Rube Foster NaN NaN  NaN
        8          Lore Bader NaN NaN  NaN
        9         Team Totals NaN NaN  NaN
        10    Charlie Sweeney NaN NaN  NaN
        11       Lee Richmond NaN NaN  NaN
        12  Old Hoss Radbourn NaN NaN  NaN
        13        Team Totals NaN NaN  NaN
        >>> ts.add_no_hitters()
        >>> ts.pitching[["Player", "NH", "PG", "CNH"]]
                    Player   NH   PG  CNH
        0      Weldon Wyckoff  0.0  0.0  0.0
        1         Ernie Shore  0.0  0.0  1.0
        2           Babe Ruth  0.0  0.0  1.0
        3        Herb Pennock  0.0  0.0  0.0
        4           Carl Mays  0.0  0.0  0.0
        5       Dutch Leonard  0.0  0.0  0.0
        6       Sad Sam Jones  0.0  0.0  0.0
        7         Rube Foster  0.0  0.0  0.0
        8          Lore Bader  0.0  0.0  0.0
        9         Team Totals  0.0  0.0  1.0
        10    Charlie Sweeney  0.0  0.0  0.0
        11       Lee Richmond  0.0  0.0  0.0
        12  Old Hoss Radbourn  0.0  0.0  0.0
        13        Team Totals  0.0  0.0  0.0
        ```
        """
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
