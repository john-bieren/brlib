#!/usr/bin/env python3

"""Defines Player class."""

import re
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi import Response
from dateutil.relativedelta import relativedelta

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import (
    BLING_DICT,
    LEAGUE_ABVS,
    MULTI_TEAM_REGEX,
    PLAYER_BATTING_COLS,
    PLAYER_BLING_COLS,
    PLAYER_FIELDING_COLS,
    PLAYER_INFO_COLS,
    PLAYER_PITCHING_COLS,
    PLAYER_URL_REGEX,
    RELATIVES_DICT,
    SEASON_REGEX,
    TEAM_REPLACEMENTS,
)
from ._helpers.inputs import validate_player_list
from ._helpers.no_hitter_dicts import nhd
from ._helpers.requests_manager import req_man
from ._helpers.utils import (
    change_innings_notation,
    clean_spaces,
    convert_numeric_cols,
    reformat_date,
    report_on_exc,
    runtime_typecheck,
    soup_from_comment,
    str_between,
    str_remove,
)
from .options import dev_alert, options, print_page


class Player:
    """
    Statistics and information from a player. Can be initialized by specifying `player_id`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded player page. If neither of these parameters are given, an exception is raised.

    ## Parameters

    * `player_id`: `str`, default `""`

        The first 5 letters of the player's last name, followed by the first two letters of their first name, and two digits as a unique identifier. This ID can be found in the URL of the player's page.

    * `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

        A previously loaded player page.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Player.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team name in `Player.info["Draft Team"]` such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    ## Attributes

    * `id`: `str`

        The unique identifier for the player used in the URL (e.g. `"vogelda01"`).

    * `name`: `str`

        The player's name (e.g. `"Daniel Vogelbach"`).

    * `info`: `pandas.DataFrame`

        Contains biographical information about the player.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerinfo-and-playersetinfo)

    * `bling`: `pandas.DataFrame`

        Contains the player's career accolades as displayed by the banners in the upper right-hand corner of their page.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerbling-and-playersetbling)

    * `batting`: `pandas.DataFrame`

        Contains the player's batting and baserunning stats from the three batting tables.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerbatting-and-playersetbatting)

    * `pitching`: `pandas.DataFrame`

        Contains the player's pitching stats from the three pitching tables.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerpitching-and-playersetpitching)

    * `fielding`: `pandas.DataFrame`

        Contains the player's fielding stats from the standard fielding table.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#playerfielding-and-playersetfielding)

    * `relatives`: `dict[str: list[str]]`

        The player's relationships with other major-leaguers. The relationships are they keys, and the values list the players. These values can be inputs to `get_players`.

    * `teams`: `list[tuple[str, str]]`

        A list of the teams on which the player appeared. Can be an input to `get_teams`.

    ## Example

    Load a player:

    ```
    >>> br.Player("whiteev01").name
    'Evan White'
    ```

    ## Methods

    * [`Player.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Player.add_no_hitters)
    * [`Player.update_team_names`](https://github.com/john-bieren/brlib/wiki/Player.update_team_names)
    """

    @runtime_typecheck
    def __init__(
        self,
        player_id: str = "",
        page: Response = Response(),
        add_no_hitters: bool | None = None,
        update_team_names: bool | None = None,
    ) -> None:
        if add_no_hitters is None:
            add_no_hitters = options.add_no_hitters
        if update_team_names is None:
            update_team_names = options.update_team_names

        if page.url == "":
            player_ids = validate_player_list([player_id])
            if len(player_ids) == 0:
                raise ValueError("invalid arguments")
            page = Player._get_player(player_ids[0])
        else:
            if not re.match(PLAYER_URL_REGEX, page.url):
                raise ValueError("page does not contain a player")

        self.name = ""
        self.id = str_between(page.url, "/", ".shtml", anchor="end")
        self.info, self.bling = (pd.DataFrame({"Player ID": [self.id]}) for _ in range(2))
        self.batting, self.pitching, self.fielding = (pd.DataFrame() for _ in range(3))
        self.teams = []
        self.relatives = defaultdict(list)
        self._yearly_salaries = defaultdict(int)
        self._url = page.url

        self._scrape_player(page)
        print_page(self.name)

        if add_no_hitters:
            self.add_no_hitters()
        if update_team_names:
            self.update_team_names()

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        if self._url == "":
            return "Player()"
        return f"Player('{self.id}')"

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `Player.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> p = br.Player("gilbety01")
        >>> p.pitching[["Team", "Season", "NH", "PG", "CNH"]]
            Team         Season  NH  PG  CNH
        0    ARI           2021 NaN NaN  NaN
        1    ARI           2022 NaN NaN  NaN
        2    ARI           2023 NaN NaN  NaN
        3    PHI           2024 NaN NaN  NaN
        4    CHW           2025 NaN NaN  NaN
        5   None  Career Totals NaN NaN  NaN
        6   None   162 Game Avg NaN NaN  NaN
        7    ARI  Career Totals NaN NaN  NaN
        8    CHW  Career Totals NaN NaN  NaN
        9    PHI  Career Totals NaN NaN  NaN
        10  None  Career Totals NaN NaN  NaN
        11  None  Career Totals NaN NaN  NaN
        >>> p.add_no_hitters()
        >>> p.pitching[["Team", "Season", "NH", "PG", "CNH"]]
            Team         Season   NH   PG  CNH
        0    ARI           2021  1.0  0.0  0.0
        1    ARI           2022  0.0  0.0  0.0
        2    ARI           2023  0.0  0.0  0.0
        3    PHI           2024  0.0  0.0  0.0
        4    CHW           2025  0.0  0.0  0.0
        5   None  Career Totals  1.0  0.0  0.0
        6   None   162 Game Avg  NaN  NaN  NaN
        7    ARI  Career Totals  1.0  0.0  0.0
        8    CHW  Career Totals  0.0  0.0  0.0
        9    PHI  Career Totals  0.0  0.0  0.0
        10  None  Career Totals  NaN  NaN  NaN
        11  None  Career Totals  NaN  NaN  NaN
        ```
        """
        success = nhd.populate()
        if not success:
            return
        # set zeros for calculable rows
        self.pitching.loc[
            (self.pitching["Season"] != "162 Game Avg")
            & ~((self.pitching["Season"] == "Career Totals") & (~self.pitching["League"].isna())),
            ["NH", "PG", "CNH"],
        ] = 0

        inh_list = nhd.player_inh_dict.get(self.id, [])
        pg_list = nhd.player_pg_dict.get(self.id, [])
        cnh_list = nhd.player_cnh_dict.get(self.id, [])

        # add no-hitters to season stats
        for col, nh_list in (("NH", inh_list), ("PG", pg_list), ("CNH", cnh_list)):
            for year, team, game_type in nh_list:
                # spahnwa01 threw his no-hitters for MLN, but the applicable total row is for BSN
                # not only are these different, but BSN isn't even the franchise abv (ATL is)
                # check for career rows for any of the franchise's abbreviations
                all_team_abvs = abv_man.all_team_abvs(team, int(year))
                self.pitching.loc[
                    (
                        # team and season row
                        (self.pitching["Season"] == year)
                        & (self.pitching["Team"] == team)
                        & (self.pitching["Game Type"].str.startswith(game_type))
                    )
                    | (
                        # multi-team season row
                        (self.pitching["Season"] == year)
                        & (self.pitching["Team"].str.fullmatch(MULTI_TEAM_REGEX))
                    )
                    | (
                        # career totals row, team career totals row
                        (self.pitching["Season"] == "Career Totals")
                        & (
                            (self.pitching["Team"].isna())
                            | (self.pitching["Team"].isin(all_team_abvs))
                        )
                        & (self.pitching["League"].isna())
                        & (self.pitching["Game Type"].str.startswith(game_type))
                    ),
                    col,
                ] += 1

    def update_team_names(self) -> None:
        """
        Standardizes team name in `Player.info["Draft Team"]` such that teams are identified by one name, excluding relocations.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> p = br.Player("beckejo02")
        >>> p.info["Draft Team"]
        0    Florida Marlins
        Name: Draft Team, dtype: object
        >>> p.update_team_names()
        >>> p.info["Draft Team"]
        0    Miami Marlins
        Name: Draft Team, dtype: object
        ```
        """
        self.info.replace({"Draft Team": TEAM_REPLACEMENTS}, inplace=True)

    @staticmethod
    def _get_player(player_id: str) -> Response:
        """Returns the page associated with a player."""
        endpoint = f"/players/{player_id[0]}/{player_id}.shtml"
        return req_man.get_page(endpoint)

    @report_on_exc()
    def _scrape_player(self, page: Response) -> None:
        """Scrapes player info and batting, pitching, and fielding stats from `page`."""
        soup = bs(page.content, "lxml")
        info = soup.find(id="info")
        content = soup.find(id="content")
        self.name = info.find("h1").text.strip()
        tables = content.find_all("div", {"class": "table_wrapper"}, recursive=False)

        wrap = soup.find(id="wrap")
        self._scrape_info(info, wrap)
        self.info = convert_numeric_cols(self.info)

        # find salary data first to add it to value tables
        for table in tables:
            if table.get("id") == "all_br-salaries":
                self._find_career_earnings(table)
                self.info.loc[:, "Minimum Career Earnings"] = sum(self._yearly_salaries.values())

        # then find the rest of the stats
        has_batted = has_pitched = has_fielded = False
        for table in tables:
            table_id = table.get("id")

            if table_id == "all_players_standard_batting":
                has_batted = True
                # these tables may be missing, but all three must exist to be merged later
                h_df_2, h_df_3 = (pd.DataFrame() for _ in range(2))
                h_df_1, advanced_batting_buffer = Player._scrape_standard_batting(table)

            elif table_id == "all_players_value_batting":
                h_df_2 = Player._scrape_value_table(table)

            elif table_id == "all_players_advanced_batting":
                h_df_3 = Player._scrape_advanced_table(table, advanced_batting_buffer)

            elif table_id == "all_players_standard_pitching":
                has_pitched = True
                p_df_1, advanced_pitching_buffer = Player._scrape_standard_pitching(table)

            elif table_id == "all_players_value_pitching":
                p_df_2 = Player._scrape_value_table(table)

            elif table_id == "all_players_advanced_pitching":
                p_df_3 = Player._scrape_advanced_table(table, advanced_pitching_buffer)

            elif table_id == "all_players_standard_fielding":
                has_fielded = True
                self._scrape_standard_fielding(table)

        if has_batted:
            self.batting = self._merge_dataframes(h_df_1, h_df_2, h_df_3)
            self.batting = self._finish_dataframe(self.batting)
        if has_pitched:
            self.pitching = self._merge_dataframes(p_df_1, p_df_2, p_df_3)
            self.pitching = self._finish_dataframe(self.pitching)
        if has_fielded:
            self.fielding = self._finish_dataframe(self.fielding)

        self.info = self.info.reindex(columns=PLAYER_INFO_COLS)
        self.bling = self.bling.reindex(columns=PLAYER_BLING_COLS)
        self.batting = self.batting.reindex(columns=PLAYER_BATTING_COLS)
        self.pitching = self.pitching.reindex(columns=PLAYER_PITCHING_COLS)
        self.fielding = self.fielding.reindex(columns=PLAYER_FIELDING_COLS)
        self.relatives = dict(self.relatives)

        # get final pieces of info which require the above DataFrames
        self._count_years_played()
        self._find_teams_info()

    def _scrape_info(self, info: Tag, wrap: Tag) -> None:
        """Populates `self.info` with data from `info` and `wrap`."""
        self.info.loc[:, "Player"] = self.name

        player_bio = info.find("div", {"id": "meta"})
        self._scrape_bio(player_bio)

        player_bling = info.find("ul", {"id": "bling"})
        self._scrape_bling(player_bling)

        # find career wins above replacement
        major_totals_summary = wrap.find("div", {"class": "p1"})
        if major_totals_summary is not None:
            self.info.loc[:, "bWAR"] = major_totals_summary.text.split("\n")[3]
        else:
            # player has played in postseason but not regular season
            self.info.loc[:, "bWAR"] = ""

    def _scrape_bio(self, player_bio: Tag) -> None:
        """Adds biographical information to `self.info`."""
        for line in player_bio.find_all("p"):
            line_str = str_remove(line.text, "\n", "•").replace("\xa0", " ")

            if line_str.startswith("Bats"):
                # no maxsplit so that easter eggs are excluded, e.g. youngja03, graype01
                bats, throws = (s.split(":", maxsplit=1)[1] for s in line_str.split("\t")[:2])
                self.info.loc[:, "Batting Hand"] = bats.strip()
                self.info.loc[:, "Throwing Hand"] = throws.strip()

            elif (
                ("kg)" in line_str or "cm," in line_str or "cm)" in line_str)
                and "(" in line_str
                and ")" in line_str
            ):
                line_str = line_str.split("(", maxsplit=1)[0]
                # need to handle potential for missing height or weight
                for measurement in line_str.split(",", maxsplit=1):
                    if "-" in measurement:
                        feet, inches = measurement.strip().split("-", maxsplit=1)
                        self.info.loc[:, "Height (in.)"] = int(feet) * 12 + int(inches)
                    elif "lb" in measurement:
                        self.info.loc[:, "Weight (lbs.)"] = measurement.strip("\xa0 lb")

            elif line_str.startswith("Born"):
                if " in " in line_str:
                    birth_date, birth_place = line_str.split(" in ", maxsplit=1)
                else:  # no birth place listed
                    birth_date, birth_place = line_str, ""

                # handle birth dates
                if "(Date unknown)" not in birth_date:
                    birth_date = birth_date.split(":", maxsplit=1)[1].strip()
                    # can have two spaces if date is only month and year
                    self.info.loc[:, "Birth Date"] = reformat_date(birth_date.replace("  ", " "))

                # get birth datetime for later use
                try:
                    birth_datetime = datetime.strptime(birth_date, "%B %d, %Y")
                except ValueError:
                    # date is not formatted as expected
                    pass

                # handle birth places
                if "Ocean" in birth_place:  # handle players born at sea
                    self.info.loc[:, "Birth Country"] = birth_place.strip()
                else:
                    birth_place = birth_place[:-2]  # remove text representation of country flag
                    birth_place_split = birth_place.split(", ")
                    if len(birth_place_split) == 1:
                        # city and/or state/country could be missing, so there's nothing to do
                        dev_alert(f'{self.id}: malformed birth place "{birth_place.strip()}"')
                        continue
                    if len(birth_place_split) == 2:
                        birth_city, birth_state_or_country = birth_place.split(", ", maxsplit=1)
                        self.info.loc[:, "Birth City"] = birth_city
                        # US states are represented by abbreviations
                        if len(birth_state_or_country) == 2:
                            self.info.loc[:, "Birth State/Province"] = birth_state_or_country
                            self.info.loc[:, "Birth Country"] = "U.S."
                        else:
                            self.info.loc[:, "Birth Country"] = birth_state_or_country
                    elif len(birth_place_split) == 3:
                        # likely Canada with province abbreviation and country name
                        birth_city, birth_province, birth_country = birth_place.split(
                            ", ", maxsplit=2
                        )
                        self.info.loc[:, "Birth City"] = birth_city
                        self.info.loc[:, "Birth State/Province"] = birth_province
                        self.info.loc[:, "Birth Country"] = birth_country

            elif line_str.startswith("Died"):
                if "in" in line_str:
                    death_date, death_place = line_str.split(" in ", maxsplit=1)
                else:  # no death place listed
                    death_date, death_place = line_str, ""

                # handle death dates
                death_date = death_date.split(":", maxsplit=1)[1].strip()
                self.info.loc[:, "Death Date"] = reformat_date(death_date)
                try:
                    death_datetime = datetime.strptime(death_date, "%B %d, %Y")
                    age = relativedelta(death_datetime, birth_datetime)
                    self.info.loc[:, "Age At Death"] = f"{age.years}y-{age.months}m-{age.days}d"
                    self.info.loc[:, "Age At Death (Days)"] = (death_datetime - birth_datetime).days
                except (
                    ValueError,  # date is not formatted as expected
                    UnboundLocalError,  # birth_datetime has improper format, was not defined
                ):
                    pass
                # remove current age cols, since they are inaccurate
                self.info.loc[:, "Age"] = None
                self.info.loc[:, "Age (Days)"] = np.nan

                # handle death places
                if "Ocean" in death_place:  # handle players born at sea differently
                    self.info.loc[:, "Death Country"] = death_place.strip()
                elif ", " in death_place:
                    death_city, death_state_or_country = death_place.split(", ", maxsplit=1)
                    self.info.loc[:, "Death City"] = death_city
                    if len(death_state_or_country) == 2:
                        self.info.loc[:, "Death State/Province"] = death_state_or_country
                        self.info.loc[:, "Death Country"] = "U.S."
                    else:
                        self.info.loc[:, "Death Country"] = death_state_or_country
                elif death_place != "":  # only state/country listed
                    if len(death_place) == 2:  # states are represented by abbreviations
                        self.info.loc[:, "Death State/Province"] = death_place
                        self.info.loc[:, "Death Country"] = "U.S."
                    else:
                        self.info.loc[:, "Death Country"] = death_place

            elif line_str.startswith("Draft"):
                # only use final time player was drafted
                draft_line = clean_spaces(line_str.split("and  the")[-1])

                draft_team, draft_line = draft_line.split(" in the ")
                draft_round = draft_line[0:2].strip("snrt")
                try:
                    # draft_team includes "Drafted by the" if player was drafted once
                    draft_team = draft_team.rsplit("the ", maxsplit=1)[1]
                except IndexError:
                    # draft_team is just the team name if drafted multiple times
                    pass
                self.info.loc[:, "Draft Team"] = draft_team.strip()
                self.info.loc[:, "Draft Round"] = draft_round

                try:
                    self.info.loc[:, "Draft Pick"] = str_between(draft_line, "round (", ")").strip(
                        "stndrh"
                    )
                    draft_line = draft_line.split(") of the ", maxsplit=1)[1]
                    draft_year, draft_type = draft_line.split(" ", maxsplit=1)
                except ValueError:
                    # if the pick is not listed (after 1st round)
                    draft_line = draft_line.split("round of the ", maxsplit=1)[1]
                    draft_year, draft_type = draft_line.split(" ", maxsplit=1)
                self.info.loc[:, "Draft Year"] = draft_year
                self.info.loc[:, "Draft Type"] = draft_type.split(" from ", maxsplit=1)[0].strip(
                    "."
                )

            elif "School:" in line_str:
                school_type, school_name = line_str.split(": ", maxsplit=1)
                self.info.loc[:, f"{school_type}s"] = f'"{school_name}"'

            elif "Schools" in line_str:
                col, school_list = line_str.split(": ", maxsplit=1)
                # ")" included because there are also commas in the names of the schools' cities
                schools = [school.strip() for school in school_list.split("),")]
                # restore ")" where necessary
                schools = [school + ")" if school[-1] != ")" else school for school in schools]
                schools_str = '", "'.join(schools)
                self.info.loc[:, col] = f'"{schools_str}"'

            elif line_str.startswith("Debut") and "AL/NL" not in line_str:
                debut_date = str_between(line_str, "Debut:", "(").strip()
                self.info.loc[:, "Debut Date"] = reformat_date(debut_date)
                try:
                    debut_datetime = datetime.strptime(debut_date, "%B %d, %Y")
                    age = relativedelta(debut_datetime, birth_datetime)
                    self.info.loc[:, "Debut Age"] = f"{age.years}y-{age.months}m-{age.days}d"
                    self.info.loc[:, "Debut Age (Days)"] = (debut_datetime - birth_datetime).days
                except (ValueError, UnboundLocalError):
                    # incomplete debut date or missing birth date, respectively
                    pass

                debut_game_link = line.find_all("a", href=True)[-1]["href"]
                if "/boxes/" in debut_game_link:
                    self.info.loc[:, "Debut Game ID"] = str_between(
                        debut_game_link, "/", ".", anchor="end"
                    )

                debut_rank = str_between(line_str, " ", " in major league history", anchor="end")
                # "(" is at the start if age is not listed
                debut_rank = debut_rank.strip("(stndrh ")
                self.info.loc[:, "Debut Rank"] = int(debut_rank.replace(",", ""))

            elif line_str.startswith("Last Game"):
                if "(" in line_str:
                    # omit player's age at the time, will be calculated below
                    last_game = str_between(line_str, "Last Game:", "(").strip()
                else:
                    last_game = line_str.replace("Last Game:", "").strip()
                self.info.loc[:, "Last Game"] = reformat_date(last_game)
                try:
                    last_game_datetime = datetime.strptime(last_game, "%B %d, %Y")
                    age = relativedelta(last_game_datetime, birth_datetime)
                    self.info.loc[:, "Last Game Age"] = f"{age.years}y-{age.months}m-{age.days}d"
                    self.info.loc[:, "Last Game Age (Days)"] = (
                        last_game_datetime - birth_datetime
                    ).days
                except (
                    ValueError,  # incomplete last game date
                    UnboundLocalError,  # birth_datetime has improper format, was not defined
                ):
                    continue

                last_game_link = line.find_all("a", href=True)[-1]["href"]
                if "/boxes/" in last_game_link:
                    self.info.loc[:, "Last Game ID"] = str_between(
                        last_game_link, "/", ".", anchor="end"
                    )

            elif line_str.startswith("Hall of Fame"):
                hof_type, hof_year = line_str.split(" in ", maxsplit=1)
                self.info.loc[:, "HOF Year"] = hof_year[:4]
                self.info.loc[:, "HOF Type"] = hof_type.split("as ", maxsplit=1)[1]
                if "BBWAA" in line_str:
                    yes, total = line_str.split(" on ", maxsplit=1)[1].split("/", maxsplit=1)
                    percentage = int(yes) / int(total.split(" ballots", maxsplit=1)[0])
                    self.info.loc[:, "HOF %"] = round(percentage, 4)

            elif line_str.startswith("Rookie Status") and "Still Intact" not in line_str:
                season = str_between(line_str, "Exceeded rookie limits during ", " season")
                self.info.loc[:, "Exceeded Rookie Limits"] = season

            elif line_str.startswith("Full Name"):
                self.info.loc[:, "Full Name"] = line_str.replace("Full Name: ", "").strip()

            elif line_str.startswith("Relatives"):
                relative_links = [player["href"] for player in line.find_all("a", href=True)]
                player_ids = [str_between(link, "/", ".", anchor="end") for link in relative_links]
                # relatives could also be managers
                is_player = [str_between(link, "/", "/") == "players" for link in relative_links]
                relations = line_str.replace("Relatives: ", "").split(";")
                # associate ids with players using their shared order
                for r in relations:
                    relation, players = r.strip().split(" of ", maxsplit=1)
                    player_count = players.count(", ") + 1
                    # swap the direction of some relationships, e.g. "Father of" refers to his Son
                    relation = RELATIVES_DICT.get(relation, None)
                    if relation is not None:
                        for _ in range(player_count):
                            relative = player_ids.pop(0)
                            if is_player.pop(0):
                                self.relatives[relation].append(relative)
                    else:
                        dev_alert(f'{self.id}: unexpected relation "{r.strip()}"')

    def _scrape_bling(self, player_bling: Tag) -> None:
        """Populates `self.bling`."""
        self.bling.loc[:, "Player"] = self.name
        self.bling[[*BLING_DICT.values()]] = 0

        if player_bling is None:
            return
        for line in player_bling.find_all("a"):
            bling = line.text
            if "x " in bling:
                times, bling = bling.split("x ", maxsplit=1)
            else:
                times = "1"
            bling_val = BLING_DICT.get(bling, None)

            if bling_val is not None:
                self.bling.loc[:, bling_val] = int(times)
            elif "World Series" in bling:
                # if a player has just one ring, the year is included in the bling
                self.bling.loc[:, "WS Wins"] = 1
            elif "Hall of Fame" not in bling:  # HOF is handled in the bio
                dev_alert(f'{self.id}: unexpected bling element "{bling}"')

    def _find_career_earnings(self, table: Tag) -> None:
        """Populates `self._yearly_salaries` from salaries table."""
        table = soup_from_comment(table, only_if_table=True)
        records = []

        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all()]
            records.append(record)
        num_columns = len(records[0])
        del records[0]  # delete header row

        for record in records:
            # if the # of columns is right and the salary column has a value
            if len(record) == num_columns and record[3]:
                # skip future option years, indicated by a leading asterisk
                if record[3][0] == "*":
                    continue
                # trailing asterisk indicates inconsistent reports, but I'll allow it
                record[3] = record[3].strip("$*")
                # += because years can have multiple rows, like salary and a paid buyout
                self._yearly_salaries[record[0]] += int(record[3].replace(",", ""))

    @staticmethod
    def _merge_dataframes(*to_merge: pd.DataFrame) -> pd.DataFrame:
        """Joins `to_merge` DataFrames into one DataFrame."""
        merged_df = to_merge[0]
        for df in to_merge[1:]:
            merged_df = merged_df.join(df.reset_index(drop=True))
        return merged_df

    def _finish_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds player name, player ID, salary, and team IDs to `df`, and corrects dtypes."""
        df.loc[:, "Player ID"] = self.id
        df.loc[:, "Player"] = self.name
        df["Salary"] = df["Season"].apply(lambda x: self._yearly_salaries.get(x, None))

        df.loc[
            ((~df["Team"].isna()) & (df["Season"] != "Career Totals")),
            "Team ID",
        ] = (
            df["Team"] + df["Season"]
        )
        # remove team ids from multi-team season summary rows, e.g. 2TM
        df.loc[
            ((~df["Team ID"].isna()) & (df["Team"].str.fullmatch(MULTI_TEAM_REGEX))),
            "Team ID",
        ] = None

        df = convert_numeric_cols(df)
        # season could be int64 if total rows are missing, e.g. hawkiro01, johns11
        if df["Season"].dtype == "int64":
            df["Season"] = df["Season"].astype(str)
        return df

    @staticmethod
    def _scrape_standard_batting(table: Tag) -> tuple[pd.DataFrame, int]:
        """Scrapes standard batting stats from `table`."""
        h_df_1 = Player._table_to_df(table, add_game_type=True)
        h_df_1.rename(
            columns={
                "WAR": "Batting bWAR",
                "Lg": "League",
            },
            inplace=True,
        )
        h_df_1 = Player._process_awards_column(h_df_1)
        h_df_1 = Player._process_career_totals(h_df_1)
        h_df_1.loc[(h_df_1["Season"] == "162 Game Avg") | (h_df_1["Pos"] == ""), "Pos"] = None

        # count the team/league summary rows which won't be under the advanced table
        summary_rows = h_df_1.loc[
            (h_df_1["Season"] == "Career Totals")
            & (h_df_1["Game Type"] == "Regular Season")
            & ((~h_df_1["Team"].isna()) | (~h_df_1["League"].isna()))
        ]
        advanced_batting_buffer = len(summary_rows) + 1  # add one for 162 game average row
        return h_df_1, advanced_batting_buffer

    @staticmethod
    def _scrape_standard_pitching(table: Tag) -> tuple[pd.DataFrame, int]:
        """Scrapes standard pitching stats from `table`."""
        p_df_1 = Player._table_to_df(table, add_game_type=True)
        p_df_1.rename(columns={"WAR": "Pitching bWAR", "Lg": "League"}, inplace=True)

        p_df_1 = Player._process_awards_column(p_df_1)
        p_df_1 = Player._process_career_totals(p_df_1)
        p_df_1["IP"].apply(change_innings_notation)

        # count the team/league summary rows which won't be under the advanced table
        summary_rows = p_df_1.loc[
            (p_df_1["Season"] == "Career Totals")
            & (p_df_1["Game Type"] == "Regular Season")
            & ((~p_df_1["Team"].isna()) | (~p_df_1["League"].isna()))
        ]
        advanced_pitching_buffer = len(summary_rows) + 1  # add one for 162 game average row
        return p_df_1, advanced_pitching_buffer

    def _scrape_standard_fielding(self, table: Tag) -> None:
        """Scrapes standard fielding stats from `table`."""
        self.fielding = Player._table_to_df(table, add_game_type=True)
        self.fielding.rename(columns={"Lg": "League", "Pos": "Position"}, inplace=True)

        self.fielding = Player._process_awards_column(self.fielding)
        self.fielding.loc[self.fielding["Position"] == "", "Position"] = None
        # set by-position totals rows to be labeled as such, the "Positions" column already exists
        career_position_totals_mask = self.fielding["Season"].str.contains("(", regex=False)
        self.fielding.loc[career_position_totals_mask, "Season"] = "Career Totals"
        if "Inn" in self.fielding.columns:
            self.fielding["Inn"].apply(change_innings_notation)

    @staticmethod
    def _process_awards_column(df_1: pd.DataFrame) -> pd.DataFrame:
        """Adds stats that are found in `df_1`'s awards column as their own columns."""
        df_1.loc[:, ["AS", "GG", "SS", "LCS MVP", "WS MVP"]] = 0
        df_1.loc[:, ["MVP Finish", "CYA Finish", "ROY Finish"]] = None

        last_season = ""
        for _, row in df_1.iterrows():
            # in standard fielding, one season can be listed multiple times (one per position)
            # we want to skip these duplicate awards entries
            if last_season == row["Season"]:
                continue
            last_season = row["Season"]

            awards = row["Awards"].split(",")
            season_mask = df_1["Season"] == row["Season"]
            for award in awards:
                if award in {"AS", "GG", "SS", "WS MVP"}:
                    df_1.loc[season_mask, award] += 1
                elif award in {"ALCS MVP", "NLCS MVP"}:
                    df_1.loc[season_mask, "LCS MVP"] += 1
                else:
                    for col in ("MVP", "CYA", "ROY"):
                        if col in award:
                            df_1.loc[season_mask, f"{col} Finish"] = int(award[4:])

        # summary rows should have missing values; totals can be found in Player.bling
        df_1.loc[df_1["Team"].isna(), ["AS", "GG", "SS", "LCS MVP", "WS MVP"]] = None
        return df_1

    @staticmethod
    def _process_career_totals(df_1: pd.DataFrame) -> pd.DataFrame:
        """
        Moves abbreviations from `df_1`'s `Season` column into the `Team` or
        `League` columns on franchise/league career totals rows.
        """
        # find franchise and league career total rows
        abbreviations = df_1["Season"].str.split(" (", regex=False, n=1).str[0]
        is_league_mask = abbreviations.isin(LEAGUE_ABVS)
        is_total_mask = df_1["Season"].str.contains("(", regex=False)  # can be team or league
        league_summary_mask = is_total_mask & is_league_mask
        team_summary_mask = is_total_mask & (~is_league_mask)

        # move franchise and league abbreviations into their respective columns
        df_1.loc[league_summary_mask, "League"] = abbreviations.loc[league_summary_mask]
        df_1.loc[team_summary_mask, "Team"] = abbreviations.loc[team_summary_mask]
        df_1.loc[is_total_mask, "Season"] = "Career Totals"
        return df_1

    @staticmethod
    def _scrape_value_table(table) -> pd.DataFrame:
        """Scrapes value batting/pitching stats from `table`."""
        df_2 = Player._table_to_df(table, add_game_type=False)
        df_2.drop(
            columns=[
                "Season",
                "Age",
                "Team",
                "Lg",
                "PA",
                "IP",
                "G",
                "GS",
                "R",
                "WAR",
                "Pos",
                "Awards",
            ],
            inplace=True,
            errors="ignore",
        )
        return df_2

    @staticmethod
    def _scrape_advanced_table(table, buffer: int) -> pd.DataFrame:
        """Scrapes advanced batting/pitching stats from `table`."""
        df_3 = Player._table_to_df(table, add_game_type=False, buffer=buffer)
        df_3.drop(
            columns=["Season", "Age", "Team", "Lg", "PA", "IP", "rOBA", "Rbat+", "Pos", "Awards"],
            inplace=True,
            errors="ignore",
        )

        # convert cWPA from percentage to float
        if "cWPA" in df_3.columns:
            df_3.loc[:, "cWPA"] = df_3["cWPA"].str.strip("%")
            df_3.loc[:, "cWPA"] = pd.to_numeric(df_3["cWPA"], errors="coerce") / 100
            df_3.loc[:, "cWPA"] = df_3["cWPA"].astype(float).round(4)
        return df_3

    @staticmethod
    def _table_to_df(table: Tag, add_game_type: bool, buffer: int = 0) -> pd.DataFrame:
        """
        Turns a player stats table into a DataFrame.
        If `add_game_type` == True, the `Game Type` column will be added to the DataFrame.
        `buffer` is the number of blank rows to add after regular season stats to correct
        for the lack franchise/league summary rows which other DataFrames have.
        """
        table = soup_from_comment(table, only_if_table=True)

        # scrape regular season and postseason tabs
        reg_records, post_records = ([] for _ in range(2))
        tables = 0
        postseason_included = False

        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            # skip upper header row, if applicable
            if record[0] == "":
                continue

            # count the number of column label rows, and therefore tables, seen
            if record[0] == "Season":
                tables += 1
            assert tables in {1, 2}
            # postseason stats rows include this identifier
            if "_post." in row.get("id", ""):
                postseason_included = True

            if tables == 1:  # on the first table (presumably regular season)
                reg_records.append(record)
            elif tables == 2:  # on the second table (postseason)
                post_records.append(record)

        reg_column_names = reg_records.pop(0)
        if tables == 2:
            post_column_names = post_records.pop(0)
            reg_df = pd.DataFrame(reg_records, columns=reg_column_names)
            post_df = pd.DataFrame(post_records, columns=post_column_names)
            reg_df = Player._clean_dataframe(reg_df)
            post_df = Player._clean_dataframe(post_df)
            if add_game_type:
                reg_df.loc[:, "Game Type"] = "Regular Season"
                post_df.loc[:, "Game Type"] = "Postseason"
            if buffer > 0:
                empty_cols = [[None] * len(reg_df.columns)] * buffer
                blank_rows = pd.DataFrame(empty_cols, columns=reg_df.columns)
                reg_df = pd.concat((reg_df, blank_rows))
            df = pd.concat((reg_df, post_df), ignore_index=True)
        else:
            df = pd.DataFrame(reg_records, columns=reg_column_names)
            df = Player._clean_dataframe(df)
            if add_game_type:
                # this could be a player who's only appeared in the postseason, e.g. kigerma01
                if postseason_included:
                    df.loc[:, "Game Type"] = "Postseason"
                else:
                    df.loc[:, "Game Type"] = "Regular Season"
        return df

    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans a stats DataFrame."""
        # remove any missed seasons that are included in the table
        df = df.loc[~df["Team"].isnull()]
        # remove any spacer rows or MLB average rows
        df = df.loc[~df["Season"].isin({"", "MLB Average"})]

        # shift career totals and 162 game avg rows which are misaligned by default
        original_seasons_column = df["Season"].copy()
        shift_rows_mask = (df["Season"].str.contains(" Yr", regex=False)) | (
            df["Season"] == "162 Game Avg"
        )
        df.loc[shift_rows_mask] = df.loc[shift_rows_mask].shift(3, axis="columns")
        # restore season column, which should not be shifted
        df.loc[:, "Season"] = original_seasons_column
        # remove the shifted season values from the league column
        df.loc[shift_rows_mask, "Lg"] = None

        # properly label the overall career totals row
        df.loc[df["Season"].str.contains("Yrs*$", na=False), "Season"] = "Career Totals"
        return df

    def _count_years_played(self) -> None:
        """Adds `"Years Played"` to `self.info`."""
        years_played = set()
        years_played.update(self.batting["Season"].values.tolist())
        years_played.update(self.pitching["Season"].values.tolist())
        years_played.update(self.fielding["Season"].values.tolist())
        # filter out "Career Totals", "162 Game Avg", and anything else that isn't a year
        years_played = set(filter(lambda x: x.isnumeric(), years_played))
        self.info["Years Played"] = len(years_played)

    def _find_teams_info(self) -> None:
        """Adds `"Teams Played For"` and `"Most Teams in a Year"` to `self.info`."""
        bat_teams = Player._scrape_teams_from_df(self.batting) if not self.batting.empty else []
        pit_teams = Player._scrape_teams_from_df(self.pitching) if not self.pitching.empty else []
        fld_teams = Player._scrape_teams_from_df(self.fielding) if not self.fielding.empty else []
        self.teams = list(dict.fromkeys(bat_teams + pit_teams + fld_teams))
        self.teams = sorted(self.teams, key=lambda x: (x[1], x[0]))

        if len(self.teams) == 0:
            return
        seasons = [x[1] for x in self.teams]
        self.info["Most Teams in a Year"] = Counter(seasons).most_common(1)[0][1]
        franchises = [abv_man.franchise_abv(abv, int(year)) for abv, year in self.teams]
        self.info["Teams Played For"] = len(dict.fromkeys(franchises))

    @staticmethod
    def _scrape_teams_from_df(df: pd.DataFrame) -> list[tuple[str, str]]:
        """Returns a list of the teams which appear in `df`."""
        season_rows = df.loc[df["Season"].str.fullmatch(SEASON_REGEX)]
        # remove multi-team season summary rows
        season_rows = season_rows[~season_rows["Team"].str.fullmatch(MULTI_TEAM_REGEX)]
        teams = list(zip(season_rows["Team"], season_rows["Season"]))  # ("SEA", 2019)
        teams = list(dict.fromkeys(teams))
        return teams
