"""Defines utility functions used throughout the codebase."""

from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Tag


def str_between(string: str, start: str, end: str, anchor: str = "start") -> str:
    """
    Returns the substring of `string` which appears between `start` and `end`.
    `string` must contain `start` and `end`.

    If `anchor` is `"start"`, the substring between the first occurrence of `start`
    and the first subsequent occurrence of `end` will be returned.

    If `anchor` is `"end"`, the substring between the final occurrence of `end`
    and the final prior occurrence of `start` will be returned.
    """
    if start not in string:
        raise ValueError("start value not in string")
    if end not in string:
        raise ValueError("end value not in string")

    if anchor == "start":
        return string.split(start, maxsplit=1)[1].split(end, maxsplit=1)[0]
    if anchor == "end":
        return string.rsplit(end, maxsplit=1)[0].rsplit(start, maxsplit=1)[1]
    raise ValueError('anchor value must be "start" or "end"')


def str_remove(string: str, *substrings: str) -> str:
    """Removes instances of `substrings` from `string`."""
    for substring in substrings:
        string = string.replace(substring, "")
    return string


def clean_spaces(string: str) -> str:
    """Removes consecutive, leading, and trailing spaces from `string`."""
    return " ".join(string.split()).strip()


def reformat_date(string_date: str) -> str:
    """
    Converts `string_date` from "Month DD, YYYY" to YYYY-MM-DD for formatting consistency.
    If `string_date` does not match this format, an empty string will be returned.
    """
    try:
        date = datetime.strptime(string_date, "%B %d, %Y")
    except ValueError:
        # input doesn't match format, cannot be reformatted, and should be discarded
        return ""
    day, month = date.day, date.month
    month = f"0{month}" if month < 10 else month
    day = f"0{day}" if day < 10 else day
    return f"{date.year}-{month}-{day}"


def soup_from_comment(tag: Tag, only_if_table: bool) -> bs | Tag:
    """
    Returns contents from the first comment within `tag`.
    If `tag` does not include a table and `only_if_table` is `True`, returns `tag`.
    """
    try:
        comment_contents = str_between(tag.decode_contents(), "<!--", "-->").strip()
        if only_if_table and not "<col><col><col>" in comment_contents:
            return tag
        return bs(comment_contents, "lxml")
    except (
        IndexError,  # thrown when indexing split functions in str_between
        ValueError,  # thrown explicitly by str_between
    ):
        return tag


def scrape_player_ids(table: bs | Tag) -> list[str]:
    """Returns player IDs from anchor tags in `table`."""
    player_id_column = []
    for row in table.find_all("a", href=True):
        link = row.get("href", "")
        if "players" not in link:
            continue
        # [11:21] includes the period in ".shtml" so rsplit works if ID is short or has a period
        player_id = link[11:21]
        player_id_column.append(player_id.rsplit(".", maxsplit=1)[0])
    return player_id_column


def convert_innings_notation(innings: str | float) -> float | None:
    """Converts box score notation to correct numerical value so that values sum correctly."""
    # could be np.nan, leave that alone since the column will eventually be converted to floats
    if not isinstance(innings, str):
        innings = str(innings)
    innings = innings.replace(".1", ".333334").replace(".2", ".666667")
    if innings == "":
        return None
    return float(innings)


def convert_numeric_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Converts the numeric columns of `df` to correct dtypes using `pd.to_numeric`."""
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise")
        except (
            ValueError,  # includes a non-convertable value of a compatible type (e.g. "a")
            TypeError,  # includes a value of an incompatible type (e.g. a list)
        ):
            # skip columns which cannot be converted
            pass
    return df


def game_id_to_endpoint(game_id: str) -> str:
    """Converts `game_id` to the associated URL endpoint."""
    is_asg = len(game_id) != 12
    if is_asg:
        endpoint = f"/allstar/{game_id}.shtml"
    else:
        endpoint = f"/boxes/{game_id[:-9]}/{game_id}.shtml"
    return endpoint
