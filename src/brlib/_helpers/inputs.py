"""Defines functions for processing and validating inputs."""

import re

from ..options import write
from .abbreviations_manager import abv_mgr
from .constants import (
    ASG_ID_REGEX,
    BML_TEAM_ABVS,
    CURRENT_YEAR,
    CY_BASEBALL,
    DATE_RANGE_REGEX,
    DATE_REGEX,
    FIRST_ASG_YEAR,
    FIRST_GAMES_YEAR,
    FIRST_TEAMS_YEAR,
    GAME_ID_REGEX,
    MISSING_SEASONS_DICT,
    NO_ASG_YEARS,
    PLAYER_ID_REGEX,
    TEAM_ALIASES,
    TEAM_ID_REGEX,
)


def validate_game_list(game_list: list[str]) -> list[str]:
    """
    Returns list including only the valid game IDs, alerts user of removed inputs if
    `options.quiet` is `False`. Will change IDs to correct case for URLs.
    """
    result = []
    for game_id in game_list:
        # parse game ID
        if re.fullmatch(GAME_ID_REGEX, game_id):
            home_team = game_id[:-9].upper()
            date = game_id[-9:-1]
            doubleheader = game_id[-1]
        elif re.fullmatch(ASG_ID_REGEX, game_id):
            home_team = "allstar"
            date = game_id[:4]
            last_fragment = game_id.rsplit("-", maxsplit=1)[1]
            if last_fragment in {"1", "2"}:
                doubleheader = last_fragment
            else:
                doubleheader = "0"
        else:
            write(f'cannot get "{game_id}": not a valid game ID')
            continue

        # validate game ID
        message = _validate_game_input(home_team, date, doubleheader)
        if message != "":
            write(f'cannot get "{game_id}": {message}')
            continue

        # check home team abbreviation
        if home_team == "allstar":
            game_number = f"-{doubleheader}" if doubleheader != "0" else ""
            result.append(f"{date}-allstar-game{game_number}")
            continue
        year = int(date[:4])
        home_team = abv_mgr.to_regular(home_team, year)
        correct_abv = abv_mgr.correct_abvs(home_team, year, era_adjustment=False)
        if len(correct_abv) == 0:  # correct_abv is a list of length 0 or 1
            write(f'cannot get "{game_id}": {home_team} did not play in {year}')
            continue
        # use correct_abv to account for discontinuities, guarantee all-caps abbreviation
        correct_abv = abv_mgr.to_alias(correct_abv[0], year)
        result.append(f"{correct_abv}{date}{doubleheader}")
    return result


def _validate_game_input(home_team: str, date: str, doubleheader: str) -> str:
    """Returns reason that input is invalid, or empty string. `home_team` must be uppercase."""
    if home_team == "allstar":
        year = int(date)
        if year < FIRST_ASG_YEAR:
            return f"there were no All-Star Games held until {FIRST_ASG_YEAR}"
        if year > CURRENT_YEAR + CY_BASEBALL - 1:
            return f"the {year} All-Star Game is in the future"
        if year not in range(FIRST_ASG_YEAR, CURRENT_YEAR + CY_BASEBALL) or year in NO_ASG_YEARS:
            return f"there was no All-Star Game in {year}"
    else:
        if not (abv_mgr.is_valid(home_team) or home_team in TEAM_ALIASES.values()):
            return f'abbreviation "{home_team}" is not associated with any teams'
        if home_team in BML_TEAM_ABVS:
            return f"box scores are not available for {home_team}"
        if not 0 <= int(doubleheader) <= 3:
            return f'doubleheader "{doubleheader}" is invalid, must be 0-3'
        year = int(date[:4])
        if year < FIRST_GAMES_YEAR:
            return f"{year} is too early, must be at least {FIRST_GAMES_YEAR}"
        if year > CURRENT_YEAR + CY_BASEBALL - 1:
            return f"{year} is in the future"
    return ""


def validate_player_list(player_list: list[str]) -> list[str]:
    """
    Returns list including only the valid player IDs, alerts user of removed inputs if
    `options.quiet` is `False`. Will change player IDs to lowercase.
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
    if not re.fullmatch(PLAYER_ID_REGEX, player_id):
        return "not a valid player ID"
    return ""


def validate_team_list(team_list: list[str]) -> list[str]:
    """
    Returns list including only the valid team IDs, alerts user of removed inputs if
    `options.quiet` is `False`. Will change IDs to uppercase.
    """
    result = []
    for team_id in team_list:
        # parse team ID
        if not re.fullmatch(TEAM_ID_REGEX, team_id):
            write(f'cannot get "{team_id}": not a valid team ID')
            continue
        abv = team_id[:-4]
        season = team_id[-4:]
        abv = abv.upper()
        message = _validate_team_input(abv, season)
        if message != "":
            write(f'cannot get "{team_id}": {message}')
            continue

        # check home team abbreviation
        correct_abv = abv_mgr.correct_abvs(abv, int(season), era_adjustment=False)
        if len(correct_abv) == 0:  # correct_abv is a list of length 0 or 1
            write(f'cannot get "{team_id}": {abv} did not play in {season}')
            continue
        result.append(f"{correct_abv[0]}{season}")
    return result


def _validate_team_input(team: str, season: str) -> str:
    """Returns reason that input is invalid, or empty string. `team` must be uppercase."""
    if not abv_mgr.is_valid(team):
        return f'abbreviation "{team}" is not associated with any teams'
    year = int(season)
    if year < FIRST_TEAMS_YEAR:
        return f"{season} is too early, must be at least {FIRST_TEAMS_YEAR}"
    if year > CURRENT_YEAR + CY_BASEBALL - 1:
        return f"{season} is in the future"
    if team in MISSING_SEASONS_DICT.get(year, {}):
        return f"{team} did not play in {season}"
    return ""


def validate_date_list(date_list: list[str]) -> list[str]:
    """
    Returns list including only the valid dates, alerts user of removed inputs if
    `options.quiet` is `False`. Dates must be uppercase.
    """
    result = []
    for date in date_list:
        if date == "ALL":
            return ["ALL"]
        if not (re.fullmatch(DATE_RANGE_REGEX, date) or re.fullmatch(DATE_REGEX, date)):
            write(f'ignoring invalid dates input "{date}"')
            continue
        if "-" in date:
            start, end = date.split("-", maxsplit=1)
            if int(start) > int(end):
                result.append(f"{end}-{start}")
                continue
        result.append(date)
    return result
