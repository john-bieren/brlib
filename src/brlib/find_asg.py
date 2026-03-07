"""Defines `find_asg` function."""

import re

from ._helpers.constants import (
    CURRENT_YEAR,
    CY_ASG,
    FIRST_ASG_YEAR,
    NO_ASG_YEARS,
    SEASON_RANGE_REGEX,
    SEASON_REGEX,
    TWO_ASG_YEARS,
)
from ._helpers.typechecking import runtime_typecheck
from .options import write


@runtime_typecheck
def find_asg(seasons: str | list[str] = "ALL") -> list[str]:
    """
    Returns a list of All-Star Game IDs which can be an input to `get_games`.

    ## Parameters

    * `seasons`: `str` or `list[str]`, default `"ALL"`

        A year, inclusive range of years (e.g. `"2017-2019"`), `"ALL"`, or a list of multiple such
        inputs which specify the seasons from which to find All-Star Games.

    ## Returns

    `list[str]`

    ## Examples

    Seasons which did not have All-Star Games are taken into account:

    ```
    >>> br.find_asg("2019-2022")
    ['2019-allstar-game', '2021-allstar-game', '2022-allstar-game']
    ```

    Seasons with two All-Star Games are also accounted for:

    ```
    >>> br.find_asg("1962")
    ['1962-allstar-game-1', '1962-allstar-game-2']
    ```
    """
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
            if not re.fullmatch(SEASON_RANGE_REGEX, seasons_input):
                write(f'skipping invalid seasons input "{seasons_input}"')
                continue
            start, end = [int(s) for s in seasons_input.split("-", maxsplit=1)]
            if start > end:
                start, end = end, start
            year_set = year_set.union(range(start, end + 1))
        else:
            if not re.fullmatch(SEASON_REGEX, seasons_input):
                write(f'skipping invalid seasons input "{seasons_input}"')
                continue
            seasons_input = int(seasons_input)
            if seasons_input in NO_ASG_YEARS:
                write(f"no All-Star Game held in {seasons_input}")
                continue
            year_set.add(seasons_input)

    year_list = [y for y in year_set if y in all_asg_years]
    if len(year_list) == 0:
        write(
            f"All-Star Games have only been held from {FIRST_ASG_YEAR} through {year_range_end - 1}"
        )
    year_list = [y for y in year_list if y not in NO_ASG_YEARS]
    year_list.sort()

    result = []
    for year in year_list:
        if year in TWO_ASG_YEARS:
            result.extend([f"{year}-allstar-game-1", f"{year}-allstar-game-2"])
        else:
            result.append(f"{year}-allstar-game")
    return result
