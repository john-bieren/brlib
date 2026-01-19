#!/usr/bin/env python3

"""Defines get_games function."""

from tqdm import tqdm

from ._helpers.inputs import validate_game_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck
from .game import Game
from .options import options


@runtime_typecheck
def get_games(
        game_list: list[tuple[str, str, str]],
        add_no_hitters: bool | None = None
        ) -> list[Game]:
    """
    Returns a list of `Game` objects corresponding to the tuples in `game_list`, which mimic the `Game` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `game_list`: `list[tuple[str, str, str]]`

        A list of tuples containing `home_team`, `date`, and `doubleheader` arguments like those for a [`Game`](https://github.com/john-bieren/brlib/wiki/Game) object.

    ## Returns

    `list[Game]`

    ## Examples

    Gather some games of interest:

    ```
    >>> br.get_games([("SEA", "20110624", "0"), ("SEA", "20230522", "0")])
    [Game('SEA', '20110624', '0'), Game('SEA', '20230522', '0')]
    ```

    Directly pass `find_games` results:

    ```
    >>> fg = br.find_games("SEA", "2025", dates="1015-1031", home_away="HOME", game_type="POST")
    >>> br.get_games(fg)
    [Game('SEA', '20251015', '0'), Game('SEA', '20251016', '0'), Game('SEA', '20251017', '0')]
    ```
    """
    if add_no_hitters is None:
        add_no_hitters = options.add_no_hitters

    game_list = validate_game_list(game_list)
    if len(game_list) == 0:
        return []

    results = []
    for home_team, date, doubleheader in tqdm(
            iterable=list(dict.fromkeys(game_list)),
            unit="game",
            bar_format=options.pb_format,
            colour=options.pb_color,
            disable=options.pb_disable
            ):
        if home_team == "ALLSTAR":
            game_number = f"-{doubleheader}" if doubleheader != "0" else ""
            endpoint = f"/allstar/{date}-allstar-game{game_number}.shtml"
        else:
            endpoint = f"/boxes/{home_team}/{home_team}{date}{doubleheader}.shtml"

        page = req_man.get_page(endpoint)
        result = Game(page=page, add_no_hitters=add_no_hitters)
        results.append(result)
        req_man.pause()
    return results
