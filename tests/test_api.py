"""Integration tests for the CineMatch FastAPI HTTP layer."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from cinematch.app import app
from tests.conftest import (
    DETAIL_PAYLOAD,
    DISCOVER_RESPONSE,
    SEARCH_RESPONSE,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Movies router
# ---------------------------------------------------------------------------


def test_search_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=SEARCH_RESPONSE):
        resp = client.get("/movies/search", params={"q": "Fight Club"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Fight Club"


def test_search_missing_q():
    resp = client.get("/movies/search")
    assert resp.status_code == 422  # validation error


def test_trending_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/trending")
    assert resp.status_code == 200


def test_trending_invalid_window():
    resp = client.get("/movies/trending", params={"time_window": "month"})
    assert resp.status_code == 422


def test_hidden_gems_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/hidden-gems")
    assert resp.status_code == 200


def test_genres_endpoint():
    resp = client.get("/movies/genres")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


def test_moods_endpoint():
    resp = client.get("/movies/moods")
    assert resp.status_code == 200
    data = resp.json()
    assert "happy" in data


def test_discover_mood_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/discover/mood", params={"mood": "happy"})
    assert resp.status_code == 200


def test_discover_mood_invalid():
    resp = client.get("/movies/discover/mood", params={"mood": "grumpy"})
    assert resp.status_code == 400


def test_discover_genre_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/discover/genre", params={"genre": "Comedy"})
    assert resp.status_code == 200


def test_discover_genre_invalid():
    resp = client.get("/movies/discover/genre", params={"genre": "Teletubbies"})
    assert resp.status_code == 400


def test_discover_decade_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/discover/decade", params={"decade": 1990})
    assert resp.status_code == 200


def test_discover_decade_invalid():
    resp = client.get("/movies/discover/decade", params={"decade": 1995})
    assert resp.status_code == 400


def test_movie_detail_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DETAIL_PAYLOAD):
        resp = client.get("/movies/550")
    assert resp.status_code == 200
    assert resp.json()["imdb_id"] == "tt0137523"


def test_recommendations_endpoint():
    with patch("cinematch.tmdb_client.get", return_value=DISCOVER_RESPONSE):
        resp = client.get("/movies/550/recommendations")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Watchlists router
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_watchlist_dir(tmp_path, monkeypatch):
    """Redirect all watchlist storage to a temp directory."""
    wl_dir = tmp_path / "watchlists"
    monkeypatch.setattr("cinematch.watchlists._DEFAULT_DIR", wl_dir)


def test_list_watchlists_empty():
    resp = client.get("/watchlists/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_watchlist_endpoint():
    resp = client.post("/watchlists/", params={"name": "test"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "test"


def test_create_duplicate_watchlist():
    client.post("/watchlists/", params={"name": "test"})
    resp = client.post("/watchlists/", params={"name": "test"})
    assert resp.status_code == 409


def test_get_watchlist_endpoint():
    client.post("/watchlists/", params={"name": "test"})
    resp = client.get("/watchlists/test")
    assert resp.status_code == 200
    assert resp.json()["name"] == "test"


def test_get_nonexistent_watchlist():
    resp = client.get("/watchlists/ghost")
    assert resp.status_code == 404


def test_delete_watchlist_endpoint():
    client.post("/watchlists/", params={"name": "test"})
    resp = client.delete("/watchlists/test")
    assert resp.status_code == 204


def test_add_movie_endpoint():
    client.post("/watchlists/", params={"name": "test"})
    resp = client.post(
        "/watchlists/test/movies",
        json={"movie_id": 550, "title": "Fight Club", "notes": "Great film"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["movie_id"] == 550


def test_remove_movie_endpoint():
    client.post("/watchlists/", params={"name": "test"})
    client.post(
        "/watchlists/test/movies",
        json={"movie_id": 550, "title": "Fight Club"},
    )
    resp = client.delete("/watchlists/test/movies/550")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


def test_mark_watched_endpoint():
    client.post("/watchlists/", params={"name": "test"})
    client.post(
        "/watchlists/test/movies",
        json={"movie_id": 550, "title": "Fight Club"},
    )
    resp = client.patch("/watchlists/test/movies/550/watched")
    assert resp.status_code == 200
    assert resp.json()["items"][0]["watched"] is True
