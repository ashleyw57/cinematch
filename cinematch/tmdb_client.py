"""Low-level TMDB API client. Handles auth, rate limiting, and HTTP."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

TMDB_BASE_URL = "https://api.themoviedb.org/3"
_last_request_time: float = 0.0
_MIN_REQUEST_INTERVAL = 0.25  # 4 requests/sec max


def _get_api_key() -> str:
    key = os.environ.get("TMDB_API_KEY", "")
    if not key:
        raise RuntimeError(
            "TMDB_API_KEY environment variable is not set. "
            "Get a free key at https://www.themoviedb.org/settings/api"
        )
    return key


def _throttle() -> None:
    global _last_request_time
    elapsed = time.monotonic() - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def get(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make a GET request to the TMDB API.

    Args:
        endpoint: API path, e.g. ``/movie/550``.
        params: Optional query parameters (``api_key`` is added automatically).

    Returns:
        Parsed JSON response as a dict.

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
        RuntimeError: If ``TMDB_API_KEY`` is not set.
    """
    _throttle()
    merged: dict[str, Any] = {"api_key": _get_api_key(), **(params or {})}
    response = httpx.get(f"{TMDB_BASE_URL}{endpoint}", params=merged, timeout=10)
    response.raise_for_status()
    return response.json()
