#!/usr/bin/env python3

"""Defines functions for processing and validating inputs."""

import re

from ..options import write
from .abbreviations_manager import abv_man
from .constants import (BML_TEAM_ABVS, CURRENT_YEAR, CY_BASEBALL,
                        DATE_RANGE_REGEX, DATE_REGEX, DOUBLEHEADER_REGEX,
                        FIRST_ASG_YEAR, FIRST_GAMES_YEAR, FIRST_TEAMS_YEAR,
                        GAME_DATE_REGEX, MISSING_SEASONS_DICT, NO_ASG_YEARS,
                        PLAYER_ID_REGEX, SEASON_REGEX, TEAM_ALIASES)


def validate_game_list(game_list: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """
    Returns list including only the valid games, alerts user of removed inputs if
    `options.quiet` is False. Will change `home_team` args to uppercase.
    """
    result = []
    for home_team, date, doubleheader in game_list:
        # validate arguments
        home_team = home_team.upper()
        message = _validate_game_input(home_team, date, doubleheader)
        if message != "":
            write(f'cannot get "({home_team}, {date}, {doubleheader})": {message}')
            continue

        # check home team abbreviation
        if home_team == "ALLSTAR":
            result.append((home_team, date, doubleheader))
            continue
        year = int(date[:4])
        home_team = abv_man.to_regular(home_team, year)
        correct_abv = abv_man.correct_abvs(home_team, year, era_adjustment=False)
        if len(correct_abv) == 0: # correct_abv is a list of length 0 or 1
            write(f'cannot get "({home_team}, {date}, {doubleheader})": {home_team} did not play in {year}')
            continue
        correct_abv = abv_man.to_alias(*correct_abv, year)
        result.append((correct_abv, date, doubleheader))
    return result

def _validate_game_input(home_team: str, date: str, doubleheader: str) -> str:
    """Returns reason that input is invalid, or empty string. `home_team` must be uppercase."""
    if home_team == "ALLSTAR":
        if not re.match(SEASON_REGEX, date):
            return f'date "{date}" is invalid, must be YYYY for All-Star Games'
        year = int(date)
        if year < FIRST_ASG_YEAR:
            return f"there were no All-Star Games held until {FIRST_ASG_YEAR}"
        if year > CURRENT_YEAR + CY_BASEBALL - 1:
            return f"the {year} All-Star Game is in the future"
        if (year not in range(FIRST_ASG_YEAR, CURRENT_YEAR+CY_BASEBALL)
            or year in NO_ASG_YEARS):
            return f"there was no All-Star Game in {year}"
    else:
        if not (abv_man.is_valid(home_team) or home_team in TEAM_ALIASES.values()):
            return f'home_team "{home_team}" is invalid'
        if home_team in BML_TEAM_ABVS:
            return f"box scores for {home_team} are not available"
        if not re.match(GAME_DATE_REGEX, date):
            return f'date "{date}" is invalid, must be YYYYMMDD'
        if not re.match(DOUBLEHEADER_REGEX, doubleheader):
            return f'doubleheader "{doubleheader}" is invalid, must be 0-3'
        year = int(date[:4])
        if year < FIRST_GAMES_YEAR:
            return f'date "{date}" is too early, must be at least {FIRST_GAMES_YEAR}'
        if year > CURRENT_YEAR + CY_BASEBALL - 1:
            return f'date "{date}" is in the future'
    return ""

def validate_player_list(player_list: list[str]) -> list[str]:
    """
    Returns list including only the valid player ids, alerts user of removed inputs if
    `options.quiet` is False. Will change player ids to lowercase.
    """
    result = []
    for player_id in player_list:
        player_id = player_id.lower()
        message = _validate_player_input(player_id)
        if message != "":
            write(f'cannot get "{player_id}": {message}')
            continue
        result.append(player_id)
    return result

def _validate_player_input(player_id: str) -> str:
    """Returns reason that input is invalid, or empty string. `player_id` must be lowercase."""
    if not re.match(PLAYER_ID_REGEX, player_id):
        return "not a valid player id"
    return ""

def validate_team_list(team_list: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Returns list including only the valid teams, alerts user of removed inputs if
    `options.quiet` is False. Will change `team` args to uppercase.
    """
    result = []
    for abv, season in team_list:
        abv = abv.upper()
        message = _validate_team_input(abv, season)
        if message != "":
            write(f'cannot get "({abv}, {season})": {message}')
            continue

        # check home team abbreviation
        correct_abv = abv_man.correct_abvs(abv, int(season), era_adjustment=False)
        if len(correct_abv) == 0: # correct_abv is a list of length 0 or 1
            write(f'cannot get "({abv}, {season})": {abv} did not play in {season}')
            continue
        result.append((*correct_abv, season))
    return result

def _validate_team_input(team: str, season: str) -> str:
    """Returns reason that input is invalid, or empty string. `team` must be uppercase."""
    if not abv_man.is_valid(team):
        return f'team "{team}" is invalid'
    if not re.match(SEASON_REGEX, season):
        return f'season "{season}" is invalid'
    year = int(season)
    if year < FIRST_TEAMS_YEAR:
        return f'season "{season}" is too early, must be at least {FIRST_TEAMS_YEAR}'
    if year > CURRENT_YEAR + CY_BASEBALL - 1:
        return f'season "{season}" is in the future'
    if team in MISSING_SEASONS_DICT.get(year, {}):
        return f"{team} did not play in {season}"
    return ""

def validate_date_list(date_list: list[str]) -> list[str]:
    """
    Returns list including only the valid dates, alerts user of removed inputs if
    `options.quiet` is False. Dates must be uppercase.
    """
    result = []
    for date in date_list:
        if date == "ALL":
            return ["ALL"]
        if not (re.match(DATE_RANGE_REGEX, date) or re.match(DATE_REGEX, date)):
            write(f'ignoring invalid dates input "{date}"')
            continue
        if "-" in date:
            start, end = date.split("-")
            if int(start) > int(end):
                result.append(f"{end}-{start}")
                continue
        result.append(date)
    return result
