#!/usr/bin/env python3

"""Defines GameSet class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import (RANGE_TEAM_REPLACEMENTS, RECORDS_COLS,
                                 TEAM_REPLACEMENTS, VENUE_REPLACEMENTS)
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .game import Game


class GameSet:
    """
    The aggregated contents of multiple `Game` objects.

    ## Parameters

    * `games`: `list[Game]`

        The list of the games to aggregate.

    ## Attributes

    * `info`: `pandas.DataFrame`

        Contains information about the games and their circumstances.

    * `batting`: `pandas.DataFrame`

        Contains batting and baserunning stats from the batting tables and the information beneath them.

    * `pitching`: `pandas.DataFrame`

        Contains pitching stats from the pitching tables and the information beneath them.

    * `fielding`: `pandas.DataFrame`

        Contains fielding stats from the batting tables and the information beneath them.

    * `team_info`: `pandas.DataFrame`

        Contains information about the teams involved in the games.

    * `ump_info`: `pandas.DataFrame`

        Contains the names and positions of the games' umpires.

    * `records`: `pandas.DataFrame`

        Contains team records in the games by franchise.

    * `players`: `list[str]`

        A list of the players who appeared in the games. Can be an input to `get_players`.

    * `teams`: `list[tuple[str, str]]`

        A list of the teams involved in the games. Can be an input to `get_teams`.

    ## Examples

    Aggregate a list of `Game` objects:

    ```
    >>> g1 = br.Game("SEA", "20180930", "0")
    >>> g2 = br.Game("SEA", "20190929", "0")
    >>> br.GameSet([g1, g2])
    GameSet(Game('SEA', '20180930', '0'), Game('SEA', '20190929', '0'))
    ```

    Directly pass `get_games` results:

    ```
    >>> gl = br.get_games([("SEA", "20180930", "0"), ("SEA", "20190929", "0")])
    >>> br.GameSet(gl)
    GameSet(Game('SEA', '20180930', '0'), Game('SEA', '20190929', '0'))
    ```

    ## Methods

    * [`GameSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/GameSet.add_no_hitters)
    * [`GameSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/GameSet.update_team_names)
    * [`GameSet.update_venue_names`](https://github.com/john-bieren/brlib/wiki/GameSet.update_venue_names)
    """
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
        return f"GameSet({", ".join((g for g in display_games))})"

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

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `GameSet.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> g1 = br.Game("SEA", "20120815", "0")
        >>> g2 = br.Game("SEA", "20120608", "0")
        >>> gs = br.GameSet([g1, g2])
        >>> gs.pitching[["Player", "Team", "NH", "PG", "CNH"]]
                    Player                 Team  NH  PG  CNH
        0   Jeremy Hellickson       Tampa Bay Rays NaN NaN  NaN
        1     Kyle Farnsworth       Tampa Bay Rays NaN NaN  NaN
        2         Team Totals       Tampa Bay Rays NaN NaN  NaN
        3     Félix Hernández     Seattle Mariners NaN NaN  NaN
        4         Team Totals     Seattle Mariners NaN NaN  NaN
        ...               ...                  ... ... ...  ...
        11      Stephen Pryor     Seattle Mariners NaN NaN  NaN
        12       Lucas Luetge     Seattle Mariners NaN NaN  NaN
        13     Brandon League     Seattle Mariners NaN NaN  NaN
        14     Tom Wilhelmsen     Seattle Mariners NaN NaN  NaN
        15        Team Totals     Seattle Mariners NaN NaN  NaN
        >>> gs.add_no_hitters()
        >>> gs.pitching[["Player", "Team", "NH", "PG", "CNH"]]
                    Player                 Team   NH   PG  CNH
        0   Jeremy Hellickson       Tampa Bay Rays  0.0  0.0  0.0
        1     Kyle Farnsworth       Tampa Bay Rays  0.0  0.0  0.0
        2         Team Totals       Tampa Bay Rays  0.0  0.0  0.0
        3     Félix Hernández     Seattle Mariners  1.0  1.0  0.0
        4         Team Totals     Seattle Mariners  1.0  1.0  0.0
        ...               ...                  ...  ...  ...  ...
        11      Stephen Pryor     Seattle Mariners  0.0  0.0  1.0
        12       Lucas Luetge     Seattle Mariners  0.0  0.0  1.0
        13     Brandon League     Seattle Mariners  0.0  0.0  1.0
        14     Tom Wilhelmsen     Seattle Mariners  0.0  0.0  1.0
        15        Team Totals     Seattle Mariners  0.0  0.0  1.0
        ```
        """
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
                player_mask = (self.pitching["Player ID"] == player_id) & game_mask
                nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
                self.pitching.loc[
                    player_mask |
                    (game_mask &
                     (self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Team ID"] == nh_team_id)),
                    col
                ] = 1

            # add combined no-hitters
            for player_id in cnh_list:
                player_mask = (self.pitching["Player ID"] == player_id) & game_mask
                nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
                self.pitching.loc[
                    player_mask |
                    (game_mask &
                     (self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Team ID"] == nh_team_id)),
                    "CNH"
                ] = 1

    def update_team_names(self) -> None:
        """
        Standardizes team names such that teams are identified by one name, excluding relocations.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> g1 = br.Game("KC1", "19550824", "0")
        >>> g2 = br.Game("TBA", "20050828", "0")
        >>> gs = br.GameSet([g1, g2])
        >>> gs.info[["Away Team", "Home Team"]]
                            Away Team              Home Team
        0           Washington Nationals  Kansas City Athletics
        1  Los Angeles Angels of Anaheim   Tampa Bay Devil Rays
        >>> gs.update_team_names()
        >>> gs.info[["Away Team", "Home Team"]]
                                Away Team              Home Team
        0  Washington Nationals (1901-1960)  Kansas City Athletics
        1                Los Angeles Angels         Tampa Bay Rays
        ```
        """
        # replace old team names
        self.team_info.replace({"Team": TEAM_REPLACEMENTS}, regex=True, inplace=True)
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
        """
        Standardizes venue names such that venues are identified by one name.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> g1 = br.Game("SEA", "20180401", "0")
        >>> g2 = br.Game("TBA", "20050828", "0")
        >>> gs = br.GameSet([g1, g2])
        >>> gs.info["Venue"]
        0       Safeco Field
        1    Tropicana Field
        Name: Venue, dtype: object
        >>> gs.update_venue_names()
        >>> gs.info["Venue"]
        0      T-Mobile Park
        1    Tropicana Field
        Name: Venue, dtype: object
        ```
        """
        self.info.replace({"Venue": VENUE_REPLACEMENTS}, inplace=True)
