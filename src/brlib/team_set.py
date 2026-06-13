"""Defines `TeamSet` class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_mgr
from ._helpers.constants import (
    RECORDS_DTYPES,
    TEAM_REPLACEMENTS,
    VENUE_REPLACEMENTS,
)
from ._helpers.no_hitter_dicts import nhd
from ._helpers.typechecking import runtime_typecheck
from .team import Team


class TeamSet:
    """
    The aggregated contents of multiple `Team` objects.

    ## Parameters

    * `teams`: `list[Team]`

        The non-empty list of the Teams to aggregate.

    ## Attributes

    * `info`: `pandas.DataFrame`

        Contains information about the teams, their results, and their personnel. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teaminfo-and-teamsetinfo)

    * `bling`: `pandas.DataFrame`

        Contains the teams' accolades and those of their players. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teambling-and-teamsetbling)

    * `batting`: `pandas.DataFrame`

        Contains the teams' batting and baserunning stats. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teambatting-and-teamsetbatting)

    * `pitching`: `pandas.DataFrame`

        Contains the teams' pitching stats. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teampitching-and-teamsetpitching)

    * `fielding`: `pandas.DataFrame`

        Contains the teams' fielding stats. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teamfielding-and-teamsetfielding)

    * `records`: `pandas.DataFrame`

        Contains the teams' cumulative regular season records by franchise. [See DataFrame
        info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gamesetrecords-and-teamsetrecords)

    * `players`: `list[str]`

        A list of the players who played for the teams. Can be an input to
        [`get_players`](https://github.com/john-bieren/brlib/wiki/get_players).

    ## Examples

    Aggregate a list of `Team` objects:

    ```
    >>> t1 = br.Team("SEP1969")
    >>> t2 = br.Team("MLA1901")
    >>> br.TeamSet([t1, t2])
    TeamSet(Team('SEP1969'), Team('MLA1901'))
    ```

    Directly pass [`get_teams`](https://github.com/john-bieren/brlib/wiki/get_teams) results:

    ```
    >>> tl = br.get_teams(["SEP1969", "MLA1901"])
    >>> br.TeamSet(tl)
    TeamSet(Team('SEP1969'), Team('MLA1901'))
    ```

    ## Methods

    * [`TeamSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/TeamSet.add_no_hitters)
    * [`TeamSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/TeamSet.update_team_names)
    * [`TeamSet.update_venue_names`](https://github.com/john-bieren/brlib/wiki/TeamSet.update_venue_names)
    """

    @runtime_typecheck
    def __init__(self, teams: list[Team]) -> None:
        self._contents = tuple(team.id for team in teams)
        if len(self._contents) == 0:
            raise ValueError("no Teams to aggregate")

        self.info = pd.concat([t.info for t in teams], ignore_index=True)
        self.bling = pd.concat([t.bling for t in teams], ignore_index=True)
        self.batting = pd.concat([t.batting for t in teams], ignore_index=True)
        self.pitching = pd.concat([t.pitching for t in teams], ignore_index=True)
        self.fielding = pd.concat([t.fielding for t in teams], ignore_index=True)

        self.players = list(chain.from_iterable(t.players for t in teams))
        self.players = list(dict.fromkeys(self.players))

        self._gather_records()

    def __len__(self) -> int:
        return len(self._contents)

    def __str__(self) -> str:
        return f"{len(self)} teams"

    def __repr__(self) -> str:
        teams = [f"Team('{team_id}')" for team_id in self._contents]
        return f'TeamSet({", ".join(teams)})'  # single quotes for <3.12 support

    def _gather_records(self) -> None:
        """Populates `self.records`."""
        prep_df = self.info.copy()
        # All-Star teams have no team ID, so they are excluded
        non_asg_rows = ~prep_df["Team ID"].isna()
        prep_df.loc[non_asg_rows, "Franchise"] = prep_df.loc[non_asg_rows, "Team ID"].apply(
            lambda x: abv_mgr.franchise_abv(x[:-4], int(x[-4:]))
        )
        prep_df.loc[~non_asg_rows, "Franchise"] = prep_df.loc[~non_asg_rows, "Team"]
        self.records = prep_df.groupby("Franchise")[["Wins", "Losses", "Ties"]].sum()

        self.records = self.records.reset_index()
        self.records["Games"] = self.records[["Wins", "Losses", "Ties"]].sum(axis=1).astype("int64")
        self.records["W-L%"] = self.records["Wins"] / (
            self.records["Wins"] + self.records["Losses"]
        )
        self.records = self.records.reindex(columns=list(RECORDS_DTYPES))
        self.records = self.records.astype(RECORDS_DTYPES)

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `TeamSet.pitching` DataFrame, which are empty by
        default (may require an additional request). You can change this behavior with
        [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> t1 = br.Team("BOS1917")
        >>> t2 = br.Team("PRO1883")
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
        nhd.populate()
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
            for col, inh_list in (("NH", individual_nh_list), ("PG", perfect_game_list)):
                for player, game_type in inh_list:
                    self.pitching.loc[
                        team_mask
                        & (
                            (
                                # player totals
                                (self.pitching["Player ID"] == player)
                                & (self.pitching["Game Type"].str.startswith(game_type))
                            )
                            | (
                                # team totals row
                                (self.pitching["Player"] == "Team Totals")
                                & (self.pitching["Game Type"].str.startswith(game_type))
                            )
                        ),
                        col,
                    ] += 1

            # add combined no-hitters
            games_logged = []
            for player, game_type, game_id in combined_nh_list:
                # player totals
                self.pitching.loc[
                    (self.pitching["Team ID"] == team_id)
                    & (
                        (self.pitching["Player ID"] == player)
                        & (self.pitching["Game Type"].str.startswith(game_type))
                    ),
                    "CNH",
                ] += 1
                # team totals row (only increment total once per game)
                if game_id not in games_logged:
                    self.pitching.loc[
                        (self.pitching["Team ID"] == team_id)
                        & (
                            (self.pitching["Player"] == "Team Totals")
                            & (self.pitching["Game Type"].str.startswith(game_type))
                        ),
                        "CNH",
                    ] += 1
                    games_logged.append(game_id)

    def update_team_names(self) -> None:
        """
        Standardizes team names such that teams are identified by one name, excluding relocations.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> t1 = br.Team("BRO1920")
        >>> t2 = br.Team("NYY1920")
        >>> ts = br.TeamSet([t1, t2])
        >>> ts.info["Team"]
        0     Brooklyn Robins
        1    New York Yankees
        Name: Team, dtype: object
        >>> ts.update_team_names()
        >>> ts.info["Team"]
        0    Brooklyn Dodgers
        1    New York Yankees
        Name: Team, dtype: object
        ```
        """
        self.info["Team"] = self.info.apply(
            lambda row: TEAM_REPLACEMENTS.get(row["Team ID"], row["Team"]), axis=1
        )
        self.bling["Team"] = self.bling.apply(
            lambda row: TEAM_REPLACEMENTS.get(row["Team ID"], row["Team"]), axis=1
        )
        self.batting["Team"] = self.batting.apply(
            lambda row: TEAM_REPLACEMENTS.get(row["Team ID"], row["Team"]), axis=1
        )
        self.pitching["Team"] = self.pitching.apply(
            lambda row: TEAM_REPLACEMENTS.get(row["Team ID"], row["Team"]), axis=1
        )
        self.fielding["Team"] = self.fielding.apply(
            lambda row: TEAM_REPLACEMENTS.get(row["Team ID"], row["Team"]), axis=1
        )

    def update_venue_names(self) -> None:
        """
        Standardizes venue names such that venues are identified by one name.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> t1 = br.Team("PHA1954")
        >>> t2 = br.Team("SFG2017")
        >>> ts = br.TeamSet([t1, t2])
        >>> ts.info["Venues"]
        0    Connie Mack Stadium
        1              AT&T Park
        Name: Venues, dtype: object
        >>> ts.update_venue_names()
        >>> ts.info["Venues"]
        0     Shibe Park
        1    Oracle Park
        Name: Venues, dtype: object
        ```
        """
        self.info["Venues"] = self.info["Venues"].apply(
            lambda x: (
                ";".join([VENUE_REPLACEMENTS.get(item, item) for item in x.split(";")])
                if isinstance(x, str)
                else x
            )
        )
