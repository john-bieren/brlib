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
