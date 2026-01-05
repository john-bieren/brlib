from .all_major_leaguers import all_major_leaguers
from .find_asg import find_asg
from .find_games import find_games
from .find_teams import find_teams
from .game import Game
from .games import Games
from .get_games import get_games
from .get_players import get_players
from .get_teams import get_teams
from .options import Options, options
from .player import Player
from .players import Players
from .team import Team
from .teams import Teams

__version__ = "0.0.2"

__all__ = [
    "all_major_leaguers",
    "find_asg",
    "find_games",
    "find_teams",
    "Game",
    "Games",
    "get_games",
    "get_players",
    "get_teams",
    "options",
    "Player",
    "Players",
    "Team",
    "Teams"
]

all_major_leaguers.__doc__ = """
Returns a DataFrame of basic information about all players in major league history.

## Parameters

None.

## Returns

`pandas.DataFrame`

## Examples

The output (as of 2025-26 offseason):

```
>>> br.all_major_leaguers()
       Player ID             Name  Career Start  Career End  Active
0      aardsda01    David Aardsma          2004        2015   False
1      aaronha01      Henry Aaron          1954        1976   False
2      aaronto01     Tommie Aaron          1962        1971   False
3       aasedo01         Don Aase          1977        1990   False
4       abadan01        Andy Abad          2001        2006   False
...          ...              ...           ...         ...     ...
23610   zupofr01       Frank Zupo          1957        1961   False
23611  zuvelpa01     Paul Zuvella          1982        1991   False
23612  zuverge01  George Zuverink          1951        1959   False
23613  zwilldu01   Dutch Zwilling          1910        1916   False
23614   zychto01        Tony Zych          2015        2017   False

[23615 rows x 5 columns]
```

You can filter results and convert them into a `get_players` input:

```
>>> aml = br.all_major_leaguers()
>>> mask = aml["Player ID"].str.startswith("q")
>>> aml = aml.loc[mask]
>>> aml["Player ID"].values.tolist()
['quackke01', 'quallch01', 'quallji01', ...]
```
"""

find_asg.__doc__ = """
Returns a list of All-Star Game tuples which can be an input to `get_games`.

## Parameters

* `seasons`: `str` or `list[str]`, default `"ALL"`

    A year, inclusive range of years (e.g. `"2017-2019"`), `"all"`, or a list of multiple such inputs which specify the seasons from which to find All-Star Games.

## Returns

`list[tuple[str, str, str]]`

## Examples

Seasons which did not have All-Star Games are taken into account:

```
>>> br.find_asg("2019-2022")
[('allstar', '2019', '0'), ('allstar', '2021', '0'), ('allstar', '2022', '0')]
```

Seasons with two All-Star Games are also accounted for:

```
>>> br.find_asg("1962")
[('allstar', '1962', '1'), ('allstar', '1962', '2')]
```
"""

find_games.__doc__ = """
Returns a list of game tuples which can be an input to `get_games`.

## Parameters

* `teams`: `str` or `list[str]`, default `"ALL"`

    A team abbreviation (e.g. `"sea"`), `"all"`, or a list of team abbreviations to specify which teams' games should be found. Abbreviations are subject to era adjustment, and aliases are not accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

* `seasons`: `str` or `list[str]`, default `"ALL"`

    A year, inclusive range of years (e.g. `"2017-2019"`), `"all"`, or a list of multiple such inputs which specify the seasons from which to find games.

* `opponents`: `str` or `list[str]`, default `"ALL"`

    A valid `teams` input specifying the opponents which `teams` must be facing in returned games.

* `dates`: `str` or `list[str]`, default `"ALL"`

    A string representing a date in MMDD format as a number (e.g. `"0704"`), an inclusive range of such numbers (e.g. `"0314-0325"`), `"all"`, or a list of multiple such inputs which specify the dates from which games should be found.

* `home_away`: `str`, default `"ALL"`

    `"home"`, `"away"`, or `"all"` to specify the role which `teams` should have in returned games.

* `game_type`: `str`, default `"ALL"`

    `"reg"`, `"post"`, or `"all"` to specify whether to find regular season and/or postseason games.

## Returns

`list[tuple[str, str, str]]`

## Examples

Find all games from a team's season:

```
>>> br.find_games("SEA", "2020")
[('HOU', '20200724', '0'), ('HOU', '20200725', '0'), ...]
```

Find matchups between teams:

```
>>> br.find_games("SEA", "2019", "STL")
[('SEA', '20190702', '0'), ('SEA', '20190703', '0'), ('SEA', '20190704', '0')]
```

Abbreviations can match multiple teams due to era adjustment:

```
>>> br.find_games(teams="BAL", seasons="1915", dates="825-826", home_away="home")
[('BAL', '19150825', '1'), ('BAL', '19150825', '2'), ('SLB', '19150825', '0'), ('BAL', '19150826', '0'), ('SLB', '19150826', '0')]
```
"""

