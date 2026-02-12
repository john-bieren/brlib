#!/usr/bin/env python3

"""Defines `get_players` function."""

from tqdm import tqdm

from ._helpers.inputs import validate_player_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck
from .options import options, write
from .player import Player


@runtime_typecheck
def get_players(
    player_list: list[str],
    add_no_hitters: bool | None = None,
    update_team_names: bool | None = None,
    ignore_errors: bool = True,
) -> list[Player]:
    """
    Returns a list of `Player` objects corresponding to the player IDs in `player_list`. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `player_list`: `list[str]`

        A list of player ID arguments like those for a [`Player`](https://github.com/john-bieren/brlib/wiki/Player) object.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Player.pitching` DataFrames, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names in `Player.info["Draft Team"]` such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `ignore_errors`: `bool`, default `True`

        Whether to suppress any raised exceptions. If `True`, players which raise an exception will be omitted from the returned list. If the exception is caused by the [rate limit](https://www.sports-reference.com/429.html) being exceeded, the list is returned as-is.

    ## Returns

    `list[Player]`

    ## Examples

    Gather some players of interest:

    ```
    >>> br.get_players(["hanigmi01", "mooredy01", "munozan01"])
    [Player('hanigmi01'), Player('mooredy01'), Player('munozan01')]
    ```

    Directly pass `players` attributes:

    ```
    >>> t = br.Team("OAK", "2023")
    >>> pl = br.get_players(t.players)
    [Player('wadety01'), Player('thomaco01'), Player('soderty01'), ...]
    ```
    """
    if add_no_hitters is None:
        add_no_hitters = options.add_no_hitters
    if update_team_names is None:
        update_team_names = options.update_team_names

    player_list = validate_player_list(player_list)
    if len(player_list) == 0:
        return []

    results = []
    for player_id in tqdm(
        iterable=list(dict.fromkeys(player_list)),
        unit="player",
        bar_format=options.pb_format,
        colour=options.pb_color,
        disable=options.pb_disable,
    ):
        endpoint = f"/players/{player_id[0]}/{player_id}.shtml"

        try:
            page = req_man.get_page(endpoint)
            result = Player(
                page=page,
                add_no_hitters=add_no_hitters,
                update_team_names=update_team_names,
            )
            results.append(result)
            req_man.pause()
        except Exception as exc:
            if not ignore_errors:
                raise
            exception_type = type(exc).__name__
            write(f"{exception_type}: {exc}")

            message = f"cannot get {player_id}"
            if exception_type == "ConnectionRefusedError":  # 429 error
                write(message + " or subsequent players")
                return results
            write(message)
            req_man.pause()
            continue
    return results
