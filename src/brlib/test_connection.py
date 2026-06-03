"""Defines `test_connection` function."""

from ._helpers.requests_manager import req_mgr
from .options import write


def test_connection() -> bool:
    """
    Indicates whether you can connect to Baseball Reference. Raised exceptions are caught and
    printed.

    ## Parameters

    None

    ## Returns

    bool

    ## Examples

    Ensure that you can connect to Baseball Reference:

    ```
    >>> br.test_connection()
    True
    ```

    Test for 429 errors:

    ```
    >>> br.test_connection()
    ConnectionRefusedError: rate limit exceeded, Baseball Reference access temporarily blocked (429 error)
    False
    ```
    """
    try:
        req_mgr.get_page("")  # load homepage, any problems will result in exceptions
    except Exception as exc:
        exception_type = type(exc).__name__
        write(f"{exception_type}: {exc}")
        return False
    return True