find_teams.__doc__ = """
Returns a list of team tuples which can be an input to `get_teams`.

## Parameters

* `teams`: `str` or `list[str]`, default `"ALL"`

    A team abbreviation (e.g. `"sea"`), segregation-era league identifier (i.e. `"bml"` for Black major league teams or `"wml"` for White major league teams), `"all"`, or a list of multiple such inputs to specify which teams' games should be found. Abbreviations are subject to era adjustment, and aliases are not accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

* `seasons`: `str` or `list[str]`, default `"ALL"`

    A year, inclusive range of years (e.g. `"2017-2019"`), `"all"`, or a list of multiple such inputs which specify the years from which to find games.

## Returns

`list[tuple[str, str]]`

## Examples

Find teams from a range of seasons without worrying about abbreviation changes:

```
>>> br.find_teams("OAK", "2022-2025")
[('OAK', '2022'), ('OAK', '2023'), ('OAK', '2024'), ('ATH', '2025')]
```

Survey entire seasons:

```
>>> br.find_teams("BML", "1948")
[('BBB', '1948'), ('BEG', '1948'), ('CAG', '1948'), ('CBE', '1948'), ...]
```

Abbreviations can match multiple teams due to era adjustment:

```
>>> br.find_teams("BAL", "1914")
[('SLB', '1914'), ('BAL', '1914')]
```
"""

Game.__doc__ = """
Statistics and information from a game. Can be initialized by specifying `home_team`, `date`, and `doubleheader`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded box score page. If neither of these sets of parameters are given, an exception is raised.

## Parameters

* `home_team`: `str`, default `""`

    The home team's abbreviation (e.g. `"sea"`), or, if the game is an All-Star Game, `"allstar"`. Era adjustment is not used, and aliases are accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

* `date`: `str`, default `""`

    The date of the game in YYYYMMDD format (e.g. `"20230830"`). Or, if the game is an All-Star Game, the year in YYYY format.

* `doubleheader`: `str`, default `""`

    The game's status as part of a doubleheader:
    * `"0"` if not part of a doubleheader.
    * `"1"` if first game of a doubleheader.
    * `"2"` if second game of a doubleheader.
    * `"3"` if third game of a tripleheader (i.e. [PIT192010023](https://www.baseball-reference.com/boxes/PIT/PIT192010023.shtml)).

    Or, if the game is an All-Star Game:
    * `"0"` if only ASG of the year.
    * `"1"` if first ASG of the year.
    * `"2"` if second ASG of the year.

* `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

    A previously loaded box score page.

* `add_no_hitters`: `bool` or `None`, default `None`

    Whether to populate the no-hitter columns in the `Game.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

## Attributes

* `id`: `str`

    The unique identifier for the game used in the URL (e.g. "SEA201805020").

* `name`: `str`

    The unique, pretty name of the game (e.g. "May 2, 2018, Oakland Athletics vs Seattle Mariners").

* `info`: `pandas.DataFrame`

    Contains information about the game and its circumstances.

* `batting`: `pandas.DataFrame`

    Contains batting and baserunning stats from the batting tables and the information beneath them.

* `pitching`: `pandas.DataFrame`

    Contains pitching stats from the pitching tables and the information beneath them.

* `fielding`: `pandas.DataFrame`

    Contains fielding stats from the batting tables and the information beneath them.

* `team_info`: `pandas.DataFrame`

    Contains information about the teams involved in the game.

* `ump_info`: `pandas.DataFrame`

    Contains the names and positions of the game's umpires.

* `linescore`: `pandas.DataFrame`

    Contains the game's linescore, a box score fixture which displays the teams' run totals by inning, among other stats.

* `players`: `list[str]`

    A list of the players who appeared in the game. Can be an input to `get_players`.

* `teams`: `list[tuple[str, str]]`

    A list of the teams involved in the game. Can be an input to `get_teams`.

## Examples

Load a game:

```
>>> br.Game("SEA", "20190926", "0").name
'September 26, 2019, Oakland Athletics vs Seattle Mariners'
```

Load an All-Star Game:

```
>>> br.Game("allstar", "2024", "0").name
'2024 All-Star Game, July 16'
```

## Methods

* [`Game.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Game.add_no_hitters)
* [`Game.update_team_names`](https://github.com/john-bieren/brlib/wiki/Game.update_team_names)
* [`Game.update_venue_name`](https://github.com/john-bieren/brlib/wiki/Game.update_venue_name)
"""

