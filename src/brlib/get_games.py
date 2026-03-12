"""Defines `get_games` function."""

from tqdm import tqdm

from ._helpers.inputs import validate_game_list
from ._helpers.requests_manager import req_mgr
from ._helpers.typechecking import runtime_typecheck
from ._helpers.utils import game_id_to_endpoint
from .game import Game
from .options import options, write


@runtime_typecheck
def get_games(
    game_list: list[str],
    add_no_hitters: bool | None = None,
    update_team_names: bool | None = None,
    update_venue_names: bool | None = None,
    ignore_errors: bool = True,
) -> list[Game]:
    """
    Returns a list of `Game` objects corresponding to the game IDs in `game_list`. By default, a
    progress bar will appear in the terminal. You can change this behavior with
    [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

    ## Parameters

    * `game_list`: `list[str]`

        A list of game IDs.

    * `add_no_hitters`: `bool` or `None`, default `None`

        Whether to populate the no-hitter columns in the `Game.pitching` DataFrames, which are empty
        by default (may require an additional request). If no value is passed, the value of
        `options.add_no_hitters` is used.

    * `update_team_names`: `bool` or `None`, default `None`

        Whether to standardize team names such that teams are identified by one name, excluding
        relocations. If no value is passed, the value of `options.update_team_names` is used.

    * `update_venue_names`: `bool` or `None`, default `None`

        Whether to standardize venue names such that venues are identified by one name. If no value
        is passed, the value of `options.update_venue_names` is used.

    * `ignore_errors`: `bool`, default `True`

        Whether to suppress any raised exceptions. If `True`, games which raise an exception will be
        omitted from the returned list. If the exception is caused by the [rate
        limit](https://www.sports-reference.com/429.html) being exceeded, the list is returned
        as-is.

    ## Returns

    `list[Game]`

    ## Examples

    Gather some games of interest:

    ```
    >>> br.get_games(["SEA201106240", "SEA202305220"])
    [Game('SEA201106240'), Game('SEA202305220')]
    ```

    Directly pass `find_games` results:

    ```
    >>> fg = br.find_games("SEA", "2025", dates="1015-1031", home_away="HOME", game_type="POST")
    >>> br.get_games(fg)
    [Game('SEA202510150'), Game('SEA202510160'), Game('SEA202510170')]
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
    for game_id in tqdm(
        iterable=list(dict.fromkeys(game_list)),
        unit="game",
        bar_format=options.pb_format,
        colour=options.pb_color,
        disable=options.pb_disable,
    ):
        endpoint = game_id_to_endpoint(game_id)

        try:
            page = req_mgr.get_page(endpoint)
            result = Game(
                page=page,
                add_no_hitters=add_no_hitters,
                update_team_names=update_team_names,
                update_venue_names=update_venue_names,
            )
            results.append(result)
            req_mgr.pause()
        except Exception as exc:
            if not ignore_errors:
                raise
            exception_type = type(exc).__name__
            write(f"{exception_type}: {exc}")

            message = f"cannot get {game_id}"
            if exception_type == "ConnectionRefusedError":  # 429 error
                write(message + " or subsequent games")
                return results
            write(message)
            req_mgr.pause()
            continue
    return results
