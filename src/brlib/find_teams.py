#!/usr/bin/env python3

"""Defines find_teams function."""

import re
from itertools import chain

import pandas as pd

from ._helpers.abbreviations_manager import abv_man
from ._helpers.constants import (CURRENT_YEAR, CY_BASEBALL, FIRST_TEAMS_YEAR,
                                 MISSING_SEASONS_DICT, SEASON_RANGE_REGEX,
                                 SEASON_REGEX)
from ._helpers.utils import runtime_typecheck
from .options import write


@runtime_typecheck
def find_teams(
    teams: str | list[str] = "ALL",
    seasons: str | list[str] = "ALL"
    ) -> list[tuple[str, str]]:
    # make sure all possible list inputs are lists
    teams = [teams] if not isinstance(teams, list) else teams
    seasons = [seasons] if not isinstance(seasons, list) else seasons

    # convert all strings to uppercase
    teams = [t.upper() for t in teams]
    seasons = [s.upper() for s in seasons]

    # validate team inputs
    teams = _process_abbreviation_list(teams, {"WML", "BML"})

    year_list = _make_year_list(seasons)
    if len(year_list) == 0:
        return []

    team_list = []
    for year in year_list:
        # correct team abbreviations for given year
        if teams == ["ALL"] or set(teams).issuperset({"WML", "BML"}):
            year_teams = ["ALL"]
        elif set(teams).issubset({"WML", "BML"}):
            year_teams = teams
        else:
            # find all matching abbreviations for year (e.g. (BAL, 1915) returns BAL and SLB)
            match_lists = [abv_man.correct_abvs(t, year, era_adjustment=True) for t in teams]
            # collapse the lists into one
            year_teams = list(chain(*match_lists))
            year_teams = [t for t in year_teams if t != ""]

            # add back non-abbreviation team inputs
            if "WML" in teams:
                year_teams.append("WML")
            if "BML" in teams:
                year_teams.append("BML")

        if len(year_teams) == 0:
            continue
        results = _find_season_teams(year, year_teams)
        team_list.extend(results)
    return team_list

def _process_abbreviation_list(abv_list: list[str], exceptions: set[str]) -> list[str]:
    """
    Returns a list including only the valid team abbreviations, except for those matching
    the contents of `exceptions`, alerts user of removed inputs if `options.quiet` is False.
    `abv_list` and `exceptions` contents must be uppercase.
    If "ALL" is in `abv_list`, return value will be ["ALL"].
    """
    result = []
    for abv in abv_list:
        if abv == "ALL":
            return ["ALL"]
        if not abv_man.is_valid(abv) and abv not in exceptions:
            write(f'skipping invalid team "{abv}"')
            continue
        result.append(abv)
    return result

def _make_year_list(seasons: list[str]) -> list[int]:
    """
    Returns the list of seasons listed in the contents of `seasons`. `seasons` must be uppercase.
    """
    year_range_end = CURRENT_YEAR + CY_BASEBALL
    all_team_years = range(FIRST_TEAMS_YEAR, year_range_end)

    year_set = set()
    for seasons_input in seasons:
        if seasons_input == "ALL":
            year_set = set(all_team_years)
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
            year_set.add(int(seasons_input))

    len_before = len(year_set)
    year_list = [y for y in year_set if y in all_team_years]
    if len_before != len(year_list):
        write(f"teams are only available from {FIRST_TEAMS_YEAR} through {year_range_end - 1}")
    year_list.sort()
    return year_list

def _find_season_teams(year: int, year_teams: list[str]) -> list[tuple[str, str]]:
    """
    Returns the list of valid teams in `year` with abbreviations listed in `year_teams`.
    `year_teams` must be uppercase. Handles missing seasons.
    """
    missing_seasons = MISSING_SEASONS_DICT.get(year, {})
    team_list = []
    for team in year_teams:
        year_mask = ((abv_man.df["First Year"] <= year) &
                     (abv_man.df["Last Year"] >= year))
        if team == "ALL":
            # identity mask
            team_mask = pd.Series(True, index=abv_man.df.index)
        elif team == "BML":
            team_mask = abv_man.df["BML"]
        elif team == "WML":
            team_mask = ~abv_man.df["BML"]
        else:
            team_mask = abv_man.df["Team"] == team

        match_rows = abv_man.df[(year_mask) & (team_mask)]
        teams = match_rows["Team"].values
        results = [(abv, str(year)) for abv in teams if abv not in missing_seasons]
        results.sort(key=lambda x: x[0]) # sort by team abv instead of franchise abv
        team_list.extend(results)
    return team_list