Game.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Game.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> g = br.Game("TOR", "20180508", "0")
>>> g.pitching[["Player", "Team", "NH", "PG", "CNH"]]
           Player               Team  NH  PG  CNH
0    James Paxton   Seattle Mariners NaN NaN  NaN
1     Team Totals   Seattle Mariners NaN NaN  NaN
2  Marcus Stroman  Toronto Blue Jays NaN NaN  NaN
3       Tim Mayza  Toronto Blue Jays NaN NaN  NaN
4   Jake Petricka  Toronto Blue Jays NaN NaN  NaN
5      Aaron Loup  Toronto Blue Jays NaN NaN  NaN
6     John Axford  Toronto Blue Jays NaN NaN  NaN
7     Team Totals  Toronto Blue Jays NaN NaN  NaN
>>> g.add_no_hitters()
>>> g.pitching[["Player", "Team", "NH", "PG", "CNH"]]
           Player               Team   NH   PG  CNH
0    James Paxton   Seattle Mariners  1.0  0.0  0.0
1     Team Totals   Seattle Mariners  1.0  0.0  0.0
2  Marcus Stroman  Toronto Blue Jays  0.0  0.0  0.0
3       Tim Mayza  Toronto Blue Jays  0.0  0.0  0.0
4   Jake Petricka  Toronto Blue Jays  0.0  0.0  0.0
5      Aaron Loup  Toronto Blue Jays  0.0  0.0  0.0
6     John Axford  Toronto Blue Jays  0.0  0.0  0.0
7     Team Totals  Toronto Blue Jays  0.0  0.0  0.0
```
"""

Game.update_team_names.__doc__ = """
Standardizes team names such that teams are identified by one name, excluding relocations.

## Parameters

None.

## Returns

`None`

## Example

```
>>> g = br.Game("FLO", "19940729", "0")
>>> g.info[["Away Team", "Home Team"]]
        Away Team        Home Team
0  Montreal Expos  Florida Marlins
>>> g.update_team_names()
>>> g.info[["Away Team", "Home Team"]]
        Away Team      Home Team
