"""Tests the attributes and methods of the `Options` singleton."""

import json

from brlib import options


def test_preferences() -> None:
    """Tests the behavior of `Options` with respect to preferences."""
    options._preferences.clear()  # overwrite user preferences for controlled environment
    # save user preferences to replace after testing
    with options._preferences_file.open("r", encoding="UTF-8") as file:
        user_preferences = json.load(file)

    try:
        # test set_preference
        options.set_preference("dev_alerts", True)
        options.set_preference("timeout_limit", 60)
        options.set_preference("pb_format", "{bar}")
        options.set_preference("pb_format", None)
        options.set_preference("print_pages", 47)
        options.set_preference("max_retries", 2.1)
        options.set_preference("not an option", False)
        options.set_preference("quiet", None)
        assert options._preferences == {"dev_alerts": True, "timeout_limit": 60}
        assert options.dev_alerts == True
        assert options.timeout_limit == 60

        # test clear_preferences
        options.clear_preferences()
        assert options._preferences == {}
        with options._preferences_file.open("r", encoding="UTF-8") as file:
            assert json.load(file) == {}

        # test preferences file creation
        options._preferences_file.unlink()
        options._load_preferences()  # should create preferences file if it doesn't exist
        with options._preferences_file.open("r", encoding="UTF-8") as file:
            assert json.load(file) == {}

        # test _load_preferences
        mock_preferences_file = {
            "pb_disable": True,
            "pb_color": "#ffffff",
            "quiet": 0,
            "request_buffer": 2,
            "not a real option": "idk",
            123: "keys must be strings",
        }
        with options._preferences_file.open("w", encoding="UTF-8") as file:
            json.dump(mock_preferences_file, file)
        options._load_preferences()
        assert options._preferences == {"pb_disable": True, "pb_color": "#ffffff"}
        assert options.pb_disable == True
        assert options.pb_color == "#ffffff"
    finally:
        # restore user preferences
        with options._preferences_file.open("w", encoding="UTF-8") as file:
            json.dump(user_preferences, file)


def test_bool_options() -> None:
    """Tests the getters and setters of the boolean options."""
    options._preferences.clear()  # overwrite user preferences for controlled environment
    bool_options = [opt for opt, val in options._defaults.items() if type(val) == bool]
    for option in bool_options:
        set_val = options._changes.get(option, None)
        default_val = options._defaults[option]
        # test that value starts with default
        assert getattr(options, option) == default_val
        # test that value can be set
        setattr(options, option, not default_val)
        assert getattr(options, option) != default_val
        # test typechecking
        setattr(options, option, "boolean")
        assert getattr(options, option) != default_val
        # test that value can be reset to default with None
        setattr(options, option, None)
        assert getattr(options, option) == default_val
        # restore value set at runtime, if applicable
        if set_val is not None:
            setattr(options, option, set_val)


def test_numeric_options() -> None:
    """Tests the getters and setters of the numeric options."""
    options._preferences.clear()  # overwrite user preferences for controlled environment
    numeric_options = [opt for opt, val in options._defaults.items() if type(val) in (int, float)]
    for option in numeric_options:
        set_val = options._changes.get(option, None)
        default_val = options._defaults[option]
        test_val = 3.141592565 if type(default_val) == float else 1247
        # test that value starts with default
        assert getattr(options, option) == default_val
        # test that value can be set
        setattr(options, option, test_val)
        assert getattr(options, option) == test_val
        # test validation that assigned values are positive
        setattr(options, option, -1 * test_val)
        assert getattr(options, option) == test_val
        # test typechecking
        setattr(options, option, "numeric")
        assert getattr(options, option) == test_val
        # test that value can be reset to default with None
        setattr(options, option, None)
        assert getattr(options, option) == default_val
        # restore value set at runtime, if applicable
        if set_val is not None:
            setattr(options, option, set_val)


def test_str_options() -> None:
    """Tests the getters and setters of the string options."""
    options._preferences.clear()  # overwrite user preferences for controlled environment
    str_options = [opt for opt, val in options._defaults.items() if type(val) == str]
    for option in str_options:
        set_val = options._changes.get(option, None)
        default_val = options._defaults[option]
        # test that value starts with default
        assert getattr(options, option) == default_val
        # test that value can be set
        setattr(options, option, "string")
        assert getattr(options, option) == "string"
        # test typechecking
        setattr(options, option, -1)
        assert getattr(options, option) == "string"
        # test that value can be reset to default with None
        setattr(options, option, None)
        assert getattr(options, option) == default_val
        # restore value set at runtime, if applicable
        if set_val is not None:
            setattr(options, option, set_val)
