#!/usr/bin/env python3

"""
Refreshes the contents of an adjacent "wiki" directory, presumably a clone of brlib's GitHub
wiki repo. Copies all public member docstrings into corresponding Markdown files, and refreshes
the column lists in DataFrames-Info.md. All changes should be manually reviewed.
"""

import inspect
from pathlib import Path

import brlib
from brlib._helpers.constants import (
    ALL_PLAYERS_COLS,
    GAME_BATTING_COLS,
    GAME_FIELDING_COLS,
    GAME_INFO_COLS,
    GAME_PITCHING_COLS,
    GAME_TEAM_INFO_COLS,
    GAME_UMP_INFO_COLS,
    PLAYER_BATTING_COLS,
    PLAYER_BLING_COLS,
    PLAYER_FIELDING_COLS,
    PLAYER_INFO_COLS,
    PLAYER_PITCHING_COLS,
    PLAYER_SALARIES_COLS,
    RECORDS_COLS,
    TEAM_BATTING_COLS,
    TEAM_FIELDING_COLS,
    TEAM_INFO_COLS,
    TEAM_PITCHING_COLS,
)
from brlib._helpers.utils import str_between


def main() -> None:
    """
    Refreshes the contents of an adjacent "wiki" directory, presumably a clone of brlib's GitHub
    wiki repo. Copies all public member docstrings into corresponding Markdown files, and refreshes
    the column lists in DataFrames-Info.md. All changes should be manually reviewed.
    """
    wiki_dir = Path(__file__).parent.parent / "wiki"

    print("Refreshing public member wiki files")
    refresh_files(wiki_dir)

    print("Refreshing column lists in DataFrames-info.md")
    refresh_cols(wiki_dir)


def refresh_files(wiki_dir: Path) -> None:
    """Copies all public member docstrings into corresponding Markdown files."""
    public_members = {
        name: mem for name, mem in inspect.getmembers(brlib) if not name.startswith("_")
    }
    for member_name, member in public_members.items():
        if inspect.ismodule(member):
            continue
        file_path = wiki_dir / f"{member_name}.md"
        file_path.write_text(clean_docstring(member.__doc__), encoding="UTF-8")

        # for classes or variables which are the instantiation of a singleton class
        if not inspect.isfunction(member):
            # create files for each of the class's public methods
            methods = inspect.getmembers(member, predicate=is_function_or_method)
            public_methods = {name: mem for name, mem in methods if not name.startswith("_")}
            for method_name, method in public_methods.items():
                file_path = wiki_dir / f"{member_name}.{method_name}.md"
                file_path.write_text(clean_docstring(method.__doc__), encoding="UTF-8")


def clean_docstring(docstring: str) -> str:
    """Reformat whitespace in `docstring`."""
    # remove leading newline
    if docstring.startswith("\n"):
        docstring = docstring[1:]
    return docstring


def is_function_or_method(member: object) -> bool:
    """
    Checks whether `inspect.isfunction` or `inspect.ismethod` is `True`. `isfunction` finds methods
    if `member` is a class, and `ismethod` finds methods if `member` is a class instance.
    """
    return inspect.isfunction(member) or inspect.ismethod(member)


def refresh_cols(wiki_dir: Path) -> None:
    """Refreshes the column lists in DataFrames-Info.md."""
    df_info_file = wiki_dir / "DataFrames-Info.md"
    # the current column lists, in the same order as DataFrames-Info.md
    cols_lists = [
        ALL_PLAYERS_COLS,
        RECORDS_COLS,
        GAME_INFO_COLS,
        GAME_BATTING_COLS,
        GAME_PITCHING_COLS,
        GAME_FIELDING_COLS,
        GAME_TEAM_INFO_COLS,
        GAME_UMP_INFO_COLS,
        PLAYER_INFO_COLS,
        PLAYER_BLING_COLS,
        PLAYER_BATTING_COLS,
        PLAYER_PITCHING_COLS,
        PLAYER_FIELDING_COLS,
        PLAYER_SALARIES_COLS,
        TEAM_INFO_COLS,
        TEAM_BATTING_COLS,
        TEAM_PITCHING_COLS,
        TEAM_FIELDING_COLS,
    ]

    # first pass: gather the line(s) for each column (including the name and any additional notes)
    col_lines = {}
    df_name = current_col_name = current_col_lines = ""
    for line in df_info_file.read_text(encoding="UTF-8").splitlines():
        # start of a new DataFrame
        if line.startswith("###"):
            # previous column's lines are complete and must be recorded
            if current_col_lines != "":
                col_lines[f"{df_name}::{current_col_name}"] = current_col_lines
            df_name = line[4:].replace("`", "").split(" and", maxsplit=1)[0]
            current_col_lines = ""
        # start of a new column
        elif line.startswith("* `"):
            # previous column's lines are complete and must be recorded
            if current_col_lines != "":
                col_lines[f"{df_name}::{current_col_name}"] = current_col_lines
            current_col_name = str_between(line, "`", "`")
            current_col_lines = line
        # additional note about a column
        elif line.startswith(" "):
            current_col_lines += f"\n{line}"

    # second pass: refresh column lists (including info) using the current columns in constants.py
    file_lines = []
    df_cols_written = False
    df_name = ""
    i = -1
    for line in df_info_file.read_text(encoding="UTF-8").splitlines():
        # start of a new DataFrame
        if line.startswith("###"):
            file_lines.append(line)
            df_name = line[4:].replace("`", "").split(" and", maxsplit=1)[0]
            df_cols_written = False
            i += 1
        # start of column list
        elif line.startswith("* `"):
            if df_cols_written:
                # all of a DataFrame's columns are written at once, so skip to the next DataFrame
                continue
            for col_name in cols_lists[i]:
                col_info = col_lines.get(f"{df_name}::{col_name}", "")
                if col_info != "":
                    file_lines.append(col_info)
                # if the column is new (or renamed, in which case info must be manually restored)
                else:
                    file_lines.append(f"* `{col_name}`")
            df_cols_written = True
        # skip column notes, as they have already been added
        elif line.startswith("    *"):
            continue
        # pass all other lines through
        else:
            file_lines.append(line)
    df_info_file.write_text("\n".join(file_lines) + "\n", encoding="UTF-8")


if __name__ == "__main__":
    main()
