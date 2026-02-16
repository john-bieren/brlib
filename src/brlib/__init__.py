"""
## Directory

### Data Classes

Collections of statistics and information about their subject.

* [`Game`](https://github.com/john-bieren/brlib/wiki/Game)
    * [`Game.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Game.add_no_hitters)
    * [`Game.update_team_names`](https://github.com/john-bieren/brlib/wiki/Game.update_team_names)
    * [`Game.update_venue_names`](https://github.com/john-bieren/brlib/wiki/Game.update_venue_names)
* [`Player`](https://github.com/john-bieren/brlib/wiki/Player)
    * [`Player.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Player.add_no_hitters)
    * [`Player.update_team_names`](https://github.com/john-bieren/brlib/wiki/Player.update_team_names)
* [`Team`](https://github.com/john-bieren/brlib/wiki/Team)
    * [`Team.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Team.add_no_hitters)
    * [`Team.update_team_names`](https://github.com/john-bieren/brlib/wiki/Team.update_team_names)
    * [`Team.update_venue_names`](https://github.com/john-bieren/brlib/wiki/Team.update_venue_names)

### `get` Functions

Convert a list of inputs to the constructors of the above classes into a list of instances of the
classes.

* [`get_games`](https://github.com/john-bieren/brlib/wiki/get_games)
* [`get_players`](https://github.com/john-bieren/brlib/wiki/get_players)
* [`get_teams`](https://github.com/john-bieren/brlib/wiki/get_teams)

### `find` Functions

Find inputs to the `get` functions based on search parameters.

* [`find_asg`](https://github.com/john-bieren/brlib/wiki/find_asg)
* [`find_games`](https://github.com/john-bieren/brlib/wiki/find_games)
* [`find_teams`](https://github.com/john-bieren/brlib/wiki/find_teams)
* In most cases, the best way to find players of interest is to use the `players` attribute of a
`Game` or `Team`. The `all_players` function can also be used, but you must handle filtering of the
results and conversion into a valid `get_players` input.

### `Set` Classes

Aggregate the contents of multiple data class objects into a single object for easy analysis of
larger samples.

* [`GameSet`](https://github.com/john-bieren/brlib/wiki/GameSet)
    * [`GameSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/GameSet.add_no_hitters)
    * [`GameSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/GameSet.update_team_names)
    * [`GameSet.update_venue_names`](https://github.com/john-bieren/brlib/wiki/GameSet.update_venue_names)
* [`PlayerSet`](https://github.com/john-bieren/brlib/wiki/PlayerSet)
    * [`PlayerSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/PlayerSet.add_no_hitters)
    * [`PlayerSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/PlayerSet.update_team_names)
* [`TeamSet`](https://github.com/john-bieren/brlib/wiki/TeamSet)
    * [`TeamSet.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/TeamSet.add_no_hitters)
    * [`TeamSet.update_team_names`](https://github.com/john-bieren/brlib/wiki/TeamSet.update_team_names)
    * [`TeamSet.update_venue_names`](https://github.com/john-bieren/brlib/wiki/TeamSet.update_venue_names)

### Other Functions

* [`all_players`](https://github.com/john-bieren/brlib/wiki/all_players)

### [`options`](https://github.com/john-bieren/brlib/wiki/options)

* [`options.clear_cache`](https://github.com/john-bieren/brlib/wiki/options.clear_cache)
* [`options.clear_preferences`](https://github.com/john-bieren/brlib/wiki/options.clear_preferences)
* [`options.set_preference`](https://github.com/john-bieren/brlib/wiki/options.set_preference)

### Other

* [DataFrames Info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info)
* [Team Abbreviation Handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling)
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
