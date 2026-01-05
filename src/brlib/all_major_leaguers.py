#!/usr/bin/env python3

"""Defines all_major_leaguers function."""

from io import StringIO

import pandas as pd

from ._helpers.requests_manager import req_man
from .options import print_page


def all_major_leaguers() -> pd.DataFrame:
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

    columns=["Player ID", "Name", "Career Start", "Career End", "Active"]
    players_df = players_df.reindex(columns=columns)
    return players_df
