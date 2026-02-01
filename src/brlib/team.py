#!/usr/bin/env python3

"""Defines Team class."""

import re

import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi import Response

from ._helpers.constants import (TEAM_BATTING_COLS, TEAM_FIELDING_COLS,
                                 TEAM_INFO_COLS, TEAM_PITCHING_COLS,
                                 TEAM_URL_REGEX, TEAM_REPLACEMENTS, VENUE_REPLACEMENTS, RANGE_TEAM_REPLACEMENTS)
from ._helpers.inputs import validate_team_list
from ._helpers.no_hitter_dicts import nhd
from ._helpers.requests_manager import req_man
from ._helpers.utils import (change_innings_notation, clean_spaces,
                             convert_numeric_cols, report_on_exc,
                             runtime_typecheck, scrape_player_ids,
                             soup_from_comment, str_between)
from .options import dev_alert, options, print_page


class Team:
    """
    Statistics and information from a team. Can be initialized by specifying `team`, and `season`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded team page. If neither of these sets of parameters are given, an exception is raised.

    ## Parameters

    * `team`: `str`, default `""`

        The team's abbreviation. Era adjustment is not used, and aliases are not accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

    * `season`: `str`, default `""`

        The year in which the team played in YYYY format (e.g. `"2022"`).

    * `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

        A previously loaded team page.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Team.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `update_venue_names`: `bool` or `None`, default `None`

        Whether to standardize venue name such that venues are identified by one name. If no value is passed, the value of `options.update_venue_names` is used.

    ## Attributes

    * `id`: `str`

        The unique identifier for the team made up of its abbreviation and season (e.g. `"SEA2017"`).

    * `name`: `str`

        The team's name (e.g. `"2017 Seattle Mariners"`).

    * `info`: `pandas.DataFrame`

        Contains information about the team, its results, and its personnel.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teaminfo-and-teamsetinfo)

    * `batting`: `pandas.DataFrame`

        Contains the team's batting and baserunning stats from the two batting tables.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teambatting-and-teamsetbatting)

    * `pitching`: `pandas.DataFrame`

        Contains the team's pitching stats from the two pitching tables.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teampitching-and-teamsetpitching)

    * `fielding`: `pandas.DataFrame`

        Contains the team's fielding stats from the standard fielding table.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#teamfielding-and-teamsetfielding)

    * `players`: `list[str]`

        A list of the players who played for the team. Can be an input to `get_players`.

    ## Example

    Load a team:

    ```
    >>> br.Team("SDP", "2022").name
    '2022 San Diego Padres'
    ```

    ## Methods

    * [`Team.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Team.add_no_hitters)
    * [`Team.update_team_names`](https://github.com/john-bieren/brlib/wiki/Team.update_team_names)
    * [`Team.update_venue_names`](https://github.com/john-bieren/brlib/wiki/Team.update_venue_names)
    """
    @runtime_typecheck
    def __init__(
            self,
            team: str = "",
            season: str = "",
            page: Response = Response(),
            add_no_hitters: bool | None = None,
            update_team_names: bool | None = None,
            update_venue_names: bool | None = None
            ) -> None:
        if add_no_hitters is None:
            add_no_hitters = options.add_no_hitters
        if update_team_names is None:
            update_team_names = options.update_team_names
        if update_venue_names is None:
            update_venue_names = options.update_venue_names

        if page.url == "":
            if any(s == "" for s in (team, season)):
                raise ValueError("insufficient arguments")

            teams = validate_team_list([(team, season)])
            if len(teams) == 0:
                raise ValueError("invalid arguments")
            page = Team._get_team(teams[0])
        else:
            if not re.match(TEAM_URL_REGEX, page.url):
                raise ValueError("page does not contain a team")

        self.name = ""
        self.id = str_between(page.url, "teams/", ".shtml").replace("/", "")
        self.info, self.batting, self.pitching , self.fielding = (pd.DataFrame() for _ in range(4))
        self.players = []
        self._url = page.url

        self._scrape_team(page)
        print_page(self.name)

        if add_no_hitters:
            self.add_no_hitters()
        if update_team_names:
            self.update_team_names()
        if update_venue_names:
            self.update_venue_names()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if self._url == "":
            return "Team()"
        team = self.id[:-4]
        season = self.id[-4:]
        return f"Team('{team}', '{season}')"

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `Team.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> t = br.Team("BOS", "1904")
        >>> t.pitching[["Player", "NH", "PG", "CNH"]]
                    Player  NH  PG  CNH
        0         Cy Young NaN NaN  NaN
        1    George Winter NaN NaN  NaN
        2  Jesse Tannehill NaN NaN  NaN
        3   Norwood Gibson NaN NaN  NaN
        4     Bill Dinneen NaN NaN  NaN
        5      Team Totals NaN NaN  NaN
        >>> t.add_no_hitters()
        >>> t.pitching[["Player", "NH", "PG", "CNH"]]
                    Player   NH   PG  CNH
        0         Cy Young  1.0  1.0  0.0
        1    George Winter  0.0  0.0  0.0
        2  Jesse Tannehill  1.0  0.0  0.0
        3   Norwood Gibson  0.0  0.0  0.0
        4     Bill Dinneen  0.0  0.0  0.0
        5      Team Totals  2.0  1.0  0.0
        ```
        """
        success = nhd.populate()
        if not success:
            return
        self.pitching.loc[:, ["NH", "PG", "CNH"]] = 0

        inh_list = nhd.team_inh_dict.get(self.id, [])
        pg_list = nhd.team_pg_dict.get(self.id, [])
        cnh_list = nhd.team_cnh_dict.get(self.id, [])

        # add individual no-hitters
        for col, inh_list in (
            ("NH", inh_list),
            ("PG", pg_list)
            ):
            for player, game_type in inh_list:
                self.pitching.loc[
                    # player totals
                    ((self.pitching["Player ID"] == player) &
                     (self.pitching["Game Type"].str.startswith(game_type))) |
                    # team totals row
                    ((self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Game Type"].str.startswith(game_type))),
                    col
                ] += 1

        # add combined no-hitters
        games_logged = []
        for player, game_type, game_id in cnh_list:
            # player totals
            self.pitching.loc[
                ((self.pitching["Player ID"] == player) &
                 (self.pitching["Game Type"].str.startswith(game_type))),
                "CNH"
            ] += 1
            # team totals row (only increment total once per game)
            # works when game_id is None because no team without box scores had multiple CNHs
            if game_id not in games_logged or game_id is None:
                self.pitching.loc[
                    ((self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Game Type"].str.startswith(game_type))),
                    "CNH"
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
        >>> t = br.Team("LAA", "2015")
        >>> t.info["Team"]
        0    Los Angeles Angels of Anaheim
        Name: Team, dtype: object
        >>> t.update_team_names()
        >>> t.info["Team"]
        0    Los Angeles Angels
        Name: Team, dtype: object
        ```
        """
        # replace old team names
        self.info.replace({"Team": TEAM_REPLACEMENTS}, inplace=True)
        self.batting.replace({"Team": TEAM_REPLACEMENTS}, inplace=True)
        self.pitching.replace({"Team": TEAM_REPLACEMENTS}, inplace=True)
        self.fielding.replace({"Team": TEAM_REPLACEMENTS}, inplace=True)

        # replace old team names within a certain range
        year = int(self.id[-4:])
        for start_year, end_year, old_name, new_name in RANGE_TEAM_REPLACEMENTS:
            if year not in range(start_year, end_year+1):
                continue
            name_dict = {old_name: new_name}
            self.info.replace({"Team": name_dict}, inplace=True)
            self.batting.replace({"Team": name_dict}, inplace=True)
            self.pitching.replace({"Team": name_dict}, inplace=True)
            self.fielding.replace({"Team": name_dict}, inplace=True)

        self.name = f"{self.id[-4:]} {self.info["Team"].values[0]}"

    def update_venue_names(self) -> None:
        """
        Standardizes venue name such that venues are identified by one name.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> t = br.Team("OAK", "2021")
        >>> t.info["Venue"]
        0    RingCentral Coliseum
        Name: Venue, dtype: object
        >>> t.update_venue_names()
        >>> t.info["Venue"]
        0    Oakland-Alameda County Coliseum
        Name: Venue, dtype: object
        ```
        """
        self.info.replace({"Venue": VENUE_REPLACEMENTS}, inplace=True)

    @staticmethod
    def _get_team(team: tuple[str, str]) -> Response:
        """Returns the page associated with a team and season."""
        abv, season = team
        endpoint = f"/teams/{abv}/{season}.shtml"
        return req_man.get_page(endpoint)

    @report_on_exc()
    def _scrape_team(self, page: Response) -> None:
        """Scrapes team info and batting, pitching, and fielding stats from `page`."""
        soup = bs(page.content, "lxml")

        # get team name, city
        page_title = soup.find("title").text
        season, remainder = page_title.split(" ", maxsplit=1)
        team_name = remainder.split(" Statistics", maxsplit=1)[0]
        self.name = " ".join((season, team_name))

        # gather team info
        self.info = pd.DataFrame({
            "Team": [team_name],
            "Season": [season],
            "Team ID": [self.id]
        })
        info = soup.find(id="info")
        bling = info.find(id="bling")
        self._scrape_info(info, bling)

        # check that the page has player stats
        content = soup.find(id="content")
        if ("No stats are currently available for this team." in content.text or # e.g. COT1932
            "These stats are for the players to appear in spring training games" in content.text):
            self.batting = self.batting.reindex(columns=TEAM_BATTING_COLS)
            self.pitching = self.pitching.reindex(columns=TEAM_PITCHING_COLS)
            self.fielding = self.fielding.reindex(columns=TEAM_FIELDING_COLS)
            return

        # gather player stats from the relevant tables
        page_tables = content.find_all("div", {"class": "table_wrapper"}, recursive=False)
        for table in page_tables:
            table_name = table.get("id")
            if table_name == "all_players_standard_batting":
                table_text = table.decode_contents().strip()
                table = bs(table_text, "lxml")
                h_df_1 = self._scrape_standard_table(table)

                h_df_1.rename(columns={"WAR": "Batting bWAR"}, inplace=True)

            elif table_name == "all_players_value_batting":
                table = soup_from_comment(table, only_if_table=True)
                h_df_2 = self._scrape_value_table(table)

            elif table_name == "all_players_standard_pitching":
                table_text = table.decode_contents().strip()
                table = bs(table_text, "lxml")
                p_df_1 = self._scrape_standard_table(table)

                p_df_1.rename(columns={"WAR": "Pitching bWAR"}, inplace=True)
                p_df_1["IP"].apply(change_innings_notation)

            elif table_name == "all_players_value_pitching":
                table = soup_from_comment(table, only_if_table=True)
                p_df_2 = self._scrape_value_table(table)

            elif table_name == "all_players_standard_fielding":
                table = soup_from_comment(table, only_if_table=True)
                self.fielding = self._scrape_standard_table(table)

                if "Inn" in self.fielding.columns:
                    self.fielding["Inn"].apply(change_innings_notation)

        # merge sorted dfs on index
        self.batting = h_df_1.merge(h_df_2, how="left", left_index=True, right_index=True)
        self.batting.loc[:, "Season"] = season
        self.batting.loc[:, "Team"] = team_name
        self.batting.loc[:, "Team ID"] = self.id
        self.batting = self.batting.reindex(columns=TEAM_BATTING_COLS)
        self.batting = convert_numeric_cols(self.batting)

        self.pitching = p_df_1.merge(p_df_2, how="left", left_index=True, right_index=True)
        self.pitching.loc[:, "Season"] = season
        self.pitching.loc[:, "Team"] = team_name
        self.pitching.loc[:, "Team ID"] = self.id
        self.pitching = self.pitching.reindex(columns=TEAM_PITCHING_COLS)
        self.pitching = convert_numeric_cols(self.pitching)

        self.fielding.loc[:, "Season"] = season
        self.fielding.loc[:, "Team"] = team_name
        self.fielding.loc[:, "Team ID"] = self.id
        self.fielding = self.fielding.reindex(columns=TEAM_FIELDING_COLS)
        self.fielding = convert_numeric_cols(self.fielding)

        self.players = list(dict.fromkeys(self.players))

    def _scrape_info(self, info: Tag, bling: Tag | None) -> None:
        """Populates `self.info` with data from `info` and `bling`."""
        for line in info.find_all("p"):
            line_str = line.text.replace("\n", "").replace("\t", " ").replace("\xa0", " ")

            if "Record" in line_str:
                team_record = str_between(line_str, "Record:", ",").strip().split("-")
                self.info.loc[:, "Wins"] = team_record[0]
                self.info.loc[:, "Losses"] = team_record[1]
                self.info.loc[:, "Ties"] = team_record[2] if len(team_record) > 2 else 0

                if "Finished" in line_str: # if season is complete
                    division_finish = str_between(line_str, "Finished", "in").strip()
                else:
                    division_finish = str_between(line_str, ",", "place").strip().split()[0]
                self.info.loc[:, "Division Finish"] = division_finish.strip("stndrh")

                if "(Schedule" in line_str:
                    division = str_between(line_str, " in ", "(Schedule")
                else:
                    division = line_str.rsplit(" in ", maxsplit=1)[1]
                self.info.loc[:, "Division"] = division.strip().replace("_", " ")

            elif "Postseason" in line_str:
                latest_series_result = str_between(line_str, "Postseason:", "(").strip()
                self.info.loc[:, "Postseason Finish"] = clean_spaces(latest_series_result)

            # switching to startswith; nested p tags result in overlapping matches for "if str in"
            elif line_str.startswith("Manager"):
                managers = line_str.split(":", maxsplit=1)[1]
                self.info.loc[:, "Managers"] = clean_spaces(managers).replace(" , ", ", ")

            elif line_str.split(":", maxsplit=1)[0] in {
                    "President",
                    "General Manager",
                    "Farm Director",
                    "Scouting Director",
                    "Ballpark"
                    }:
                col, value = line_str.split(":", maxsplit=1)
                col = "Venue" if col == "Ballpark" else col # for consistency across library
                self.info.loc[:, col] = clean_spaces(value)

            elif line_str.startswith("Attendance"):
                self.info.loc[:, "Attendance"] = str_between(line_str, "Attendance:", "(").strip()
                self.info.loc[:, "Attendance Rank"] = str_between(line_str, "(", ")")

            elif line_str.startswith("Park Factors"):
                # if park factors are last info item, this may be included in line_str
                line_str = line_str.replace("More team info, park factors, postseason, & more", "")
                multi_year = one_year = ""
                if "Multi-year:" in line_str:
                    if "One-year" in line_str:
                        multi_year = str_between(line_str, "Multi-year:", "One-year:")
                        one_year = line_str.split("One-year:")[1]
                    else:
                        multi_year = line_str.split("Multi-year:")[1]
                else:
                    one_year = line_str.split("One-year:")[1]

                my_bat = my_pit = oy_bat = oy_pit = ""
                if multi_year != "":
                    my_bat, my_pit = multi_year.strip().split(", ")
                    my_bat = my_bat.split(" - ", maxsplit=1)[1]
                    my_pit = my_pit.split(" - ", maxsplit=1)[1]
                if one_year != "":
                    oy_bat, oy_pit = one_year.strip().split(", ")
                    oy_bat = oy_bat.split(" - ", maxsplit=1)[1]
                    oy_pit = oy_pit.split(" - ", maxsplit=1)[1]
                self.info.loc[:, "Multi-Year Batting Park Factor"] = my_bat
                self.info.loc[:, "Multi-Year Pitching Park Factor"] = my_pit
                self.info.loc[:, "One-Year Batting Park Factor"] = oy_bat
                self.info.loc[:, "One-Year Pitching Park Factor"] = oy_pit

            elif line_str.startswith("Pythagorean"):
                pyth_w, pyth_l = str_between(line_str, "Pythagorean W-L: ", ", ").split("-")
                self.info.loc[:, "Pythagorean Wins"] = pyth_w
                self.info.loc[:, "Pythagorean Losses"] = pyth_l

        # scrape bling section
        self.info.loc[:, ["Team Gold Glove", "Pennant", "World Series"]] = 0
        if bling is not None:
            for line in bling.find_all("a"):
                bling_name = line.text
                if bling_name == "Team Gold Glove":
                    self.info.loc[:, "Team Gold Glove"] = 1
                elif bling_name == "World Series Champions":
                    self.info.loc[:, "World Series"] = 1
                elif bling_name[-7:] == "Pennant":
                    self.info.loc[:, "Pennant"] = 1
                else:
                    dev_alert(f'{self.id}: unexpected bling element "{bling_name}"')

        self.info = self.info.reindex(columns=TEAM_INFO_COLS)
        self.info = convert_numeric_cols(self.info)

    def _scrape_standard_table(self, table: bs) -> pd.DataFrame:
        """Gathers team standard batting/pitching/fielding stats from `table`."""
        # scrape regular season and postseason tabs
        reg_records, post_records = ([] for _ in range(2))
        end_of_reg_table = found_postseason_table = False

        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]

            # figure out when the postseason table starts
            if "Totals" in record[1]:
                # we're in the final rows of regular season table
                end_of_reg_table = True
            if end_of_reg_table and record[0] == "Rk":
                # we're on another column label row and therefore a new table
                found_postseason_table = True

            if found_postseason_table:
                post_records.append(record)
            else:
                reg_records.append(record)

        # set up DataFrame
        # remove fielding upper category row (Standard, Total Zone, DRS, etc.) if it exists
        if len(reg_records[0]) != len(reg_records[1]):
            reg_records.pop(0)
        reg_column_names = reg_records.pop(0)
        if reg_column_names[3] == "Pos": # table has two columns named "Pos" by default
            reg_column_names[3] = "Position"
        if found_postseason_table:
            post_column_names = post_records.pop(0)
            reg_df = pd.DataFrame(reg_records, columns=reg_column_names)
            post_df = pd.DataFrame(post_records, columns=post_column_names)
            reg_df.loc[:, "Game Type"] = "Regular Season"
            post_df.loc[:, "Game Type"] = "Postseason"
            df_1 = pd.concat((reg_df, post_df))
        else:
            df_1 = pd.DataFrame(reg_records, columns=reg_column_names)
            df_1.loc[:, "Game Type"] = "Regular Season"

        # remove column label rows
        df_1 = df_1.loc[
            (df_1["Rk"] != "Rk") &
            (df_1["Player"] != "Standard")
        ]
        # remove handedness indicators
        df_1.loc[:, "Player"] = df_1["Player"].str.strip("*#")

        # missing position values should not be an empty string
        if "Pos" in df_1.columns:
            df_1.loc[df_1["Pos"] == "", "Pos"] = None
        # not elif because batting DataFrame has both columns
        if "Position" in df_1.columns:
            df_1.loc[df_1["Position"] == "", "Position"] = None

        # add player ids to table, excluding non-player rows
        player_id_column = scrape_player_ids(table)
        df_1.loc[df_1["Rk"] != "", "Player ID"] = player_id_column
        df_1.loc[df_1["Player ID"] == "nan", "Player ID"] = None
        self.players += player_id_column

        # sort table so that it can be joined to the value table with the expected alignment
        df_1.sort_values(by=["Game Type", "Player ID"], ascending=False, inplace=True)
        df_1.reset_index(drop=True, inplace=True)
        df_1 = Team._process_awards_column(df_1)
        return df_1

    @staticmethod
    def _process_awards_column(df_1: pd.DataFrame) -> pd.DataFrame:
        """Adds stats that are found in the awards column as their own columns in `df_1`."""
        df_1.loc[:, ["AS", "GG", "SS", "LCS MVP", "WS MVP"]] = 0
        df_1.loc[:, ["MVP Finish", "CYA Finish", "ROY Finish"]] = None
        # null out awards columns for totals rows
        df_1.loc[df_1["Player ID"].isna(), ["AS", "GG", "SS", "LCS MVP", "WS MVP"]] = None

        for _, row in df_1.iterrows():
            awards = row["Awards"].split(",")
            player_mask = df_1["Player ID"] == row["Player ID"]
            for award in awards:
                if award in {"AS", "GG", "SS", "WS MVP"}:
                    df_1.loc[player_mask, award] += 1
                elif award in {"ALCS MVP", "NLCS MVP"}:
                    df_1.loc[player_mask, "LCS MVP"] = 1
                else:
                    for col in ("MVP", "CYA", "ROY"):
                        if col in award:
                            df_1.loc[player_mask, f"{col} Finish"] = int(award[4:])
        return df_1

    def _scrape_value_table(self, table: bs) -> pd.DataFrame:
        """Gathers team value batting/pitching stats from `table`."""
        # scrape table
        records = []
        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            records.append(record)

        # set up DataFrame
        column_names = records.pop(0)
        df_2 = pd.DataFrame(records, columns=column_names)
        # remove column label rows
        df_2 = df_2.loc[df_2["Rk"] != "Rk"]

        # add player ids to table, excluding non-player rows
        player_id_column = scrape_player_ids(table)
        df_2.loc[df_2["Rk"] != "", "Player ID"] = player_id_column
        df_2.loc[df_2["Player ID"] == "nan", "Player ID"] = None
        self.players += player_id_column

        # sort table so that it can be joined to the standard table with the expected alignment
        df_2.sort_values(by="Player ID", ascending=False, inplace=True)
        # remove columns also found in standard table
        df_2.drop(
            columns=[
                "Rk", "Player", "Player ID", "Age", "PA", "IP",
                "G", "GS", "R", "WAR", "Pos", "Awards"
            ], inplace=True, errors="ignore"
        )
        df_2.reset_index(drop=True, inplace=True)
        return df_2
