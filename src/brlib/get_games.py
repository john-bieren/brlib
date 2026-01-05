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
