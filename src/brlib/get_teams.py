#!/usr/bin/env python3

"""Defines get_teams function."""

from tqdm import tqdm

from ._helpers.inputs import validate_team_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck
from .options import options, write
from .team import Team


@runtime_typecheck
def get_teams(
    team_list: list[tuple[str, str]],
    add_no_hitters: bool | None = None,
    update_team_names: bool | None = None,
    update_venue_names: bool | None = None,
    ignore_errors: bool = True,
) -> list[Team]:
    """
    Returns a list of `Team` objects corresponding to the tuples in `team_list`, which mimic the `Team` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `team_list`: `list[tuple[str, str]]`

        A list of tuples containing `team`, and `season` arguments like those for a [`Team`](https://github.com/john-bieren/brlib/wiki/Team) object.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Team.pitching` DataFrames, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `update_venue_names`: `bool` or `None`, default `None`

        Whether to standardize venue names such that venues are identified by one name. If no value is passed, the value of `options.update_venue_names` is used.

    * `ignore_errors`: `bool`, default `True`

        Whether to suppress any raised exceptions. If `True`, teams which raise an exception will be omitted from the returned list. If the exception is caused by the [rate limit](https://www.sports-reference.com/429.html) being exceeded, the list is returned as-is.

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
    if update_team_names is None:
        update_team_names = options.update_team_names
    if update_venue_names is None:
        update_venue_names = options.update_venue_names

    team_list = validate_team_list(team_list)
    if len(team_list) == 0:
        return []

    results = []
    for abv, season in tqdm(
        iterable=list(dict.fromkeys(team_list)),
        unit="team",
        bar_format=options.pb_format,
        colour=options.pb_color,
        disable=options.pb_disable,
    ):
        endpoint = f"/teams/{abv}/{season}.shtml"

        try:
            page = req_man.get_page(endpoint)
            result = Team(
                page=page,
                add_no_hitters=add_no_hitters,
                update_team_names=update_team_names,
                update_venue_names=update_venue_names,
            )
            results.append(result)
        except ConnectionRefusedError as exc:
            if not ignore_errors:
                raise
            write(f"{type(exc).__name__}: {exc}")
            return results
        except Exception as exc:
            if not ignore_errors:
                raise
            write(f"{type(exc).__name__}: {exc}")
            write(f"cannot get {abv}{season}")
            continue
        finally:
            req_man.pause()
    return results
