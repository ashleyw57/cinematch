"""Tests for cinematch.movies business logic."""

from __future__ import annotations

import pytest

from cinematch import movies
from cinematch.models import Movie, MovieDetail


def test_search_returns_movies(mock_tmdb_search):
    results = movies.search("Fight Club")
    assert len(results) == 1
    assert isinstance(results[0], Movie)
    assert results[0].title == "Fight Club"
    assert results[0].id == 550


def test_search_passes_page(mock_tmdb_search):
    movies.search("Fight Club", page=3)
    call_kwargs = mock_tmdb_search.call_args
    assert call_kwargs[0][1]["page"] == 3


def test_get_detail_returns_movie_detail(mock_tmdb_detail):
    detail = movies.get_detail(550)
    assert isinstance(detail, MovieDetail)
    assert detail.imdb_id == "tt0137523"
    assert detail.runtime == 139
    assert "Drama" in detail.genre_names


def test_movie_poster_url():
    m = Movie(
        id=1,
        title="Test",
        poster_path="/abc.jpg",
        vote_average=7.0,
        vote_count=100,
        popularity=10.0,
    )
    assert m.poster_url == "https://image.tmdb.org/t/p/w500/abc.jpg"


def test_movie_no_poster_url():
    m = Movie(id=1, title="Test", vote_average=7.0, vote_count=100, popularity=10.0)
    assert m.poster_url is None


def test_movie_year():
    m = Movie(
        id=1,
        title="Test",
        release_date="1999-10-15",
        vote_average=7.0,
        vote_count=100,
        popularity=10.0,
    )
    assert m.year == "1999"


def test_discover_by_mood_valid(mock_tmdb_discover):
    results = movies.discover_by_mood("happy")
    assert isinstance(results, list)
    assert all(isinstance(r, Movie) for r in results)


def test_discover_by_mood_invalid():
    with pytest.raises(ValueError, match="Unknown mood"):
        movies.discover_by_mood("grumpy")


def test_discover_by_genre_valid(mock_tmdb_discover):
    results = movies.discover_by_genre("comedy")
    assert isinstance(results, list)


def test_discover_by_genre_invalid():
    with pytest.raises(ValueError, match="Unknown genre"):
        movies.discover_by_genre("Teletubbies")


def test_discover_by_decade_valid(mock_tmdb_discover):
    results = movies.discover_by_decade(1990)
    assert isinstance(results, list)


def test_discover_by_decade_invalid():
    with pytest.raises(ValueError):
        movies.discover_by_decade(1995)  # not a round decade


def test_find_hidden_gems(mock_tmdb_discover):
    results = movies.find_hidden_gems()
    assert isinstance(results, list)


def test_trending_week(mock_tmdb_discover):
    results = movies.trending("week")
    assert isinstance(results, list)


def test_trending_day(mock_tmdb_discover):
    results = movies.trending("day")
    assert isinstance(results, list)


def test_trending_invalid():
    with pytest.raises(ValueError):
        movies.trending("month")


def test_list_genres_returns_dict():
    genres = movies.list_genres()
    assert isinstance(genres, dict)
    assert 35 in genres
    assert genres[35] == "Comedy"


def test_list_moods_returns_list():
    moods = movies.list_moods()
    assert "happy" in moods
    assert "sad" in moods
    assert sorted(moods) == moods  # should be sorted


def test_get_recommendations(mock_tmdb_discover):
    results = movies.get_recommendations(550)
    assert isinstance(results, list)
