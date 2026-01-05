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
        for file in CACHE_DIR.iterdir():
            file.unlink()

    def clear_preferences(self) -> None:
        self._preferences.clear()
        self._preferences_file.write_text(json.dumps({}), encoding="UTF-8")

    @property
    def add_no_hitters(self) -> bool:
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
