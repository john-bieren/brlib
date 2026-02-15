"""Defines `get_games` function."""

from tqdm import tqdm

from ._helpers.inputs import validate_game_list
from ._helpers.requests_manager import req_man
from ._helpers.utils import runtime_typecheck, str_between
from .game import Game
from .options import options, write


@runtime_typecheck
def get_games(
    game_list: list[tuple[str, str, str]],
    add_no_hitters: bool | None = None,
    update_team_names: bool | None = None,
    update_venue_names: bool | None = None,
    ignore_errors: bool = True,
) -> list[Game]:
    """
    Returns a list of `Game` objects corresponding to the tuples in `game_list`, which mimic the `Game` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `game_list`: `list[tuple[str, str, str]]`

        A list of tuples containing `home_team`, `date`, and `doubleheader` arguments like those for a [`Game`](https://github.com/john-bieren/brlib/wiki/Game) object.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Game.pitching` DataFrames, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names such that teams are identified by one name, excluding relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `update_venue_names`: `bool` or `None`, default `None`

        Whether to standardize venue names such that venues are identified by one name. If no value is passed, the value of `options.update_venue_names` is used.

    * `ignore_errors`: `bool`, default `True`

        Whether to suppress any raised exceptions. If `True`, games which raise an exception will be omitted from the returned list. If the exception is caused by the [rate limit](https://www.sports-reference.com/429.html) being exceeded, the list is returned as-is.

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
    if update_team_names is None:
        update_team_names = options.update_team_names
    if update_venue_names is None:
        update_venue_names = options.update_venue_names

    game_list = validate_game_list(game_list)
    if len(game_list) == 0:
        return []

    results = []
    for home_team, date, doubleheader in tqdm(
        iterable=list(dict.fromkeys(game_list)),
        unit="game",
        bar_format=options.pb_format,
        colour=options.pb_color,
        disable=options.pb_disable,
    ):
        if home_team == "ALLSTAR":
            game_number = f"-{doubleheader}" if doubleheader != "0" else ""
            endpoint = f"/allstar/{date}-allstar-game{game_number}.shtml"
        else:
            endpoint = f"/boxes/{home_team}/{home_team}{date}{doubleheader}.shtml"

        try:
            page = req_man.get_page(endpoint)
            result = Game(
                page=page,
                add_no_hitters=add_no_hitters,
                update_team_names=update_team_names,
                update_venue_names=update_venue_names,
            )
            results.append(result)
            req_man.pause()
        except Exception as exc:
            if not ignore_errors:
                raise
            exception_type = type(exc).__name__
            write(f"{exception_type}: {exc}")

            game_id = str_between(endpoint, "/", ".", anchor="end")
            message = f"cannot get {game_id}"
            if exception_type == "ConnectionRefusedError":  # 429 error
                write(message + " or subsequent games")
                return results
            write(message)
            req_man.pause()
            continue
    return results
