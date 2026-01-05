#!/usr/bin/env python3

"""Defines find_games function."""

import re
from itertools import chain

from bs4 import BeautifulSoup as bs
from curl_cffi.requests import Response
from tqdm import tqdm

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import (BML_TEAM_ABVS, CURRENT_YEAR, CY_BASEBALL,
                                 FIRST_GAMES_YEAR, NO_POSTSEASON_YEARS,
                                 SCHEDULE_TAG_REGEX, SEASON_RANGE_REGEX,
                                 SEASON_REGEX, TEAM_ALIASES)
from ._helpers.inputs import validate_date_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import report_on_exc, runtime_typecheck
from .options import options, print_page, write


@runtime_typecheck
def find_games(
        teams: str | list[str] = "ALL",
        seasons: str | list[str] = "ALL",
        opponents: str | list[str] = "ALL",
        dates: str | list[str] = "ALL",
        home_away: str = "ALL",
        game_type: str = "ALL"
        ) -> list[tuple[str, str, str]]:
    # make sure all possible list inputs are lists
    teams = [teams] if not isinstance(teams, list) else teams
    seasons = [seasons] if not isinstance(seasons, list) else seasons
    opponents = [opponents] if not isinstance(opponents, list) else opponents
    dates = [dates] if not isinstance(dates, list) else dates

    # convert all strings to uppercase
    teams = [t.upper() for t in teams]
    seasons = [s.upper() for s in seasons]
    opponents = [o.upper() for o in opponents]
    dates = [d.upper() for d in dates]
    home_away = home_away.upper()
    game_type = game_type.upper()

    # validate inputs
    teams = _process_abbreviation_list(teams)
    opponents = _process_abbreviation_list(opponents)
    dates = validate_date_list(dates)
    if not _check_other_inputs(home_away, game_type):
        return []

    year_list = _find_year_list(teams, seasons, opponents, game_type)
    if len(year_list) == 0:
        return []

    game_list = []
    for year in tqdm(
            iterable=year_list, unit="season",
            bar_format=options.pb_format, colour=options.pb_color,
            disable=options.pb_disable
            ):
        # correct abbreviations for given year
        if teams == ["ALL"]:
            year_teams = ["ALL"]
        else:
            # find all matching abbreviations for year (e.g. (BAL, 1915) returns BAL and SLB)
            match_lists = [abv_man.correct_abvs(t, year, era_adjustment=True) for t in teams]
            # collapse the lists into one
            year_teams = list(chain(*match_lists))
            year_teams = [t for t in year_teams if t != ""]
        if opponents == ["ALL"]:
            year_opponents = ["ALL"]
        else:
            match_lists = [abv_man.correct_abvs(o, year, era_adjustment=True) for o in opponents]
            year_opponents = list(chain(*match_lists))
            year_opponents = [o for o in year_opponents if o != ""]

        page = req_man.get_page(f"/leagues/majors/{year}-schedule.shtml")
        results = _find_season_games(page, year_teams, year_opponents, dates, home_away, game_type)
        print_page(f"{year} MLB Schedule")
        game_list.extend(results)
        req_man.pause()
    return game_list

def _process_abbreviation_list(abv_list: list[str]) -> list[str]:
    """
    Returns a list including only the valid team abbreviations for teams with box scores
    (not including aliases), alerts user of removed inputs if `options.quiet` is False.
    `abv_list` contents must be uppercase. If "ALL" is in `abv_list`, return value will be ["ALL"].
    """
    result = []
    for abv in abv_list:
        if abv == "ALL":
            return ["ALL"]
        if not abv_man.is_valid(abv) or abv in TEAM_ALIASES.values():
            write(f'skipping invalid team "{abv}"')
            continue
        if abv in BML_TEAM_ABVS:
            write(f"skipping {abv}: no box scores available")
            continue
        result.append(abv)
    return result

def _check_other_inputs(home_away: str, game_type: str) -> bool:
    """
    Indicates whether the `home_away` and `game_type` inputs have valid values.
    Inputs must be uppercase.
    """
    if home_away not in {"ALL", "HOME", "AWAY"}:
        write(f'invalid home_away input "{home_away}"')
        return False
    if game_type not in {"ALL", "REG", "POST"}:
        write(f'invalid game_type input "{game_type}"')
        return False
    return True

