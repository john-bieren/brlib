#!/usr/bin/env python3

"""Defines get_teams function."""

from tqdm import tqdm

from ._helpers.inputs import validate_team_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck
from .options import options
from .team import Team


@runtime_typecheck
def get_teams(
        team_list: list[tuple[str, str]],
        add_no_hitters: bool | None = None
        ) -> list[Team]:
    """
    Returns a list of `Team` objects corresponding to the input list of tuples which mimic the `Team` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `team_list`: `list[tuple[str, str]]`

        A list of tuples containing `team`, and `season` arguments like those for a [`Team`](https://github.com/john-bieren/brlib/wiki/Team) object.

    ## Returns

    `list[Team]`

    ## Examples

    Gather some teams of interest:

    ```
    >>> br.get_teams([("HOU", "2019"), ("SEA", "2021"), ("WSN", "2022")])
    [Team('HOU', '2019'), Team('SEA', '2021'), Team('WSN', '2022')]
    ```

    Directly pass `find_teams` results or `teams` attributes:

    ```
    >>> ft = br.find_teams(["SEA", "TBR"], ["2008", "2010"])
    >>> br.get_teams(ft)
    [Team('SEA', '2008'), Team('TBR', '2008'), Team('SEA', '2010'), Team('TBR', '2010')]
    ```
    """
    if add_no_hitters is None:
        add_no_hitters = options.add_no_hitters

    team_list = validate_team_list(team_list)
    if len(team_list) == 0:
        return []

    results = []
    for abv, season in tqdm(
            iterable=list(dict.fromkeys(team_list)),
            unit="team",
            bar_format=options.pb_format,
            colour=options.pb_color,
            disable=options.pb_disable
            ):
        endpoint = f"/teams/{abv}/{season}.shtml"

        page = req_man.get_page(endpoint)
        result = Team(page=page, add_no_hitters=add_no_hitters)
        results.append(result)
        req_man.pause()
    return results
