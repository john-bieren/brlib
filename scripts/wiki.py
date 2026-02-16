#!/usr/bin/env python3

"""
Copies public member docstrings into Markdown files in an adjacent "wiki" directory,
presumably a clone of brlib's GitHub wiki repo. This is used to refresh the wiki's contents.
"""

import inspect
from pathlib import Path

import brlib


def main() -> None:
    """
    Copies public member docstrings into Markdown files in an adjacent "wiki" directory,
    presumably a clone of brlib's GitHub wiki repo. This is used to refresh the wiki's contents.
    """
    wiki_dir = Path(__file__).parent.parent / "wiki"
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
    if docstring[0] == "\n":
        docstring = docstring[1:]
    return docstring


def is_function_or_method(member: object) -> bool:
    """
    Checks whether `inspect.isfunction` or `inspect.ismethod` is `True`. `isfunction` finds methods
    if `member` is a class, and `ismethod` finds methods if `member` is a class instance.
    """
    return inspect.isfunction(member) or inspect.ismethod(member)


if __name__ == "__main__":
    main()
