"""Shared pytest fixtures for CineMatch tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from cinematch.app import app

# ---------------------------------------------------------------------------
# Sample TMDB API payloads (trimmed to fields our models care about)
# ---------------------------------------------------------------------------

MOVIE_PAYLOAD = {
    "id": 550,
    "title": "Fight Club",
    "overview": "A ticking-time-bomb insomniac...",
    "release_date": "1999-10-15",
    "vote_average": 8.4,
    "vote_count": 26000,
    "popularity": 61.4,
    "genre_ids": [18, 53],
    "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
}

DETAIL_PAYLOAD = {
    **MOVIE_PAYLOAD,
    "genres": [{"id": 18, "name": "Drama"}, {"id": 53, "name": "Thriller"}],
    "runtime": 139,
    "tagline": "Mischief. Mayhem. Soap.",
    "budget": 63000000,
    "revenue": 101200000,
    "homepage": None,
    "imdb_id": "tt0137523",
}

SEARCH_RESPONSE = {"results": [MOVIE_PAYLOAD], "total_pages": 1, "page": 1}
DISCOVER_RESPONSE = {"results": [MOVIE_PAYLOAD], "total_pages": 1, "page": 1}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """Return a FastAPI TestClient (no real HTTP calls made)."""
    return TestClient(app)


@pytest.fixture()
def tmp_watchlist_dir(tmp_path: Path) -> Path:
    """Return a temp directory for watchlist storage."""
    return tmp_path / "watchlists"


@pytest.fixture()
def mock_tmdb_search():
    """Patch tmdb_client.get to return a search response."""
    with patch("cinematch.tmdb_client.get", return_value=SEARCH_RESPONSE) as m:
        yield m


@pytest.fixture()
def mock_tmdb_detail():
    """Patch tmdb_client.get to return a movie detail response."""
    with patch("cinematch.tmdb_client.get", return_value=DETAIL_PAYLOAD) as m:
        yield m


@pytest.fixture()
def mock_tmdb_discover():
    """Patch tmdb_client.get to return a discover response."""
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE) as m:
        yield m
