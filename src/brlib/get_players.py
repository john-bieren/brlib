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
