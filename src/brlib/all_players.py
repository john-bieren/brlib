"""Defines `all_players` function."""

from io import StringIO

import pandas as pd

from ._helpers.requests_manager import req_man
from .options import print_page


def all_players() -> pd.DataFrame:
    """
    Returns a DataFrame of basic information about all players in major league history.
    [See DataFrame info](https://github.com/john-bieren/brlib/wiki/DataFrames-Info#all_players)

    ## Parameters

    None

    ## Returns

    `pandas.DataFrame`

    ## Examples

    The output (as of 2025-26 offseason):

    ```
    >>> br.all_players()
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
    >>> ap = br.all_players()
    >>> mask = ap["Player ID"].str.startswith("q")
    >>> ap = ap.loc[mask]
    >>> ap["Player ID"].values.tolist()
    ['quackke01', 'quallch01', 'quallji01', ...]
    ```
    """
    page = req_man.get_page("/short/inc/players_search_list.csv")
    print_page("All MLB Players")
    csv_lines = str(page.content, "UTF-8").strip()
    # add column names, which are not included in the payload
    columns = "Player ID,Name,Career Span,Active,1,2,3,4,5\n"
    players_df = pd.read_csv(StringIO(columns + csv_lines))

    # split career span into start and end (if span is one year, only year is listed, no range)
    players_df["Career Start"] = players_df["Career Span"].str.split("-", n=1).str[0].astype(int)
    players_df["Career End"] = players_df["Career Span"].str.split("-", n=1).str[-1].astype(int)
    # convert active column from 0/1 to boolean
    players_df["Active"] = players_df["Active"].astype(bool)

    columns = ["Player ID", "Name", "Career Start", "Career End", "Active"]
    players_df = players_df.reindex(columns=columns)
    return players_df
