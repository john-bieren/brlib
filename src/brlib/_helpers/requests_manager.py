#!/usr/bin/env python3

"""Defines and instantiates RequestsManager singleton."""

import time

from curl_cffi import Response, requests

from ..options import options, write
from .singleton import Singleton


class RequestsManager(Singleton):
    """
    Manages web requests while observing Baseball Reference's
    [rate limit](https://www.sports-reference.com/429.html).
    """
    def __init__(self) -> None:
        self._last_request = 0
        self._session = requests.Session()

    def get_page(self, endpoint: str) -> Response:
        """
        Loads a Baseball Reference page.
        `endpoint` is the page's URL excluding the prefix "https://www.baseball-reference.com".
        A request will not be made until `options.request_buffer` seconds have passed since
        the previous request was made.
        """
        url = "https://www.baseball-reference.com" + endpoint
        retries = 0

        while True:
            self.pause() # won't do anything if it has been long enough
            self._last_request = time.perf_counter_ns()
            try:
                page = self._session.get(url, timeout=options.timeout_limit)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as exc:
                if retries >= options.max_retries:
                    raise ConnectionError("could not load page") from exc
                write("could not load page, retrying")
                retries += 1
                continue
            break

        if not page.ok:
            if page.status_code == 429:
                raise ConnectionRefusedError("429 error: rate limit exceeded, Baseball Reference access temporarily blocked")
            if page.status_code == 404:
                raise ConnectionError(f"404 error: {url} does not exist")
            raise ConnectionError(f"{url} returned {page.status_code} status code")
        return page

    def pause(self) -> None:
        """
        Pauses execution until `options.request_buffer` seconds have passed since
        the previous request was made.
        """
        ns_delta = (time.perf_counter_ns()-self._last_request) / 1e9
        pause_length = max(options.request_buffer - ns_delta, 0)
        time.sleep(pause_length)

req_man = RequestsManager()