0  Montreal Expos  Miami Marlins
```
"""

Game.update_venue_name.__doc__ = """
Standardizes venue name such that venues are identified by one name.

## Parameters

None.

## Returns

`None`

## Example

```
>>> g = br.Game("FLO", "19940729", "0")
>>> g.info["Venue"]
0    Joe Robbie Stadium
Name: Venue, dtype: object
>>> g.update_venue_name()
>>> g.info["Venue"]
0    Hard Rock Stadium
Name: Venue, dtype: object
```
"""

Games.__doc__ = """
Aggregation of multiple `Game` objects.

## Parameters

* `games`: `list[Game]`

    The list of the games to aggregate.

## Attributes

* `info`: `pandas.DataFrame`

    Contains information about the games and their circumstances.

* `batting`: `pandas.DataFrame`

    Contains batting and baserunning stats from the batting tables and the information beneath them.

* `pitching`: `pandas.DataFrame`

    Contains pitching stats from the pitching tables and the information beneath them.

* `fielding`: `pandas.DataFrame`

    Contains fielding stats from the batting tables and the information beneath them.

* `team_info`: `pandas.DataFrame`

    Contains information about the teams involved in the games.

* `ump_info`: `pandas.DataFrame`

    Contains the names and positions of the games' umpires.

* `records`: `pandas.DataFrame`

    Contains team records in the games by franchise.

* `players`: `list[str]`

    A list of the players who appeared in the games. Can be an input to `get_players`.

* `teams`: `list[tuple[str, str]]`

    A list of the teams involved in the games. Can be an input to `get_teams`.

## Examples

Aggregate a list of `Game` objects:

```
>>> g1 = br.Game("SEA", "20180930", "0")                                          
>>> g2 = br.Game("SEA", "20190929", "0")
>>> br.Games([g1, g2])                
Games(Game('SEA', '20180930', '0'), Game('SEA', '20190929', '0'))
```

Directly pass `get_games` results:

```
>>> gl = br.get_games([("SEA", "20180930", "0"), ("SEA", "20190929", "0")])              
>>> br.Games(gl)
Games(Game('SEA', '20180930', '0'), Game('SEA', '20190929', '0'))
```

## Methods

* [`Games.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Games.add_no_hitters)
* [`Games.update_team_names`](https://github.com/john-bieren/brlib/wiki/Games.update_team_names)
* [`Games.update_venue_names`](https://github.com/john-bieren/brlib/wiki/Games.update_venue_names)
"""

Games.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Games.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> g1 = br.Game("SEA", "20120815", "0")
>>> g2 = br.Game("SEA", "20120608", "0")
>>> gs = br.Games([g1, g2])
>>> gs.pitching[["Player", "Team", "NH", "PG", "CNH"]]
               Player                 Team  NH  PG  CNH
0   Jeremy Hellickson       Tampa Bay Rays NaN NaN  NaN
1     Kyle Farnsworth       Tampa Bay Rays NaN NaN  NaN
2         Team Totals       Tampa Bay Rays NaN NaN  NaN
3     Félix Hernández     Seattle Mariners NaN NaN  NaN
4         Team Totals     Seattle Mariners NaN NaN  NaN
...               ...                  ... ... ...  ...
11      Stephen Pryor     Seattle Mariners NaN NaN  NaN
12       Lucas Luetge     Seattle Mariners NaN NaN  NaN
13     Brandon League     Seattle Mariners NaN NaN  NaN
14     Tom Wilhelmsen     Seattle Mariners NaN NaN  NaN
15        Team Totals     Seattle Mariners NaN NaN  NaN
>>> gs.add_no_hitters()
>>> gs.pitching[["Player", "Team", "NH", "PG", "CNH"]]
               Player                 Team   NH   PG  CNH
0   Jeremy Hellickson       Tampa Bay Rays  0.0  0.0  0.0
1     Kyle Farnsworth       Tampa Bay Rays  0.0  0.0  0.0
2         Team Totals       Tampa Bay Rays  0.0  0.0  0.0
3     Félix Hernández     Seattle Mariners  1.0  1.0  0.0
4         Team Totals     Seattle Mariners  1.0  1.0  0.0
...               ...                  ...  ...  ...  ...
11      Stephen Pryor     Seattle Mariners  0.0  0.0  1.0
12       Lucas Luetge     Seattle Mariners  0.0  0.0  1.0
13     Brandon League     Seattle Mariners  0.0  0.0  1.0
14     Tom Wilhelmsen     Seattle Mariners  0.0  0.0  1.0
15        Team Totals     Seattle Mariners  0.0  0.0  1.0
```
"""

Games.update_team_names.__doc__ = """
Standardizes team names such that teams are identified by one name, excluding relocations.

## Parameters

None.

## Returns

`None`

## Example

```
>>> g1 = br.Game("SEA", "20180401", "0")
>>> g2 = br.Game("TBA", "20050828", "0")
>>> gs = br.Games([g1, g2])
>>> gs.info[["Away Team", "Home Team"]]
                       Away Team             Home Team
0              Cleveland Indians      Seattle Mariners
1  Los Angeles Angels of Anaheim  Tampa Bay Devil Rays
>>> gs.update_team_names()
>>> gs.info[["Away Team", "Home Team"]]
             Away Team         Home Team
0  Cleveland Guardians  Seattle Mariners
1   Los Angeles Angels    Tampa Bay Rays
```
"""

Games.update_venue_names.__doc__ = """
Standardizes venue names such that venues are identified by one name.

## Parameters

None.

## Returns

`None`

## Example

```
>>> g1 = br.Game("SEA", "20180401", "0")
>>> g2 = br.Game("TBA", "20050828", "0")
>>> gs = br.Games([g1, g2])
>>> gs.info["Venue"]
0       Safeco Field
1    Tropicana Field
Name: Venue, dtype: object
>>> gs.update_venue_names()
>>> gs.info["Venue"]
0      T-Mobile Park
1    Tropicana Field
Name: Venue, dtype: object
```
"""

get_games.__doc__ = """
Returns a list of `Game` objects corresponding to the input list of tuples which mimic the `Game` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

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

get_players.__doc__ = """
Returns a list of `Player` objects corresponding to the input list of player IDs. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

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

get_teams.__doc__ = """
Returns a list of `Team` objects corresponding to the input list of tuples which mimic the `Team` initialization parameters. By default, a progress bar will appear in the terminal. You can change this behavior with [`options.pb_disable`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

* `team_list`: `list[tuple[str, str]]`

    A list of tuples containing `team`, and `season` arguments like those for a [`Team`](https://github.com/john-bieren/brlib/wiki/Team) object.

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

Options.__doc__ = """
Options to change brlib's behavior. The options' values can be read or set using attributes. The type of an assigned value must match that of the option's default value, unless the assigned value is `None`, which removes a previous assignment.

## Attributes

* `add_no_hitters`, default `False`

    Default value for `add_no_hitters` arguments when initializing `Game`, `Player`, and `Team` objects.

* `request_buffer`, default `2.015`

    Buffer, in seconds, between requests. Necessary to obey Baseball Reference's [rate limit](https://www.sports-reference.com/429.html).

* `timeout_limit`, default `10`

    Timeout parameter for requests.

* `max_retries`, default `2`

    Number of retries to attempt on failed requests.

* `pb_format`, default `"{percentage:3.2f}%|{bar}{r_bar}"`

    The format of the progress bar. The value is passed to the tqdm `bar_format` argument, read the tqdm docs [here](https://tqdm.github.io/docs/tqdm).

* `pb_color`, default `"#cccccc"`

    The color of the progress bar. The value is passed to the tqdm `colour` argument, read the tqdm docs [here](https://tqdm.github.io/docs/tqdm).

* `pb_disable`, default `False`

    Whether to disable the progress bar.

* `print_pages`, default `False`

    Whether to print descriptions of visited pages.

* `dev_alerts`, default `False`

    Whether to print alerts meant for brlib developers.

* `quiet`, default `False`

    Whether to mute most printed messages.

## Examples

Read the value of an option:

```
>>> br.options.request_buffer
2.015
```

Change an option's value for the duration of the session:

```
>>> br.options.pb_disable = True
```

Remove the assigned value:

```
>>> br.options.print_pages = True
>>> br.options.print_pages
True
>>> br.options.print_pages = None
>>> br.options.print_pages
False
```

## Methods

* [`options.clear_cache`](https://github.com/john-bieren/brlib/wiki/options.clear_cache)
* [`options.clear_preferences`](https://github.com/john-bieren/brlib/wiki/options.clear_preferences)
* [`options.set_preference`](https://github.com/john-bieren/brlib/wiki/options.set_preference)
"""

Options.clear_cache.__doc__ = """
Deletes all files in the cache directory. The cache will be replenished when necessary in a future session, but the deleted data will persist for the duration of the current session.

## Parameters

None.

## Returns

`None`

## Example

Clear the cache:

```
>>> br.options.clear_cache()
```
"""

Options.clear_preferences.__doc__ = """
Resets option preferences for current and future sessions.

## Parameters

None.

## Returns

`None`

## Examples

Changes take effect immediately:

```
>>> br.options.set_preference("print_pages", True)
>>> br.options.print_pages
True
>>> br.options.clear_preferences()
>>> br.options.print_pages
False
```

Session-level changes to option values persist:

```
>>> br.options.set_preference("max_retries", 5)
>>> br.options.max_retries
5
>>> br.options.max_retries = 3
>>> br.options.clear_preferences()
>>> br.options.max_retries
3
```
"""

Options.set_preference.__doc__ = """
Changes the default value of an option for current and future sessions.

## Parameters

* `option`: `str`

    The name of the option.

* `value`: `Any`

    The new default value. Must use the correct type for the given option. Use `None` to remove a preference.

## Returns

`None`

## Examples

Setting and removing a preference:

```
>>> br.options.set_preference("add_no_hitters", True)
>>> br.options.add_no_hitters
True
>>> br.options.set_preference("add_no_hitters", None)
>>> br.options.add_no_hitters
False
```

Session-level changes to option values persist:

```
>>> br.options.max_retries = 3
>>> br.options.set_preference("max_retries", 5)
>>> br.options.max_retries
3
>>> br.options.max_retries = None
>>> br.options.max_retries
5
```
"""

Player.__doc__ = """
Statistics and information from a player. Can be initialized by specifying `player_id`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded player page. If neither of these parameters are given, an exception is raised.

## Parameters

* `player_id`: `str`, default `""`

    The first 5 letters of the player's last name, followed by the first two letters of their first name, and two digits as a unique identifier. This ID can be found in the URL of the player's page.

* `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

    A previously loaded player page.

* `add_no_hitters`: `bool` or `None`, default `None`

    Whether to populate the no-hitter columns in the `Player.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

## Attributes

* `id`: `str`

    The unique identifier for the player used in the URL (e.g. `"vogelda01"`).

* `name`: `str`

    The player's name (e.g. `"Daniel Vogelbach"`).

* `info`: `pandas.DataFrame`

    Contains biographical information about the player.

* `bling`: `pandas.DataFrame`

    Contains the player's career accolades as displayed by the banners in the upper right-hand corner of their page.

* `batting`: `pandas.DataFrame`

    Contains the player's batting and baserunning stats from the three batting tables.

* `pitching`: `pandas.DataFrame`

    Contains the player's pitching stats from the three pitching tables.

* `fielding`: `pandas.DataFrame`

    Contains the player's fielding stats from the standard fielding table.

* `relatives`: `dict[str: list[str]]`

    The player's relationships with other major leaguers. The relationships are they keys, and the values list the players. These values can be inputs to `get_players`.

* `teams`: `list[tuple[str, str]]`

    A list of the teams on which the player appeared. Can be an input to `get_teams`.

## Example

Load a player:

```
>>> br.Player("whiteev01").name
'Evan White'
```

## Methods

* [`Player.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Player.add_no_hitters)
* [`Player.update_team_name`](https://github.com/john-bieren/brlib/wiki/Player.update_team_name)
"""

Player.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Player.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> p = br.Player("gilbety01")
>>> p.pitching[["Team", "Season", "NH", "PG", "CNH"]]
    Team         Season  NH  PG  CNH
0    ARI           2021 NaN NaN  NaN
1    ARI           2022 NaN NaN  NaN
2    ARI           2023 NaN NaN  NaN
3    PHI           2024 NaN NaN  NaN
4    CHW           2025 NaN NaN  NaN
5   None  Career Totals NaN NaN  NaN
6   None   162 Game Avg NaN NaN  NaN
7    ARI  Career Totals NaN NaN  NaN
8    CHW  Career Totals NaN NaN  NaN
9    PHI  Career Totals NaN NaN  NaN
10  None  Career Totals NaN NaN  NaN
11  None  Career Totals NaN NaN  NaN
>>> p.add_no_hitters()
>>> p.pitching[["Team", "Season", "NH", "PG", "CNH"]]
    Team         Season   NH   PG  CNH
0    ARI           2021  1.0  0.0  0.0
1    ARI           2022  0.0  0.0  0.0
2    ARI           2023  0.0  0.0  0.0
3    PHI           2024  0.0  0.0  0.0
4    CHW           2025  0.0  0.0  0.0
5   None  Career Totals  1.0  0.0  0.0
6   None   162 Game Avg  NaN  NaN  NaN
7    ARI  Career Totals  1.0  0.0  0.0
8    CHW  Career Totals  0.0  0.0  0.0
9    PHI  Career Totals  0.0  0.0  0.0
10  None  Career Totals  NaN  NaN  NaN
11  None  Career Totals  NaN  NaN  NaN
```
"""

Player.update_team_name.__doc__ = """
Standardizes team name in `Player.info["Draft Team"]` such that teams are identified by one name, excluding relocations.

## Parameters

None.

## Returns

`None`

## Example

```
>>> p = br.Player("beckejo02")
>>> p.info["Draft Team"]
0    Florida Marlins
Name: Draft Team, dtype: object
>>> p.update_team_name()
>>> p.info["Draft Team"]
0    Miami Marlins
Name: Draft Team, dtype: object
```
"""

Players.__doc__ = """
Aggregation of multiple `Player` objects.

## Parameters

* `players`: `list[Player]`

    The list of the players to aggregate.

## Attributes

* `info`: `pandas.DataFrame`

    Contains biographical information about the players.

* `bling`: `pandas.DataFrame`

    Contains the players' career accolades as displayed by the banners in the upper right-hand corner of their pages.

* `batting`: `pandas.DataFrame`

    Contains the players' batting and baserunning stats.

* `pitching`: `pandas.DataFrame`

    Contains the players' pitching stats.

* `fielding`: `pandas.DataFrame`

    Contains the players' fielding stats.

* `teams`: `list[tuple[str, str]]`

    A list of the teams on which the players appeared. Can be an input to `get_teams`.

## Examples

Aggregate a list of `Player` objects:

```
>>> p1 = br.Player("lewisky01")
>>> p2 = br.Player("sanchsi01")
>>> br.Players([p1, p2])
Players(Player(lewisky01), Player(sanchsi01))
```

Directly pass `get_players` results:

```
>>> pl = br.get_players(["lewisky01", "sanchsi01"])
>>> br.Players(pl)      
Players(Player(lewisky01), Player(sanchsi01))
```

## Methods

* [`Players.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Players.add_no_hitters)
* [`Players.update_team_names`](https://github.com/john-bieren/brlib/wiki/Players.update_team_names)
"""

Players.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Players.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> p1 = br.Player("coleta01")
>>> p2 = br.Player("penafe01")
>>> ps = br.Players([p1, p2])
>>> mask = ps.pitching["Season"].str.len() == 4
>>> ps.pitching.loc[mask, ["Player", "Season", "NH", "PG", "CNH"]]
         Player Season  NH  PG  CNH
0   Taylor Cole   2017 NaN NaN  NaN
1   Taylor Cole   2018 NaN NaN  NaN
2   Taylor Cole   2019 NaN NaN  NaN
7    Félix Peña   2016 NaN NaN  NaN
8    Félix Peña   2017 NaN NaN  NaN
9    Félix Peña   2018 NaN NaN  NaN
10   Félix Peña   2019 NaN NaN  NaN
11   Félix Peña   2020 NaN NaN  NaN
12   Félix Peña   2021 NaN NaN  NaN
>>> ps.add_no_hitters()
>>> ps.pitching.loc[mask, ["Player", "Season", "NH", "PG", "CNH"]]
         Player Season   NH   PG  CNH
0   Taylor Cole   2017  0.0  0.0  0.0
1   Taylor Cole   2018  0.0  0.0  0.0
2   Taylor Cole   2019  0.0  0.0  1.0
7    Félix Peña   2016  0.0  0.0  0.0
8    Félix Peña   2017  0.0  0.0  0.0
9    Félix Peña   2018  0.0  0.0  0.0
10   Félix Peña   2019  0.0  0.0  1.0
11   Félix Peña   2020  0.0  0.0  0.0
12   Félix Peña   2021  0.0  0.0  0.0
```
"""

Players.update_team_names.__doc__ = """
Standardizes team names in `Players.info["Draft Team"]` such that teams are identified by one name, excluding relocations.

## Parameters

None.

## Returns

`None`

## Example

```
>>> pl = br.get_players(["longoev01", "shielja02", "uptonbj01"])
>>> ps = br.Players(pl)
>>> ps.info["Draft Team"]
0    Tampa Bay Devil Rays
1    Tampa Bay Devil Rays
2    Tampa Bay Devil Rays
Name: Draft Team, dtype: object
>>> ps.update_team_names()
>>> ps.info["Draft Team"]
0    Tampa Bay Rays
1    Tampa Bay Rays
2    Tampa Bay Rays
Name: Draft Team, dtype: object
```
"""

Team.__doc__ = """
Statistics and information from a team. Can be initialized by specifying `team`, and `season`, and the associated page will be loaded automatically. Can also be initialized with a previously loaded team page. If neither of these sets of parameters are given, an exception is raised.

## Parameters

* `team`: `str`, default `""`

    The team's abbreviation. Era adjustment is not used, and aliases are not accepted. [Read more about team abbreviation handling](https://github.com/john-bieren/brlib/wiki/Team-Abbreviation-Handling).

* `season`: `str`, default `""`

    The year in which the team played in YYYY format (e.g. `"2022"`).

* `page`: `curl_cffi.requests.Response`, default `curl_cffi.requests.Response()`

    A previously loaded team page.

* `add_no_hitters`: `bool` or `None`, default `None`

    Whether to populate the no-hitter columns in the `Team.pitching` DataFrame, which are empty by default (may require an additional request). If no value is passed, the value of `options.add_no_hitters` is used.

## Attributes

* `id`: `str`

    The unique identifier for the team made up of its abbreviation and season (e.g. `"SEA2017"`).

* `name`: `str`

    The team's name (e.g. `"2017 Seattle Mariners"`).

* `info`: `pandas.DataFrame`

    Contains information about the team, its results, and its personnel.

* `batting`: `pandas.DataFrame`

    Contains the team's batting and baserunning stats from the two batting tables.

* `pitching`: `pandas.DataFrame`

    Contains the team's pitching stats from the two pitching tables.

* `fielding`: `pandas.DataFrame`

    Contains the team's fielding stats from the standard fielding table.

* `players`: `list[str]`

    A list of the players who played for the team. Can be an input to `get_players`.

## Example

Load a team:

```
>>> br.Team("SDP", "2022").name
'2022 San Diego Padres'
```

## Methods

* [`Team.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Team.add_no_hitters)
"""

Team.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Team.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> t = br.Team("BOS", "1904")
>>> t.pitching[["Player", "NH", "PG", "CNH"]]
            Player  NH  PG  CNH
0         Cy Young NaN NaN  NaN
1    George Winter NaN NaN  NaN
2  Jesse Tannehill NaN NaN  NaN
3   Norwood Gibson NaN NaN  NaN
4     Bill Dinneen NaN NaN  NaN
5      Team Totals NaN NaN  NaN
>>> t.add_no_hitters()
>>> t.pitching[["Player", "NH", "PG", "CNH"]]
            Player   NH   PG  CNH
0         Cy Young  1.0  1.0  0.0
1    George Winter  0.0  0.0  0.0
2  Jesse Tannehill  1.0  0.0  0.0
3   Norwood Gibson  0.0  0.0  0.0
4     Bill Dinneen  0.0  0.0  0.0
5      Team Totals  2.0  1.0  0.0
```
"""

Teams.__doc__ = """
Aggregation of multiple `Team` objects.

## Parameters

* `teams`: `list[Team]`

    The list of the teams to aggregate.

## Attributes

* `info`: `pandas.DataFrame`

    Contains information about the teams, their results, and their personnel.

* `batting`: `pandas.DataFrame`

    Contains the teams' batting and baserunning stats.

* `pitching`: `pandas.DataFrame`

    Contains the teams' pitching stats.

* `fielding`: `pandas.DataFrame`

    Contains the teams' fielding stats.

* `records`: `pandas.DataFrame`

    Contains the teams' regular season records by franchise.

* `players`: `list[str]`

    A list of the players who played for the teams. Can be an input to `get_players`.

## Examples

Aggregate a list of `Team` objects:

```
>>> t1 = br.Team("SEP", "1969")
>>> t2 = br.Team("MLA", "1901")
>>> br.Teams([t1, t2])
Teams(Team('SEP', '1969'), Team('MLA', '1901'))
```

Directly pass `get_teams` results:

```
>>> tl = br.get_teams([("SEP", "1969"), ("MLA", "1901")])
>>> br.Teams(tl)
Teams(Team('SEP', '1969'), Team('MLA', '1901'))
```

## Methods

* [`Teams.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/Teams.add_no_hitters)
"""

Teams.add_no_hitters.__doc__ = """
Populates the no-hitter columns in the `Teams.pitching` DataFrame, which are empty by default (may require an additional request). You can change this behavior with [`options.add_no_hitters`](https://github.com/john-bieren/brlib/wiki/options).

## Parameters

None.

## Returns

`None`

## Example

```
>>> t1 = br.Team("BOS", "1917")
>>> t2 = br.Team("PRO", "1883")
>>> ts = br.Teams([t1, t2])
>>> ts.pitching[["Player", "NH", "PG", "CNH"]]
               Player  NH  PG  CNH
0      Weldon Wyckoff NaN NaN  NaN
1         Ernie Shore NaN NaN  NaN
2           Babe Ruth NaN NaN  NaN
3        Herb Pennock NaN NaN  NaN
4           Carl Mays NaN NaN  NaN
5       Dutch Leonard NaN NaN  NaN
6       Sad Sam Jones NaN NaN  NaN
7         Rube Foster NaN NaN  NaN
8          Lore Bader NaN NaN  NaN
9         Team Totals NaN NaN  NaN
10    Charlie Sweeney NaN NaN  NaN
11       Lee Richmond NaN NaN  NaN
12  Old Hoss Radbourn NaN NaN  NaN
13        Team Totals NaN NaN  NaN
>>> ts.add_no_hitters()
>>> ts.pitching[["Player", "NH", "PG", "CNH"]]
               Player   NH   PG  CNH
0      Weldon Wyckoff  0.0  0.0  0.0
1         Ernie Shore  0.0  0.0  1.0
2           Babe Ruth  0.0  0.0  1.0
3        Herb Pennock  0.0  0.0  0.0
4           Carl Mays  0.0  0.0  0.0
5       Dutch Leonard  0.0  0.0  0.0
6       Sad Sam Jones  0.0  0.0  0.0
7         Rube Foster  0.0  0.0  0.0
8          Lore Bader  0.0  0.0  0.0
9         Team Totals  0.0  0.0  1.0
10    Charlie Sweeney  0.0  0.0  0.0
11       Lee Richmond  0.0  0.0  0.0
12  Old Hoss Radbourn  0.0  0.0  0.0
13        Team Totals  0.0  0.0  0.0
```
"""
