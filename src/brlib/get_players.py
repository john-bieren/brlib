#!/usr/bin/env python3

"""Defines get_players function."""

from tqdm import tqdm

from ._helpers.inputs import validate_player_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck
from .options import options
from .player import Player


@runtime_typecheck
def get_players(
        player_list: list[str],
        add_no_hitters: bool | None = None
        ) -> list[Player]:
    """
    Returns a list of `Player` objects corresponding to the player IDs in `player_list`. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `player_list`: `list[str]`

        A list of player ID arguments like those for a [`Player`](https://github.com/john-bieren/brlib/wiki/Player) object.

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

    player_list = validate_player_list(player_list)
    if len(player_list) == 0:
        return []

    results = []
    for player_id in tqdm(
            iterable=list(dict.fromkeys(player_list)),
            unit="player",
            bar_format=options.pb_format,
            colour=options.pb_color,
            disable=options.pb_disable
            ):
        endpoint = f"/players/{player_id[0]}/{player_id}.shtml"

        page = req_man.get_page(endpoint)
        result = Player(page=page, add_no_hitters=add_no_hitters)
        results.append(result)
        req_man.pause()
    return results
