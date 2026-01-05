#!/usr/bin/env python3

"""Defines Team class."""

import re

import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi import Response

from ._helpers.constants import (TEAM_BATTING_COLS, TEAM_FIELDING_COLS,
                                 TEAM_INFO_COLS, TEAM_PITCHING_COLS,
                                 TEAM_URL_REGEX)
from ._helpers.inputs import validate_team_list
from ._helpers.no_hitter_dicts import nhd
from ._helpers.requests_manager import req_man
from ._helpers.utils import (change_innings_notation, convert_numeric_cols,
                             report_on_exc, runtime_typecheck,
                             scrape_player_ids, soup_from_comment, str_between)
from .options import dev_alert, options, print_page


class Team():
    @runtime_typecheck
    def __init__(
            self,
            team: str = "",
            season: str = "",
            page: Response = Response(),
            add_no_hitters: bool | None = None
            ) -> None:
        if add_no_hitters is None:
            add_no_hitters = options.add_no_hitters

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
        if add_no_hitters:
            self.add_no_hitters()
        print_page(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if self._url == "":
            return "Team()"
        team = self.id[:-4]
        season = self.id[-4:]
        return f"Team('{team}', '{season}')"

    def add_no_hitters(self) -> None:
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
            if game_id not in games_logged:
                self.pitching.loc[
                    ((self.pitching["Player"] == "Team Totals") &
                     (self.pitching["Game Type"].str.startswith(game_type))),
                    "CNH"
                ] += 1
                games_logged.append(game_id)

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
            "Team ID": [self.id],
            # default values:
            "Playoff Finish": ["N/A"],
            "Pennant": [0],
            "Championship": [0]
        })
        info = soup.find(id="info")
        bling = info.find(id="bling")
        self._scrape_info(info, bling)

        # gather player stats from relevant tables
        content = soup.find(id="content")
        if "No stats are currently available for this team." in content.text: # e.g. COT1932
            self.batting = self.batting.reindex(columns=TEAM_BATTING_COLS)
            self.pitching = self.pitching.reindex(columns=TEAM_PITCHING_COLS)
            self.fielding = self.fielding.reindex(columns=TEAM_FIELDING_COLS)
            return

        page_tables = content.find_all("div", {"class": "table_wrapper"}, recursive=False)
        for table in page_tables:
            table_name = table.get("id")
            if table_name == "all_players_standard_batting":
                table_text = table.decode_contents().strip()
                table = bs(table_text, "lxml")
                h_df_1 = Team._scrape_standard_table(table)

                h_df_1.rename(columns={"WAR": "Batting bWAR"}, inplace=True)

            elif table_name == "all_players_value_batting":
                table = soup_from_comment(table, only_if_table=True)
                h_df_2 = Team._scrape_value_table(table)

            elif table_name == "all_players_standard_pitching":
                table_text = table.decode_contents().strip()
                table = bs(table_text, "lxml")
                p_df_1 = Team._scrape_standard_table(table)

                p_df_1.rename(columns={"WAR": "Pitching bWAR"}, inplace=True)
                p_df_1["IP"].apply(change_innings_notation)

            elif table_name == "all_players_value_pitching":
                table = soup_from_comment(table, only_if_table=True)
                p_df_2 = Team._scrape_value_table(table)

            elif table_name == "all_players_standard_fielding":
                table = soup_from_comment(table, only_if_table=True)
                self.fielding = Team._scrape_standard_table(table)

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

        self.players = self.players + list(self.batting["Player ID"].values)
        self.players = self.players + list(self.pitching["Player ID"].values)
        self.players = self.players + list(self.fielding["Player ID"].values)
        self.players = list(dict.fromkeys(self.players))
        self.players.remove("") # player id field from team totals rows

    def _scrape_info(self, info: Tag, bling: Tag | None) -> None:
        """Populates `self.info` with data from `info` and `bling`."""
        for line in info.find_all("p"):
            line_str = line.text.replace("\n", "").replace("\t", " ").replace("\xa0", " ")

            if "Record" in line_str:
                team_record = str_between(line_str, "Record:", ",").strip().split("-")
                self.info.loc[:, "Wins"] = team_record[0]
                self.info.loc[:, "Losses"] = team_record[1]
                self.info.loc[:, "Ties"] = team_record[2] if len(team_record) > 2 else 0

                if "Finished" in line_str: # if season is compelte
                    division_finish = str_between(line_str, "Finished", "in").strip()
                else:
                    division_finish = str_between(line_str, ",", "place").strip().split()[0]
                self.info.loc[:, "Division Finish"] = division_finish.strip("stndrh")

                try:
                    division = str_between(line_str, " in ", "(Schedule").strip()
                except ValueError:
                    division = line_str.rsplit(" in ", maxsplit=1)[1]
                self.info.loc[:, "Division"] = division.replace("_", " ")

            elif "Postseason" in line_str:
                latest_series_result = str_between(line_str, "Postseason:", "(").strip()
                self.info.loc[:, "Playoff Finish"] = latest_series_result.replace("  ", " ")
                if "World Series" in latest_series_result:
                    self.info.loc[:, "Pennant"] = 1
                    if "Won " in latest_series_result:
                        self.info.loc[:, "Championship"] = 1

            # switching to startswith; nested p tags result in overlapping matches for "if str in"
            elif line_str.startswith("Manager"):
                managers = line_str.split(":", maxsplit=1)[1]
                spaces_cleaned = " ".join(managers.split())
                self.info.loc[:, "Managers"] = spaces_cleaned.replace(" , ", ", ")

            elif line_str.split(":", maxsplit=1)[0] in set([
                    "Ballpark",
                    "President",
                    "General Manager",
                    "Farm Director",
                    "Scouting Director"
                    ]):
                col, value = line_str.split(":", maxsplit=1)
                spaces_cleaned = " ".join(value.split())
                self.info.loc[:, col] = spaces_cleaned

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

        # other than team gold gloves, bling only has redundant info (pennants, WS wins)
        self.info.loc[:, "Team Gold Glove"] = 0
        if bling is not None:
            for line in bling.find_all("a"):
                line_str = line.text
                if line_str == "Team Gold Glove":
                    self.info.loc[:, "Team Gold Glove"] = 1
                elif (line_str != "World Series Champions"
                      and line_str[-7:] != "Pennant"):
                    dev_alert(f'{self.id}: unexpected bling element "{bling}"')

        self.info = self.info.reindex(columns=TEAM_INFO_COLS)
        self.info = convert_numeric_cols(self.info)

    @staticmethod
    def _scrape_standard_table(table: bs) -> pd.DataFrame:
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
                # we're on another column header row and therefore a new table
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

        # remove column header rows
        df_1 = df_1.loc[
            (df_1["Rk"] != "Rk") &
            (df_1["Player"] != "Standard")
        ]
        # remove handedness indicators
        df_1.loc[:, "Player"] = df_1["Player"].str.strip("*#")
        # add player ids to table, exclude non-player rows
        player_id_column = scrape_player_ids(table)
        df_1.loc[df_1["Rk"] != "", "Player ID"] = player_id_column
        df_1.loc[df_1["Player ID"] == "nan", "Player ID"] = ""
        # sort values for consistency across tables
        df_1.sort_values(by=["Game Type", "Player ID"], ascending=False, inplace=True)
        df_1.reset_index(drop=True, inplace=True)
        df_1 = Team._process_awards_column(df_1)
        return df_1

    @staticmethod
    def _process_awards_column(df_1: pd.DataFrame) -> pd.DataFrame:
        """Adds stats that are found in the awards column as their own columns in `df_1`."""
        df_1.loc[:, ["AS", "GG", "SS", "LCS MVP", "WS MVP"]] = 0
        df_1.loc[:, ["MVP Finish", "CYA Finish", "ROY Finish"]] = None
        # null out awards columns for subtotals rows
        df_1.loc[
            (df_1["Player ID"] == "" ) & (df_1["Player"] != "Team Totals"),
            ["AS", "GG", "SS", "LCS MVP", "WS MVP"]
        ] = None
        team_totals_mask = df_1["Player"] == "Team Totals"
        # for team totals, set awards with voting info to 0 to count vote getters
        df_1.loc[team_totals_mask, ["MVP Finish", "CYA Finish", "ROY Finish"]] = 0

        for _, row in df_1.iterrows():
            awards = row["Awards"].split(",")
            player_mask = df_1["Player ID"] == row["Player ID"]
            for award in awards:
                if award in {"AS", "GG", "SS", "WS MVP"}:
                    df_1.loc[(player_mask) | (team_totals_mask), award] += 1
                elif award in {"ALCS MVP", "NLCS MVP"}:
                    df_1.loc[(player_mask) | (team_totals_mask), "LCS MVP"] += 1
                else:
                    for col in ("MVP", "CYA", "ROY"):
                        if col in award:
                            df_1.loc[player_mask, f"{col} Finish"] = int(award.strip(f"{col}-"))
                            df_1.loc[team_totals_mask, f"{col} Finish"] += 1
        return df_1

    @staticmethod
    def _scrape_value_table(table: bs) -> pd.DataFrame:
        """Gathers team value batting/pitching stats from `table`."""
        # scrape table
        records = []
        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            records.append(record)

        # set up DataFrame
        column_names = records.pop(0)
        df_2 = pd.DataFrame(records, columns=column_names)
        # remove column header rows
        df_2 = df_2.loc[df_2["Rk"] != "Rk"]

        # add player ids to table, exclude non-player rows
        player_id_column = scrape_player_ids(table)
        df_2.loc[df_2["Rk"] != "", "Player ID"] = player_id_column
        df_2.loc[df_2["Player ID"] == "nan", "Player ID"] = ""
        # sort table so that table can be joined to standard batting with expected alignment
        df_2.sort_values(by="Player ID", ascending=False, inplace=True)

        # remove columns also found in standard table
        df_2.drop(
            columns=[
                "Rk", "Player", "Player ID", "Age", "PA", "IP",
                "G", "GS", "R", "WAR", "Pos", "Awards"
            ], inplace=True, errors="ignore"
        )
        return df_2.reset_index(drop=True)
