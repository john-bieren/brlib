#!/usr/bin/env python3

"""Defines find_asg function."""

import re

from ._helpers.constants import (CURRENT_YEAR, CY_ASG, FIRST_ASG_YEAR,
                                 NO_ASG_YEARS, SEASON_RANGE_REGEX,
                                 SEASON_REGEX, TWO_ASG_YEARS)
from ._helpers.utils import runtime_typecheck
from .options import write


@runtime_typecheck
def find_asg(seasons: str | list[str] = "ALL") -> list[tuple[str, str, str]]:
    # process input
    seasons = [seasons] if not isinstance(seasons, list) else seasons
    seasons = [s.upper() for s in seasons]

    year_range_end = CURRENT_YEAR + CY_ASG
    all_asg_years = range(FIRST_ASG_YEAR, year_range_end)

    year_set = set()
    for seasons_input in seasons:
        if seasons_input == "ALL":
            year_set = set(all_asg_years)
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
            if seasons_input in NO_ASG_YEARS:
                write(f"no All-Star Game held in {seasons_input}")
                continue
            year_set.add(seasons_input)

    len_before = len(year_set)
    year_list = [y for y in year_set if y in all_asg_years]
    if len_before != len(year_list):
        write(f"All-Star Game box scores are only available from {FIRST_ASG_YEAR} through {year_range_end - 1}")
    # remove years which had no All-Star Game (silently, so that nothing prints if seasons="ALL")
    year_list = [y for y in year_list if y not in NO_ASG_YEARS]
    year_list.sort()

    result = []
    for year in year_list:
        if year in TWO_ASG_YEARS:
            result.extend((("allstar", str(year), "1"), ("allstar", str(year), "2")))
        else:
            result.append(("allstar", str(year), "0"))
    return result
