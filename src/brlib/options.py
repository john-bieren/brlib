#!/usr/bin/env python3

"""Defines and instantiates Options singleton."""

import json
from collections import ChainMap
from typing import Any

from tqdm import tqdm

from ._helpers.constants import CACHE_DIR, CONFIG_DIR
from ._helpers.singleton import Singleton
from ._helpers.utils import is_type


class Options(Singleton):
    """
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

        The format of the progress bar. The value is passed to the tqdm `bar_format` argument. For more, read the tqdm [docs](https://tqdm.github.io/docs/tqdm).

    * `pb_color`, default `"#cccccc"`

        The color of the progress bar. The value is passed to the tqdm `colour` argument. For more, read the tqdm [docs](https://tqdm.github.io/docs/tqdm).

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
    >>> br.options.pb_disable
    True
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
    def __init__(self) -> None:
        self._defaults = {
            "add_no_hitters": False,
            "request_buffer": 2.015,
            "timeout_limit": 10,
            "max_retries": 2,
            "pb_format": "{percentage:3.2f}%|{bar}{r_bar}",
            "pb_color": "#cccccc",
            "pb_disable": False,
            "print_pages": False,
            "dev_alerts": False,
            "quiet": False
        }
        self._preferences_file = CONFIG_DIR / "preferences_v1.json"
        self._changes, self._preferences = ({} for _ in range(2))
        self._settings = ChainMap(self._changes, self._preferences, self._defaults)
        self._load_preferences()

    def _load_preferences(self) -> None:
        """Validates and loads preferences.json contents into `self._preferences`."""
        if not self._preferences_file.exists():
            self._preferences_file.write_text(json.dumps({}), encoding="UTF-8")
            return

        self._preferences.update(json.loads(self._preferences_file.read_bytes()))
        if not is_type(self._preferences, dict[str, Any]):
            print(f"ignoring preferences: preferences.json keys must have type {str}")

        for option, value in self._preferences.items():
            if option not in self._defaults:
                print(f'unknown option "{option}" listed in preferences.json')
                del self._preferences[option]
                continue

            if not isinstance(value, type(self._defaults[option])):
                print(f"{option} preference in preferences.json must have type {type(self._defaults[option])}")
                del self._preferences[option]

    def set_preference(self, option: str, value: Any) -> None:
        """
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
        if option not in self._defaults:
            if not self.quiet:
                print(f'unknown option "{option}"')
            return

        if value is not None:
            if not isinstance(value, type(self._defaults[option])):
                if not self.quiet:
                    print(f"{option} preference must have type {type(self._defaults[option])}")
                return
            self._preferences[option] = value
        else:
            # reset to default
            if option not in self._preferences:
                if not self.quiet:
                    print(f'no preference set for {option}')
                return
            del self._preferences[option]

        self._preferences_file.write_text(json.dumps(self._preferences), encoding="UTF-8")

    @staticmethod
    def clear_cache() -> None:
        """
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
        for file in CACHE_DIR.iterdir():
            file.unlink()

    def clear_preferences(self) -> None:
        """
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
        self._preferences.clear()
        self._preferences_file.write_text(json.dumps({}), encoding="UTF-8")

    @property
    def add_no_hitters(self) -> bool:
        """
        Default value for `add_no_hitters` arguments when initializing
        `Game`, `Player`, and `Team` objects.
        """
        return self._settings["add_no_hitters"]

    @add_no_hitters.setter
    def add_no_hitters(self, value: bool | None) -> None:
        if value is None:
            self._changes.pop("add_no_hitters", None)
            return
        if not isinstance(value, bool):
            if not self.quiet:
                print(f"add_no_hitters preference must have type {bool}")
            return
        self._changes["add_no_hitters"] = value

    @property
    def request_buffer(self) -> float:
        """
        Buffer, in seconds, between requests.
        Necessary to obey Baseball Reference's [rate limit](https://www.sports-reference.com/429.html).
        """
        return self._settings["request_buffer"]

    @request_buffer.setter
    def request_buffer(self, value: float | None) -> None:
        if value is None:
            self._changes.pop("request_buffer", None)
            return
        if value < 0:
            if not self.quiet:
                print("cannot set request_buffer to negative value")
            return
        if not isinstance(value, float):
            if not self.quiet:
                print(f"request_buffer preference must have type {float}")
            return
        self._changes["request_buffer"] = value

    @property
    def timeout_limit(self) -> int:
        """Timeout parameter for requests."""
        return self._settings["timeout_limit"]

    @timeout_limit.setter
    def timeout_limit(self, value: int | None) -> None:
        if value is None:
            self._changes.pop("timeout_limit", None)
            return
        if value < 0:
            if not self.quiet:
                print("cannot set timeout_limit to negative value")
            return
        if not isinstance(value, int):
            if not self.quiet:
                print(f"timeout_limit preference must have type {int}")
            return
        self._changes["timeout_limit"] = value

    @property
    def max_retries(self) -> int:
        """Number of retries to attempt on failed requests."""
        return self._settings["max_retries"]

    @max_retries.setter
    def max_retries(self, value: int | None) -> None:
        if value is None:
            self._changes.pop("max_retries", None)
            return
        if value < 0:
            if not self.quiet:
                print("cannot set max_retries to negative value")
            return
        if not isinstance(value, int):
            if not self.quiet:
                print(f"max_retries preference must have type {int}")
            return
        self._changes["max_retries"] = value

    @property
    def pb_format(self) -> str:
        """
        The format of the progress bar. The value is passed to the tqdm `bar_format` argument.
        For more, read the tqdm [docs](https://tqdm.github.io/docs/tqdm).
        """
        return self._settings["pb_format"]

    @pb_format.setter
    def pb_format(self, value: str | None) -> None:
        if value is None:
            self._changes.pop("pb_format", None)
            return
        if not isinstance(value, str):
            if not self.quiet:
                print(f"pb_format preference must have type {str}")
            return
        self._changes["pb_format"] = value

    @property
    def pb_color(self) -> str:
        """
        The color of the progress bar. The value is passed to the tqdm `colour` argument.
        For more, read the tqdm [docs](https://tqdm.github.io/docs/tqdm).
        """
        return self._settings["pb_color"]

    @pb_color.setter
    def pb_color(self, value: str | None) -> None:
        if value is None:
            self._changes.pop("pb_color", None)
            return
        if not isinstance(value, str):
            if not self.quiet:
                print(f"pb_color preference must have type {str}")
            return
        self._changes["pb_color"] = value

    @property
    def pb_disable(self) -> bool:
        """Whether to disable the progress bar."""
        return self._settings["pb_disable"]

    @pb_disable.setter
    def pb_disable(self, value: bool | None) -> None:
        if value is None:
            self._changes.pop("pb_disable", None)
            return
        if not isinstance(value, bool):
            if not self.quiet:
                print(f"pb_disable preference must have type {bool}")
            return
        self._changes["pb_disable"] = value

    @property
    def print_pages(self) -> bool:
        """Whether to print descriptions of visited pages."""
        return self._settings["print_pages"]

    @print_pages.setter
    def print_pages(self, value: bool | None) -> None:
        if value is None:
            self._changes.pop("print_pages", None)
            return
        if not isinstance(value, bool):
            if not self.quiet:
                print(f"print_pages preference must have type {bool}")
            return
        self._changes["print_pages"] = value

    @property
    def dev_alerts(self) -> bool:
        """Whether to print alerts meant for brlib developers."""
        return self._settings["dev_alerts"]

    @dev_alerts.setter
    def dev_alerts(self, value: bool | None) -> None:
        if value is None:
            self._changes.pop("dev_alerts", None)
            return
        if not isinstance(value, bool):
            if not self.quiet:
                print(f"dev_alerts preference must have type {bool}")
            return
        self._changes["dev_alerts"] = value

    @property
    def quiet(self) -> bool:
        """Whether to mute most printed messages."""
        return self._settings["quiet"]

    @quiet.setter
    def quiet(self, value: bool | None) -> None:
        if value is None:
            self._changes.pop("quiet", None)
            return
        if not isinstance(value, bool):
            if not self.quiet:
                print(f"quiet preference must have type {bool}")
            return
        self._changes["quiet"] = value

options = Options()

def write(message: str) -> None:
    """Prints something if options.quiet is False."""
    if not options.quiet:
        tqdm.write(message)

def print_page(message: str) -> None:
    """Prints something if options.print_pages is True."""
    if options.print_pages:
        tqdm.write(message)

def dev_alert(message: str) -> None:
    """Prints something if options.dev_alerts is True."""
    if options.dev_alerts:
        tqdm.write(message)
