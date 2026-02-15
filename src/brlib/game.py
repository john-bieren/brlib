"""Defines `Game` class."""

import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from curl_cffi.requests import Response

from ._helpers.constants import (
    ALLSTAR_GAME_URL_REGEX,
    FORFEITED_GAME_WINNERS,
    GAME_BATTING_COLS,
    GAME_FIELDING_COLS,
    GAME_INFO_COLS,
    GAME_PITCHING_COLS,
    GAME_TEAM_INFO_COLS,
    GAME_URL_REGEX,
    PICKOFF_REGEX,
    RANGE_TEAM_REPLACEMENTS,
    SB_ATTEMPT_REGEX,
    TEAM_REPLACEMENTS,
    VENUE_REPLACEMENTS,
)
from ._helpers.inputs import validate_game_list
from ._helpers.no_hitter_dicts import nhd
from ._helpers.requests_manager import req_man
from ._helpers.utils import (
    change_innings_notation,
    clean_spaces,
    convert_numeric_cols,
    reformat_date,
    runtime_typecheck,
    scrape_player_ids,
    soup_from_comment,
    str_between,
    str_remove,
)
from .options import dev_alert, options, print_page


class Game:
    """
    Statistics and information from a game. Can be initialized by specifying `home_team`, `date`, and `doubleheader`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded box score page. If neither of these sets of parameters are given, an exception is raised.

    ## Parameters

    * `home_team`: `str`, default `""`

        The home team's abbreviation (e.g. `"sea"`), or, if the game is an All-Star Game, `"allstar"`. Era adjustment is not used, and aliases are accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

    * `date`: `str`, default `""`

        The date of the game in YYYYMMDD format (e.g. `"20230830"`). Or, if the game is an All-Star Game, the year in YYYY format.

    * `doubleheader`: `str`, default `""`

        The game's status as part of a doubleheader:
        * `"0"` if not part of a doubleheader.
        * `"1"` if first game of a doubleheader.
        * `"2"` if second game of a doubleheader.
        * `"3"` if third game of a tripleheader (i.e. [PIT192010023](https://www.baseball-reference.com/boxes/PIT/PIT192010023.shtml)).

        Or, if the game is an All-Star Game:
        * `"0"` if only ASG of the year.
        * `"1"` if first ASG of the year.
        * `"2"` if second ASG of the year.

    * `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

        A previously loaded box score page.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Game.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `update_venue_names`: `bool` or `None`, default `None`

        Whether to standardize venue name such that venues are identified by one name. If no value is passed, the value of `options.update_venue_names` is used.

    ## Attributes

    * `id`: `str`

        The unique identifier for the game used in the URL (e.g. "SEA201805020").

    * `name`: `str`

        The unique, pretty name of the game (e.g. "May 2, 2018, Oakland Athletics vs Seattle Mariners").

    * `info`: `pandas.DataFrame`

        Contains information about the game and its circumstances.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gameinfo-and-gamesetinfo)

    * `batting`: `pandas.DataFrame`

        Contains batting and baserunning stats from the batting tables and the information beneath them.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gamebatting-and-gamesetbatting)

    * `pitching`: `pandas.DataFrame`

        Contains pitching stats from the pitching tables and the information beneath them.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gamepitching-and-gamesetpitching)

    * `fielding`: `pandas.DataFrame`

        Contains fielding stats from the batting tables and the information beneath them.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gamefielding-and-gamesetfielding)

    * `team_info`: `pandas.DataFrame`

        Contains information about the teams involved in the game.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gameteam_info-and-gamesetteam_info)

    * `ump_info`: `pandas.DataFrame`

        Contains the names and positions of the game's umpires.
        [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#gameump_info-and-gamesetump_info)

    * `linescore`: `pandas.DataFrame`

        Contains the game's linescore, a box score fixture which displays the teams' run totals by inning, as well as their total runs, hits, and errors.

    * `players`: `list[str]`

        A list of the players who appeared in the game. Can be an input to `get_players`.

    * `teams`: `list[tuple[str, str]]`

        A list of the teams involved in the game. Can be an input to `get_teams`.

    ## Examples

    Load a game:

    ```
    >>> br.Game("SEA", "20190926", "0").name
    'September 26, 2019, Oakland Athletics vs Seattle Mariners'
    ```

    Load an All-Star Game:

    ```
    >>> br.Game("allstar", "2024", "0").name
    '2024 All-Star Game, July 16'
    ```

    ## Methods

    * [`Game.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Game.add_no_hitters)
    * [`Game.update_team_names`](https://github.com/john-bieren/brlib/wiki/Game.update_team_names)
    * [`Game.update_venue_names`](https://github.com/john-bieren/brlib/wiki/Game.update_venue_names)
    """

    @runtime_typecheck
    def __init__(
        self,
        home_team: str = "",
        date: str = "",
        doubleheader: str = "",
        page: Response = Response(),
        add_no_hitters: bool | None = None,
        update_team_names: bool | None = None,
        update_venue_names: bool | None = None,
    ) -> None:
        if add_no_hitters is None:
            add_no_hitters = options.add_no_hitters
        if update_team_names is None:
            update_team_names = options.update_team_names
        if update_venue_names is None:
            update_venue_names = options.update_venue_names

        if page.url == "":
            if any(s == "" for s in (home_team, date, doubleheader)):
                raise ValueError("insufficient arguments")

            games = validate_game_list([(home_team, date, doubleheader)])
            if len(games) == 0:
                raise ValueError("invalid arguments")
            page = Game._get_game(games[0])
        else:
            if not re.match(GAME_URL_REGEX, page.url) and not re.match(
                ALLSTAR_GAME_URL_REGEX, page.url
            ):
                raise ValueError("page does not contain a game")

        self.name = ""
        self.id = str_between(page.url, "/", ".", anchor="end")
        self.info, self.batting, self.pitching, self.fielding = [pd.DataFrame() for _ in range(4)]
        self.team_info, self.ump_info, self.linescore = [pd.DataFrame() for _ in range(3)]
        self.players, self.teams = [[] for _ in range(2)]
        self._home_score = self._away_score = 0
        self._home_team = self._away_team = self._winning_team = ""
        self._home_team_id = self._away_team_id = None
        self._is_asg = False
        self._url = page.url

        self._scrape_game(page)
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
            return "Game()"
        home_team = self._url[45:48] if not self._is_asg else "allstar"
        date = self._url[48:56] if not self._is_asg else self._url[43:47]
        if self._is_asg:
            doubleheader = self._url[61] if self._url[61].isnumeric() else "0"
        else:
            doubleheader = self._url[56]
        return f"Game('{home_team}', '{date}', '{doubleheader}')"

    def add_no_hitters(self) -> None:
        """
        Populates the no-hitter columns in the `Game.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> g = br.Game("TOR", "20180508", "0")
        >>> g.pitching[["Player", "Team", "NH", "PG", "CNH"]]
                   Player               Team  NH  PG  CNH
        0    James Paxton   Seattle Mariners NaN NaN  NaN
        1     Team Totals   Seattle Mariners NaN NaN  NaN
        2  Marcus Stroman  Toronto Blue Jays NaN NaN  NaN
        3       Tim Mayza  Toronto Blue Jays NaN NaN  NaN
        4   Jake Petricka  Toronto Blue Jays NaN NaN  NaN
        5      Aaron Loup  Toronto Blue Jays NaN NaN  NaN
        6     John Axford  Toronto Blue Jays NaN NaN  NaN
        7     Team Totals  Toronto Blue Jays NaN NaN  NaN
        >>> g.add_no_hitters()
        >>> g.pitching[["Player", "Team", "NH", "PG", "CNH"]]
                   Player               Team   NH   PG  CNH
        0    James Paxton   Seattle Mariners  1.0  0.0  0.0
        1     Team Totals   Seattle Mariners  1.0  0.0  0.0
        2  Marcus Stroman  Toronto Blue Jays  0.0  0.0  0.0
        3       Tim Mayza  Toronto Blue Jays  0.0  0.0  0.0
        4   Jake Petricka  Toronto Blue Jays  0.0  0.0  0.0
        5      Aaron Loup  Toronto Blue Jays  0.0  0.0  0.0
        6     John Axford  Toronto Blue Jays  0.0  0.0  0.0
        7     Team Totals  Toronto Blue Jays  0.0  0.0  0.0
        ```
        """
        success = nhd.populate()
        if not success:
            return
        self.pitching.loc[:, ["NH", "PG", "CNH"]] = 0

        inh_player_id = nhd.game_inh_dict.get(self.id, "")
        pg_player_id = nhd.game_pg_dict.get(self.id, "")
        cnh_list = nhd.game_cnh_dict.get(self.id, [])

        # add individual no-hitters
        for col, player_id in (("NH", inh_player_id), ("PG", pg_player_id)):
            if player_id == "":
                continue
            player_mask = self.pitching["Player ID"] == player_id
            nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
            self.pitching.loc[
                player_mask
                | (
                    (self.pitching["Player"] == "Team Totals")
                    & (self.pitching["Team ID"] == nh_team_id)
                ),
                col,
            ] = 1

        # add combined no-hitters
        for player_id in cnh_list:
            player_mask = self.pitching["Player ID"] == player_id
            nh_team_id = self.pitching.loc[player_mask, "Team ID"].values[0]
            self.pitching.loc[
                player_mask
                | (
                    (self.pitching["Player"] == "Team Totals")
                    & (self.pitching["Team ID"] == nh_team_id)
                ),
                "CNH",
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
        >>> g = br.Game("FLO", "19940729", "0")
        >>> g.info[["Away Team", "Home Team"]]
                Away Team        Home Team
        0  Montreal Expos  Florida Marlins
        >>> g.update_team_names()
        >>> g.info[["Away Team", "Home Team"]]
                Away Team      Home Team
        0  Montreal Expos  Miami Marlins
        ```
        """
        if self._is_asg:
            return

        # replace old team names
        self.linescore.replace({"Team": TEAM_REPLACEMENTS}, regex=True, inplace=True)
        self.team_info.replace({"Team": TEAM_REPLACEMENTS}, regex=True, inplace=True)
        self.info.replace({"Game": TEAM_REPLACEMENTS}, regex=True, inplace=True)
        self.info.replace(
            {
                "Home Team": TEAM_REPLACEMENTS,
                "Away Team": TEAM_REPLACEMENTS,
                "Winning Team": TEAM_REPLACEMENTS,
                "Losing Team": TEAM_REPLACEMENTS,
            },
            inplace=True,
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

        # replace old team names within a certain range
        year = int(self._home_team_id[-4:])
        for start_year, end_year, old_name, new_name in RANGE_TEAM_REPLACEMENTS:
            if year not in range(start_year, end_year + 1):
                continue
            name_dict = {old_name: new_name}

            self.linescore.replace({"Team": name_dict}, regex=True, inplace=True)
            self.team_info.replace({"Team": name_dict}, regex=True, inplace=True)
            self.info.replace({"Game": name_dict}, regex=True, inplace=True)
            self.info.replace(
                {
                    "Home Team": name_dict,
                    "Away Team": name_dict,
                    "Winning Team": name_dict,
                    "Losing Team": name_dict,
                },
                inplace=True,
            )
            self.batting.replace({"Team": name_dict, "Opponent": name_dict}, inplace=True)
            self.pitching.replace({"Team": name_dict, "Opponent": name_dict}, inplace=True)
            self.fielding.replace({"Team": name_dict, "Opponent": name_dict}, inplace=True)

        self.name = self.info["Game"].values[0]

    def update_venue_names(self) -> None:
        """
        Standardizes venue name such that venues are identified by one name.

        ## Parameters

        None

        ## Returns

        `None`

        ## Example

        ```
        >>> g = br.Game("FLO", "19940729", "0")
        >>> g.info["Venue"]
        0    Joe Robbie Stadium
        Name: Venue, dtype: object
        >>> g.update_venue_names()
        >>> g.info["Venue"]
        0    Hard Rock Stadium
        Name: Venue, dtype: object
        ```
        """
        self.info.replace({"Venue": VENUE_REPLACEMENTS}, inplace=True)

    @staticmethod
    def _get_game(game: tuple[str, str, str]) -> Response:
        """Returns the page associated with a game."""
        home_team, date, doubleheader = game
        if home_team == "ALLSTAR":
            game_number = f"-{doubleheader}" if doubleheader != "0" else ""
            endpoint = f"/allstar/{date}-allstar-game{game_number}.shtml"
        else:
            endpoint = f"/boxes/{home_team}/{home_team}{date}{doubleheader}.shtml"
        return req_man.get_page(endpoint)

    def _scrape_game(self, page: Response) -> None:
        """Scrapes game info and batting, pitching, and fielding stats from `page`."""
        soup = bs(page.content, "lxml")
        content = soup.find(id="content")
        section_wrappers = content.find_all("div", {"class": "section_wrapper"})

        other_info_index = -1
        for i, tag in enumerate(section_wrappers):
            if tag.text.strip() == "Other Info":
                other_info_index = i
        assert other_info_index != -1
        self._scrape_info(content, section_wrappers[other_info_index])

        batting_tables = content.find_all("div", {"class": "table_wrapper"})[:2]
        for table in batting_tables:
            h_df = self._scrape_batting(table)
            self.batting = pd.concat((self.batting, h_df))

        self._scrape_pitching(section_wrappers[other_info_index - 1])

        self.batting = convert_numeric_cols(self.batting)
        self.pitching = convert_numeric_cols(self.pitching)
        self.players = list(dict.fromkeys(self.players))

        self.info["Game"] = self.name
        self.info["Game ID"] = self.id
        self.info["Home Team ID"] = self._home_team_id
        self.info["Away Team ID"] = self._away_team_id
        self.batting["Game ID"] = self.id
        self.pitching["Game ID"] = self.id
        self.batting.reset_index(drop=True, inplace=True)
        self.pitching.reset_index(drop=True, inplace=True)

        self._get_fielding_dataframe()
        self._scrape_stolen_base_stats(batting_tables)
        self._get_ump_info()

        self.info = self.info.reindex(columns=GAME_INFO_COLS)
        self.batting = self.batting.reindex(columns=GAME_BATTING_COLS)
        self.pitching = self.pitching.reindex(columns=GAME_PITCHING_COLS)
        self.fielding = self.fielding.reindex(columns=GAME_FIELDING_COLS)
        self.team_info = self.team_info.reindex(columns=GAME_TEAM_INFO_COLS)

    def _scrape_info(self, content: Tag, other_info: Tag) -> None:
        """Populates `self.info` with data from `content` and `other_info`."""
        self.info = pd.DataFrame([self.name], columns=["Game"])
        self.team_info = pd.DataFrame(
            {"Home/Away": ["Away", "Home"], "Game ID": [self.id, self.id]}
        )
        heading = clean_spaces(content.find("h1").text)
        linescore = content.find("div", {"class": "linescore_wrap"})
        scorebox = content.find("div", {"class": "scorebox"})

        self._scrape_heading(heading)
        self._scrape_linescore(linescore)
        self._scrape_scorebox(scorebox)
        self._gather_team_info()
        self._scrape_other_info(other_info)
        self.info = convert_numeric_cols(self.info)

    def _scrape_heading(self, heading: str) -> None:
        """Scrapes game type and name from `heading`."""
        if "All-Star" in heading:
            self._is_asg = True
            self.info["Game Type"] = "All-Star Game"
            if self.id[-1].isdigit():
                self.name = heading.replace("Box Score", self.id[-1])
            else:
                self.name = heading.replace(" Box Score", "")

        # regular season game
        elif ")" not in heading and "World Series" not in heading:
            self.info["Game Type"] = "Regular Season"
            matchup, date = heading.replace(" Box Score:", ",").split(", ", maxsplit=1)

            doubleheader = int(self.id[-1])
            if doubleheader == 0:
                self.name = f"{date}, {matchup}"
            else:
                self.name = f"{date}, {matchup}, Game {doubleheader}"

        # postseason game
        else:
            year_series_game, matchup, month_day = heading.rsplit(", ", maxsplit=2)
            year, series_game = year_series_game.split(" ", maxsplit=1)

            # print the series abbreviation instead of the full name, except for the World Series
            if "(" in series_game:
                series_game = series_game.split("(", maxsplit=1)[1].replace(")", "")
            self.name = f"{month_day}, {year}, {matchup}, {series_game}"

            if "World Series" in heading:
                self.info["Game Type"] = "World Series"
            else:
                self.info["Game Type"] = str_between(heading, "League ", " (")

    def _scrape_linescore(self, linescore: Tag) -> None:
        """Scrapes team names and run totals, and populates `self.linescore` from `linescore`."""
        records = []
        for row in linescore.find_all("tr")[:3]:  # only grab column labels and two teams' lines
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            record = [i for i in record if "Sports Logos.net" not in i]
            # remove the X in the bottom of the ninth, if applicable
            record = [None if i == "X" else i for i in record]
            records.append(record)
        records[0].pop(0)  # extra empty string

        self.info["Innings"] = len(records[0]) - 4  # don't count Team, R, H, E cols
        self.info["Away Score"] = self._away_score = int(records[1][-3])
        self.info["Home Score"] = self._home_score = int(records[2][-3])
        self.info["Away Team"] = self._away_team = records[1][0]
        self.info["Home Team"] = self._home_team = records[2][0]

        changed_winner = FORFEITED_GAME_WINNERS.get(self.id)
        if self._home_score > self._away_score or changed_winner == self._home_team:
            self._winning_team, self.info["Losing Team"] = self._home_team, self._away_team
        elif self._away_score > self._home_score or changed_winner == self._away_team:
            self._winning_team, self.info["Losing Team"] = self._away_team, self._home_team
        else:
            self.info["Losing Team"] = self._winning_team = None
        self.info["Winning Team"] = self._winning_team

        records[0][0] = "Team"  # give the team column a name
        self.linescore = pd.DataFrame(records[1:3], columns=records[0])
        # convert string numbers to nullable ints (since B9 could be None)
        self.linescore[records[0][1:]] = self.linescore[records[0][1:]].astype("Int64")

        # record the teams by using the links to their pages
        if not self._is_asg:
            tags = linescore.find_all("a", href=True)
            teams = [tag["href"] for tag in tags if tag["href"].startswith("/teams/")]
            teams = [
                tuple(str_between(team, "/teams/", ".").split("/", maxsplit=1)) for team in teams
            ]
            assert len(teams) == 2
            self._away_team_id, self._home_team_id = ["".join(team) for team in teams]
            self.teams += teams

    def _scrape_scorebox(self, scorebox: Tag) -> None:
        """Scrapes several pieces of game info from `scorebox`."""
        elements = scorebox.find_all("div", recursive=False)
        teams = elements[0:2]
        game_info = elements[2]

        for team in teams:
            # determine whether current team is home team
            img_alt_text = team.find("img").get("alt")
            if self._is_asg:
                img_alt_text = img_alt_text.replace(".", "")
            is_home = self._home_team in img_alt_text

            # get team's post-game record
            if not self._is_asg:
                record = [
                    t.text for t in team.find_all("div") if "-" in t.text and "via" not in t.text
                ][0]
                score = int(team.find("div", {"class": "score"}).text)
                if is_home:
                    self.team_info.loc[1, "Record"] = record
                    assert self._home_score == score
                else:
                    self.team_info.loc[0, "Record"] = record
                    assert self._away_score == score

            # get team's previous and next game IDs
            prevnext = team.find("div", {"class": "prevnext"})
            games = prevnext.find_all("a")
            for game in games:
                game_id = str_between(game["href"], "/", ".", anchor="end")
                if game.text == "Prev Game":
                    self.team_info.loc[int(is_home), "Previous Game ID"] = game_id
                elif game.text == "Next Game":
                    self.team_info.loc[int(is_home), "Next Game ID"] = game_id

        for line in game_info.find_all("div"):
            line_str = line.text
            if "day, " in line_str:
                self.info["Day of Week"], date_to_format = line_str.split(", ", maxsplit=1)
                self.info["Date"] = reformat_date(date_to_format)
            elif "Start Time:" in line_str:
                self.info["Start Time"] = str_between(line_str, "Time: ", " Local")
            elif "Attendance:" in line_str:
                attendance = line_str.replace("Attendance: ", "")
                self.info["Attendance"] = int(attendance.replace(",", ""))
            elif "Venue:" in line_str:
                self.info["Venue"] = line_str.replace("Venue: ", "")
            elif "Duration:" in line_str:
                duration = line_str.replace("Game Duration: ", "")
                hours, minutes = duration.split(":", maxsplit=1)
                self.info["Duration"] = int(hours) * 60 + int(minutes)
            elif "Game, on" in line_str:
                self.info["Surface"] = line_str.split(", on ", maxsplit=1)[1].capitalize()

    def _gather_team_info(self) -> None:
        """Generates `self.team_info`."""
        self.team_info.loc[:, "Team"] = [self._away_team, self._home_team]
        self.team_info.loc[:, "Team ID"] = [self._away_team_id, self._home_team_id]
        self.team_info.loc[:, "Score"] = [self._away_score, self._home_score]

        if self._winning_team == self._home_team:
            self.team_info.loc[:, "Result"] = ["Loss", "Win"]
        elif self._winning_team == self._away_team:
            self.team_info.loc[:, "Result"] = ["Win", "Loss"]
        else:
            self.team_info.loc[:, "Result"] = "Tie"

    def _scrape_other_info(self, other_info: Tag) -> None:
        """Scrapes weather and umpire info from `other_info`."""
        other_info = soup_from_comment(other_info, only_if_table=False)
        other_info_list = other_info.find_all("div")

        umpires = weather_info = ""
        # [1:] because the first tag is the parent of the others
        for line in other_info_list[1:]:
            line_str = line.text.strip(" \n.")
            if "Umpires" in line_str:
                umpires = line_str.replace("Umpires: ", "")
            elif "Field Condition" in line_str:
                self.info["Field Condition"] = line_str.replace("Field Condition: ", "")
            elif "Start Time Weather" in line_str:
                weather_info = line_str[20:]

        self.info[["HP Ump", "1B Ump", "2B Ump", "3B Ump", "LF Ump", "RF Ump"]] = np.nan
        umpires_list = umpires.split(", ")
        for line in umpires_list:
            # "HP - Pat Hoberg"
            spot = line[0:2]
            ump = line[5:]
            if ump == "(none)":
                continue
            self.info[f"{spot} Ump"] = ump

        for info in weather_info.strip(".").split(", "):
            if "Unknown" in info:
                continue
            if "°" in info:
                self.info["Temperature"] = info.split("°", maxsplit=1)[0]
            elif "Dome" in info:
                self.info["Weather"] = info
                self.info["Wind Speed"] = "0"
            elif "Wind" in info:
                self.info["Wind Speed"] = wind_speed = str_between(info, "Wind ", "mph")
                if wind_speed != "0":
                    try:
                        self.info["Wind Direction"] = info.split("mph ", maxsplit=1)[1]
                    except IndexError:
                        pass
            elif info in {"Sunny", "Night", "Overcast", "Cloudy"}:
                self.info["Weather"] = info
            elif info in {"No Precipitation", "Rain", "Drizzle", "Showers", "Snow"}:
                self.info["Precipitation"] = info
            else:
                dev_alert(f'{self.id}: unexpected weather description "{info}"')

    def _scrape_batting(self, table: Tag) -> pd.DataFrame:
        """Scrapes batting stats from `table`."""
        # extract stats from table
        table_id = table.get("id")
        table = soup_from_comment(table, only_if_table=True)
        records = []
        for row in table.find_all("tr"):
            record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
            records.append(record)

        h_df = pd.DataFrame(records[1:], columns=records[0])
        h_df.rename(columns={"Batting": "Player"}, inplace=True)

        # remove blank rows
        h_df = h_df.loc[h_df["Player"] != ""]
        h_df.reset_index(drop=True, inplace=True)

        # separate batter name and position
        original_player_col = h_df["Player"].copy()
        is_player_mask = h_df["Player"] != "Team Totals"
        h_df[["Player", "Position"]] = h_df.loc[is_player_mask, "Player"].str.rsplit(
            expand=True, n=1
        )
        # find and fix split-up player names where no position was present, e.g. CHN190306020
        has_pos_mask = is_player_mask & (h_df["Position"].str.isupper())
        # this also renames final "Player" row to "Team Totals" instead of "Team"
        h_df.loc[~has_pos_mask, "Player"] = original_player_col.loc[~has_pos_mask]
        h_df.loc[~has_pos_mask, "Position"] = np.nan

        # get player IDs
        player_id_column = scrape_player_ids(table)
        h_df.loc[is_player_mask, "Player ID"] = player_id_column
        h_df.loc[~is_player_mask, "Player ID"] = None
        self.players += player_id_column

        # make sure all batters have only one row, combine their stats if not
        # used when a player is DH and pitches or when there is an illegal substitution
        if not h_df["Player ID"].is_unique:
            counts = h_df["Player ID"].value_counts()
            assert len(counts.loc[counts > 2]) == 0
            dup_players = counts.loc[counts == 2].index.tolist()

            # combine stats from the players' two rows and drop the second row
            for player in dup_players:
                player_mask = h_df["Player ID"] == player
                player_indices = h_df.loc[player_mask].index.to_list()
                keep_row = h_df.iloc[player_indices[0]]
                drop_row = h_df.iloc[player_indices[1]]
                h_df.drop(index=player_indices[1], inplace=True)
                # re-define this after dropping one of the rows
                player_mask = h_df["Player ID"] == player

                # stats are split across only certain columns, the rest are copied
                for col in ["AB", "R", "H", "RBI", "BB", "SO", "PO", "A"]:
                    keep = int(keep_row[col]) if keep_row[col] != "" else 0
                    drop = int(drop_row[col]) if drop_row[col] != "" else 0
                    h_df.loc[player_mask, col] = str(keep + drop)

                # positions can differ as well
                if keep_row["Position"] != drop_row["Position"]:
                    positions = "-".join([keep_row["Position"], drop_row["Position"]])
                    h_df.loc[player_mask, "Position"] = positions
            h_df.reset_index(drop=True, inplace=True)

        # determine home team
        if str_remove(self._home_team, " ", "-", ".") in table_id:
            h_df = self._set_home_team(h_df, True)
        elif str_remove(self._away_team, " ", "-", ".") in table_id:
            h_df = self._set_home_team(h_df, False)
        else:
            raise ValueError("home and away teams cannot be found from batting tables")

        # extract stats from details column
        h_df[["2B", "3B", "HR", "SB", "CS", "SF", "SH", "HBP", "GDP", "IBB"]] = 0
        for i, row in h_df.iterrows():
            for stat in row["Details"].split(","):
                if stat == "":
                    continue
                if "·" in stat:
                    num, stat = stat.split("·", maxsplit=1)
                    num = int(num)
                else:
                    num = 1
                # "IBB" is the abbreviation for intentional walks used across the rest of the site
                stat = "IBB" if stat == "IW" else stat
                h_df.loc[i, stat] = num
                h_df.loc[len(h_df) - 1, stat] += num  # team totals row

        # get additional stats from below the table
        player_stats = {
            "TB": "TB",
            "2-out RBI": "2-Out RBI",
            "E": "E",
            "Outfield Assists": "OFA",
            # TODO are these both still used (e.g. SEA202510100, 1961-allstar-game-1)
            "PB": "PB",
            "Passed Balls": "PB",
        }
        team_stats = {"Team LOB": "LOB", "With RISP": "RISP"}
        dp_tp = ["DP", "TP"]
        h_df[list(dict.fromkeys(player_stats.values()))] = 0
        h_df[dp_tp] = 0

        team_totals_mask = h_df["Player"] == "Team Totals"
        footer = table.find("div", {"class": "footer no_hide_long"})
        # [1:] because the first tag is the parent of the others
        for line in footer.find_all("div")[1:]:
            # skip the divs which contain the fielding and baserunning divs
            if "\n" in line.text:
                continue
            line_str = line.text.replace("\xa0", " ")
            # can't use line_str.strip(".") because "Jr." ends with a period
            line_str = line_str[:-1] if line_str[-1] == "." else line_str
            stat, players = line_str.split(": ", maxsplit=1)

            if player_stats.get(stat) is not None:
                stat_name = player_stats.get(stat)
                for player in players.split("; "):
                    player = player.split(" (", maxsplit=1)[0]
                    if player[-1].isnumeric():
                        player, number = player.rsplit(maxsplit=1)
                        number = int(number)
                    else:
                        number = 1
                    # += because players can be listed twice, e.g. BOS201708250
                    h_df.loc[h_df["Player"] == player, stat_name] += number
                    h_df.loc[team_totals_mask, stat_name] += number

            elif team_stats.get(stat) is not None:
                stat_name = team_stats.get(stat)
                h_df.loc[team_totals_mask, stat_name] = line_str.split(": ", maxsplit=1)[1]

            elif stat in dp_tp:
                total, player_list = players.split(". ", maxsplit=1)
                h_df.loc[team_totals_mask, stat] = int(total)

                for dp_players in player_list.split("; "):
                    if dp_players.rsplit(maxsplit=1)[1].isnumeric():
                        dp_players, number = dp_players.rsplit(maxsplit=1)
                        number = int(number)
                    else:
                        number = 1
                    for player in set(dp_players.split("-")):
                        h_df.loc[h_df["Player"] == player, stat] += number

        # convert cWPA from percentage to a float
        if "cWPA" in h_df.columns:
            h_df["cWPA"] = h_df["cWPA"].str.strip("%")
            h_df["cWPA"] = pd.to_numeric(h_df["cWPA"], errors="coerce") / 100
            h_df["cWPA"] = h_df["cWPA"].round(4)
        return h_df

    def _scrape_pitching(self, pitching_section: Tag) -> None:
        """Scrapes pitching stats from `table`."""
        pitching_section = soup_from_comment(pitching_section, only_if_table=True)

        for table in pitching_section.find_all("div", {"class": "table_wrapper"}):
            # extract stats from table
            records = []
            for row in table.find_all("tr"):
                record = [ele.text.strip() for ele in row.find_all(["th", "td"])]
                records.append(record)

            p_df = pd.DataFrame(records[1:], columns=records[0])
            p_df.rename(columns={"Pitching": "Player"}, inplace=True)

            # get player IDs
            player_id_column = scrape_player_ids(table)
            p_df.loc[p_df["Player"] != "Team Totals", "Player ID"] = player_id_column
            p_df.loc[p_df["Player"] == "Team Totals", "Player ID"] = None
            self.players += player_id_column

            # determine home team
            if str_remove(self._home_team, " ", "-", ".") in table.get("id"):
                p_df = self._set_home_team(p_df, True)
            elif str_remove(self._away_team, " ", "-", ".") in table.get("id"):
                p_df = self._set_home_team(p_df, False)
            else:
                raise ValueError("home and away teams cannot be found from pitching tables")

            # replace potential infinite season ERA, which would make column non-numeric
            p_df.loc[p_df["ERA"] == "inf", "ERA"] = None
            p_df["IP"].apply(change_innings_notation)

            p_df.loc[p_df["Player"] != "Team Totals", "Position"] = "RP"
            p_df.loc[0, "Position"] = "SP"  # the first pitcher to appear for the team

            p_df[["GS", "GF", "CG", "SHO"]] = 0
            p_df.loc[[0, len(p_df) - 1], "GS"] = 1  # first pitcher plus team totals
            p_df.loc[[len(p_df) - 2, len(p_df) - 1], "GF"] = 1
            if len(p_df) == 2:  # only SP and team totals
                p_df["CG"] = 1
                if p_df.loc[0, "R"] == "0":
                    p_df["SHO"] = 1

            # create details column with wins, losses, saves, blown saves, and holds
            p_df[["W", "L", "SV", "BS", "Holds"]] = 0
            try:
                p_df[["Player", "Details"]] = p_df["Player"].str.split(
                    ", ", expand=True, regex=False, n=1
                )
                for i, row in p_df.iterrows():
                    if row["Details"] is None:
                        continue
                    details = [d.split(" ", maxsplit=1)[0] for d in row["Details"].split(", ")]
                    for stat in details:
                        # "H" is also the name of the hits allowed column
                        stat = "Holds" if stat == "H" else stat
                        # "SV" is the abbreviation for saves used across the rest of the site
                        stat = "SV" if stat == "S" else stat
                        p_df.loc[i, stat] = 1
                        p_df.loc[len(p_df) - 1, stat] += 1  # team totals row
            except ValueError:
                # no details present, p_df["Player"].str.split only returned one column
                pass

            self.pitching = pd.concat((self.pitching, p_df))

        # add extra info found below the tables
        stats = {
            "Balks": "Balks",
            # TODO are these both still used (e.g. SEA202510100, 1961-allstar-game-1)
            "WP": "WP",
            "Wild Pitches": "WP",
            "HBP": "HBP",
            "IBB": "IBB",
        }
        self.pitching[list(dict.fromkeys(stats))] = 0
        events_section = pitching_section.find("div", {"class": "indiv_events"})
        both_team_totals_mask = self.pitching["Player"] == "Team Totals"
        # [1:] because the first tag is the parent of the others
        for line in events_section.find_all("div")[1:]:
            line_str = line.text.strip("\n .")
            stat, value = line_str.split(": ", maxsplit=1)
            stat_name = stats.get(stat)
            if stat_name is None or value == "None":
                continue

            for player in value.split("); "):
                player = player.split(" (", maxsplit=1)[0].replace("\xa0", " ")
                if player[-1].isnumeric():
                    player, number = player.rsplit(maxsplit=1)
                    number = int(number)
                else:
                    number = 1

                player_mask = self.pitching["Player"] == player
                team_name = self.pitching.loc[player_mask, "Team"].values[0]
                team_totals_mask = both_team_totals_mask & (self.pitching["Team"] == team_name)
                self.pitching.loc[player_mask, stat_name] = number
                self.pitching.loc[team_totals_mask, stat_name] += number

        # convert cWPA from percentage to a float
        if "cWPA" in self.pitching.columns:
            self.pitching["cWPA"] = self.pitching["cWPA"].str.strip("%")
            self.pitching["cWPA"] = pd.to_numeric(self.pitching["cWPA"], errors="coerce") / 100
            self.pitching["cWPA"] = self.pitching["cWPA"].round(4)

    def _set_home_team(self, df: pd.DataFrame, team_is_home: bool) -> pd.DataFrame:
        """Sets variables and `df` columns related to which team is at home."""
        if team_is_home:
            df["Home/Away"] = "Home"
            df["Team Score"] = self._home_score
            team = self._home_team
            opponent = self._away_team
            team_id = self._home_team_id
            opponent_id = self._away_team_id
        else:
            df["Home/Away"] = "Away"
            df["Team Score"] = self._away_score
            team = self._away_team
            opponent = self._home_team
            team_id = self._away_team_id
            opponent_id = self._home_team_id

        df["Team"] = team
        df["Opponent"] = opponent
        df["Team ID"] = team_id
        df["Opponent Team ID"] = opponent_id

        if self._winning_team == team:
            df["Result for Team"] = "Win"
        elif self._winning_team == opponent:
            df["Result for Team"] = "Loss"
        elif self._winning_team is None:
            df["Result for Team"] = "Tie"
        return df

    def _get_fielding_dataframe(self) -> None:
        """Copies info and moves fielding stats from `self.batting` to `self.fielding`."""
        self.fielding = self.batting[
            [
                "Player",
                "Player ID",
                "Position",
                "PO",
                "A",
                "E",
                "DP",
                "TP",
                "OFA",
                "PB",
                "SB",
                "CS",
                "Team",
                "Team ID",
                "Opponent",
                "Opponent Team ID",
                "Team Score",
                "Result for Team",
                "Home/Away",
                "Game ID",
            ]
        ].copy()

        # filter out batters who did not appear in the field
        positions = self.fielding["Position"].copy()
        is_string_mask = positions.apply(lambda x: isinstance(x, str))
        # replace NaN values with empty strings
        positions = positions.where(is_string_mask, "")
        positions = positions.str.split("-").apply(lambda pos: set(pos) - {"DH", "PH", "PR"})
        played_defense_mask = positions.apply(lambda x: len(x) > 0)
        self.fielding = self.fielding[played_defense_mask]
        self.fielding.reset_index(drop=True, inplace=True)

        # some old games have an asterisk in PO team total rows (e.g. SLN190106150)
        self.fielding.loc[self.fielding["PO"] == "*", "PO"] = None

        # remove pitchers who did not hit
        self.batting = self.batting.loc[~self.batting["AB"].isna()]
        self.batting.reset_index(drop=True, inplace=True)

    def _scrape_stolen_base_stats(self, batting_tables: list[Tag]) -> None:
        """Tallies SB attempts and results by catcher, stealer, and base from `batting_tables`."""
        self.batting[
            [
                "2B SB",
                "3B SB",
                "HP SB",
                "2B CS",
                "3B CS",
                "HP CS",
                "Pick",
                "1B Pick",
                "2B Pick",
                "3B Pick",
            ]
        ] = 0
        self.fielding[
            [
                "SB",
                "2B SB",
                "3B SB",
                "HP SB",
                "CS",
                "2B CS",
                "3B CS",
                "HP CS",
                "Pick",
                "1B Pick",
                "2B Pick",
                "3B Pick",
            ]
        ] = 0
        base_conversions = {"1st base": "1B", "2nd base": "2B", "3rd base": "3B", "Home": "HP"}
        sb_ids = {"SBhome", "SBvisitor", "CShome", "CSvisitor", "Pickoffshome", "Pickoffsvisitor"}

        for table in batting_tables:
            table = soup_from_comment(table, only_if_table=True)
            footer = table.find("div", {"class": "footer no_hide_long"})

            for line in footer.find_all("div", {"id": sb_ids}):
                line_str = line.text.strip(".")
                stat, players = line_str.split(": ", maxsplit=1)
                stat = "Pick" if stat == "Pickoffs" else stat

                for player in players.split("; "):
                    stealer, info = player.strip(")").split(" (", maxsplit=1)
                    if info == "":
                        # no info for many old games
                        continue
                    # remove the player's game total, if applicable
                    stealer = (
                        stealer.rsplit(" ", maxsplit=1)[0] if stealer[-1].isdigit() else stealer
                    )
                    for attempt in info.split(", "):
                        # skip the running season total (sometimes empty in older box scores)
                        if attempt.isdigit() or attempt == "":
                            continue
                        att_match = re.search(SB_ATTEMPT_REGEX, attempt) or re.search(
                            PICKOFF_REGEX, attempt
                        )
                        assert att_match is not None
                        base = base_conversions[att_match.group("base")]
                        # "pitcher" may be the catcher on some POCS, but it still works correctly
                        # strip() because there's a trailing space if times != 1
                        pitcher = att_match.group("pitcher").replace("POCS", "").strip()
                        times = att_match.group("times")
                        times = int(times) if times != "" else 1

                        # increment defensive stats
                        if len(att_match.groups()) == 4:  # match is _SB_ATTEMPT_REGEX
                            # strip() because there's a trailing space if times != 1
                            catcher = att_match.group("catcher").strip()
                            defenders_mask = self.fielding["Player"].isin({pitcher, catcher})
                        else:
                            defenders_mask = self.fielding["Player"] == pitcher

                        defense_team = self.fielding.loc[defenders_mask, "Team"].values[0]
                        defense_mask = defenders_mask | (
                            (self.fielding["Player"] == "Team Totals")
                            & (self.fielding["Team"] == defense_team)
                        )
                        self.fielding.loc[defense_mask, [stat, f"{base} {stat}"]] += times

                        # incremenet offensive stats
                        stealer_mask = self.batting["Player"] == stealer
                        offense_mask = stealer_mask | (
                            (self.batting["Player"] == "Team Totals")
                            & (self.batting["Team"] != defense_team)
                        )
                        # no need to increment SB or CS because they're already tallied
                        if stat == "Pick":
                            self.batting.loc[offense_mask, "Pick"] += times
                        self.batting.loc[offense_mask, f"{base} {stat}"] += times

    def _get_ump_info(self) -> None:
        """Populates `self.ump_info`."""
        self.ump_info = pd.melt(
            self.info,
            id_vars=["Game ID"],
            value_vars=["HP Ump", "1B Ump", "2B Ump", "3B Ump", "LF Ump", "RF Ump"],
        )
        self.ump_info.rename(columns={"variable": "Position", "value": "Umpire"}, inplace=True)
        self.ump_info = self.ump_info.loc[~self.ump_info["Umpire"].isnull()]
        self.ump_info["Position"] = self.ump_info["Position"].str.replace(" Ump", "")