def _find_year_list(
        teams: list[str],
        seasons: list[str],
        opponents: list[str],
        game_type: str
        ) -> list[int]:
    """
    Returns the list of years within `seasons` in which `game_type` games between
    `teams` and `opponents` are possible. Inputs must be uppercase.
    """
    year_range_end = CURRENT_YEAR + CY_BASEBALL
    all_game_years = range(FIRST_GAMES_YEAR, year_range_end)

    year_set = set()
    for seasons_input in seasons:
        if seasons_input == "ALL":
            year_set = set(all_game_years)
            break
        if "-" in seasons_input:
            if not re.match(SEASON_RANGE_REGEX, seasons_input):
                write(f'skipping invalid seasons input "{seasons_input}"')
                continue
            start, end = [int(s) for s in seasons_input.split("-", maxsplit=1)]
            if start > end:
                start, end = end, start
            year_set = year_set.union(range(start, end + 1))
        else:
            if not re.match(SEASON_REGEX, seasons_input):
                write(f'skipping invalid seasons input "{seasons_input}"')
                continue
            seasons_input = int(seasons_input)
            if game_type == "POST" and seasons_input in NO_POSTSEASON_YEARS:
                write(f"no postseason held in {seasons_input}")
                continue
            year_set.add(seasons_input)

    len_before = len(year_set)
    year_set = {y for y in year_set if y in all_game_years}
    if len_before != len(year_set):
        write(f"box scores are only available from {FIRST_GAMES_YEAR} through {year_range_end - 1}")

    if game_type == "POST":
        # remove years which had no postseason (silently, so that nothing prints if seasons="ALL")
        year_set = {y for y in year_set if y not in NO_POSTSEASON_YEARS}

    # filter years to those which could possibly contain a matchup of the teams and opponents
    if teams != ["ALL"] and opponents != ["ALL"]:
        valid_years = set(range(FIRST_GAMES_YEAR, year_range_end))
        if teams != ["ALL"]:
            valid_years.intersection_update(_all_franchise_seasons(teams))
        if opponents != ["ALL"]:
            valid_years.intersection_update(_all_franchise_seasons(opponents))
        year_set.intersection_update(valid_years)

    year_list = list(year_set)
    year_list.sort()
    return year_list

def _all_franchise_seasons(abbreviations: list[str]) -> set[int]:
    """
    Returns the set of years in which any team associated with listed abbreviations played.
    Does not handle missing seasons because none exist for teams that currently have box scores.
    `abbreviations` must be uppercase.
    """
    team_matches = abv_man.df.loc[abv_man.df["Team"].isin(abbreviations)]
    franchise_abvs = team_matches["Franchise"].values
    franchise_abv_matches = abv_man.df.loc[abv_man.df["Franchise"].isin(franchise_abvs)]

    result = set()
    for _, row in franchise_abv_matches.iterrows():
        years = set(range(row["First Year"], row["Last Year"] + 1))
        result = result.union(years)
    return result

@report_on_exc(0)
def _find_season_games(
        page: Response,
        teams: list[str],
        opponents: list[str],
        dates: list[str],
        home_away: str,
        game_type: str
        ) -> list[tuple[str, str, str]]:
    """
    Scrapes an MLB schedule page, and returns the games from that season which
    match all of the other input parameters. Inputs must be uppercase.
    """
    team_set = set(teams)
    opponent_set = set(opponents)

    # convert date inputs into a set of valid dates
    date_set = set()
    if dates == ["ALL"]:
        date_set = set(range(301, 1130))
    else:
        for date in dates:
            if "-" in date:
                int_dates = [int(d) for d in date.split("-", maxsplit=1)]
                date_set = date_set.union(range(int_dates[0], int_dates[1] + 1))
            else:
                date_set.add(int(date))

    soup = bs(page.content, "lxml")
    content = soup.find(id="content")
    schedules = content.find_all("div", {"class": "section_wrapper", "id": SCHEDULE_TAG_REGEX})
    # there's a regular season schedule and probably a postseason one as well
    assert len(schedules) in {1, 2}

    # filter regular season/postseason games
    postseason_exists = len(schedules) == 2
    if postseason_exists:
        if game_type == "REG":
            del schedules[1]
        elif game_type == "POST":
            del schedules[0]
    else:
        if game_type == "POST":
            return []

    game_list = []
    for schedule in schedules:
        games = schedule.find_all("p")
        for game in games:
            links = game.find_all("a", href=True)
            # there should be links to the pages of the away team, home team, and box score
            if len(links) != 3:
                # skip games which lack box scores
                continue
            away_link, home_link, endpoint = [a["href"] for a in links]
            if "previews" in endpoint:
                continue

            date = endpoint[-15:-7]
            doubleheader = endpoint[-7]
            away_team = away_link.split("/")[2]
            home_team = home_link.split("/")[2]

            append = False
            if home_away == "ALL":
                append = (
                    not team_set.isdisjoint({away_team, home_team, "ALL"}) and
                    not opponent_set.isdisjoint({away_team, home_team, "ALL"}) and
                    int(date[4:]) in date_set
                )
            elif home_away == "HOME":
                append = (
                    not team_set.isdisjoint({home_team, "ALL"}) and
                    not opponent_set.isdisjoint({away_team, "ALL"}) and
                    int(date[4:]) in date_set
                )
            elif home_away == "AWAY":
                append = (
                    not team_set.isdisjoint({away_team, "ALL"}) and
                    not opponent_set.isdisjoint({home_team, "ALL"}) and
                    int(date[4:]) in date_set
                )

            if append:
                game_list.append((home_team, date, doubleheader))
    return game_list
