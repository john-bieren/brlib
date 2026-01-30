#!/usr/bin/env python3

"""Defines PlayerSet class."""

from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import MULTI_TEAM_REGEX, TEAM_REPLACEMENTS
from ._helpers.no_hitter_dicts import nhd
from ._helpers.utils import runtime_typecheck
from .player import Player


class PlayerSet:
    """
    The aggregated contents of multiple `Player` objects.

    ## Parameters

    * `players`: `list[Player]`

        The list of the players to aggregate.

    ## Attributes

    * `info`: `pandas.DataFrame`

        Contains biographical information about the players.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerinfo-and-playersetinfo)

    * `bling`: `pandas.DataFrame`

        Contains the players' career accolades as displayed by the banners in the upper right-hand corner of their pages.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerbling-and-playersetbling)

    * `batting`: `pandas.DataFrame`

        Contains the players' batting and baserunning stats.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerbatting-and-playersetbatting)

    * `pitching`: `pandas.DataFrame`

        Contains the players' pitching stats.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerpitching-and-playersetpitching)

    * `fielding`: `pandas.DataFrame`

        Contains the players' fielding stats.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerfielding-and-playersetfielding)

    * `teams`: `list[tuple[str, str]]`

        A list of the teams on which the players appeared. Can be an input to `get_teams`.

    ## Examples

    Aggregate a list of `Player` objects:

    ```
    >>> p1 = br.Player("lewisky01")
    >>> p2 = br.Player("sanchsi01")
    >>> br.PlayerSet([p1, p2])
    PlayerSet(Player(lewisky01), Player(sanchsi01))
    ```

    Directly pass `get_players` results:

    ```
    >>> pl = br.get_players(["lewisky01", "sanchsi01"])
    >>> br.PlayerSet(pl)
    PlayerSet(Player(lewisky01), Player(sanchsi01))
    ```

    ## Methods

    * [`PlayerSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/PlayerSet.add_no_hitters)
    * [`PlayerSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/PlayerSet.update_team_names)
    """
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
        return f"PlayerSet({", ".join((f"Player({p})" for p in self._contents))})"

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `PlayerSet.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> p1 = br.Player("coleta01")
        >>> p2 = br.Player("penafe01")
        >>> ps = br.PlayerSet([p1, p2])
        >>> mask = ps.pitching["Season"].str.len() == 4
        >>> ps.pitching.loc[mask, ["Player", "Season", "NH", "PG", "CNH"]]
                Player Season  NH  PG  CNH
        0   Taylor Cole   2017 NaN NaN  NaN
        1   Taylor Cole   2018 NaN NaN  NaN
        2   Taylor Cole   2019 NaN NaN  NaN
        7    Félix Peña   2016 NaN NaN  NaN
        8    Félix Peña   2017 NaN NaN  NaN
        9    Félix Peña   2018 NaN NaN  NaN
        10   Félix Peña   2019 NaN NaN  NaN
        11   Félix Peña   2020 NaN NaN  NaN
        12   Félix Peña   2021 NaN NaN  NaN
        >>> ps.add_no_hitters()
        >>> ps.pitching.loc[mask, ["Player", "Season", "NH", "PG", "CNH"]]
                Player Season   NH   PG  CNH
        0   Taylor Cole   2017  0.0  0.0  0.0
        1   Taylor Cole   2018  0.0  0.0  0.0
        2   Taylor Cole   2019  0.0  0.0  1.0
        7    Félix Peña   2016  0.0  0.0  0.0
        8    Félix Peña   2017  0.0  0.0  0.0
        9    Félix Peña   2018  0.0  0.0  0.0
        10   Félix Peña   2019  0.0  0.0  1.0
        11   Félix Peña   2020  0.0  0.0  0.0
        12   Félix Peña   2021  0.0  0.0  0.0
        ```
        """
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
                        player_mask &
                        # team and season row
                        (((self.pitching["Season"] == year) &
                          (self.pitching["Team"] == team) &
                          (self.pitching["Game Type"].str.startswith(game_type))) |
                        # multi-team season row
                         ((self.pitching["Season"] == year) &
                          (self.pitching["Team"].str.fullmatch(MULTI_TEAM_REGEX))) |
                        # career totals row, team career totals row
                         ((self.pitching["Season"] == "Career Totals") &
                          ((self.pitching["Team"].isna()) |
                           (self.pitching["Team"].isin(all_team_abvs))) &
                          (self.pitching["League"].isna()) &
                          (self.pitching["Game Type"].str.startswith(game_type)))),
                        col
                    ] += 1

    def update_team_names(self) -> None:
        """
        Standardizes team names in `PlayerSet.info["Draft Team"]` such that teams are identified by one name, excluding relocations.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> pl = br.get_players(["longoev01", "hanigmi01", "troutmi01"])
        >>> ps = br.PlayerSet(pl)
        >>> ps.info["Draft Team"]
        0             Tampa Bay Devil Rays
        1                Milwaukee Brewers
        2    Los Angeles Angels of Anaheim
        Name: Draft Team, dtype: object
        >>> ps.update_team_names()
        >>> ps.info["Draft Team"]
        0        Tampa Bay Rays
        1     Milwaukee Brewers
        2    Los Angeles Angels
        Name: Draft Team, dtype: object
        ```
        """
        self.info.replace({"Draft Team": TEAM_REPLACEMENTS}, inplace=True)
