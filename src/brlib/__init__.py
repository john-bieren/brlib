"""
A library for collecting baseball statistics from [Baseball
Reference](https://www.baseball-reference.com).

Documentation can be found on the [wiki](https://github.com/john-bieren/brlib/wiki).
"""

from .all_players import all_players
from .find_asg import find_asg
from .find_games import find_games
from .find_teams import find_teams
from .game import Game
from .game_set import GameSet
from .get_games import get_games
from .get_players import get_players
from .get_teams import get_teams
from .options import options
from .player import Player
from .player_set import PlayerSet
from .team import Team
from .team_set import TeamSet

__version__ = "0.3.0.dev0"

__all__ = [
    "all_players",
    "find_asg",
    "find_games",
    "find_teams",
    "Game",
    "GameSet",
    "get_games",
    "get_players",
    "get_teams",
    "options",
    "Player",
    "PlayerSet",
    "Team",
    "TeamSet",
]
