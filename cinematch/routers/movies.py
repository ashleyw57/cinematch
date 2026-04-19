"""HTTP router for movie endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from cinematch import movies as movie_lib
from cinematch.models import Movie, MovieDetail

router = APIRouter()


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


def _bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/search", response_model=list[Movie])
def search_movies(
    q: str = Query(..., description="Search query string"),
    page: int = Query(1, ge=1, description="Page number"),
) -> list[Movie]:
    """Search for movies by title keyword."""
    return movie_lib.search(q, page=page)


@router.get("/trending", response_model=list[Movie])
def trending_movies(
    time_window: str = Query("week", pattern="^(day|week)$"),
) -> list[Movie]:
    """Get currently trending movies (day or week)."""
    try:
        return movie_lib.trending(time_window)
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/hidden-gems", response_model=list[Movie])
def hidden_gems(
    page: int = Query(1, ge=1),
) -> list[Movie]:
    """Discover high-rated, under-the-radar movies."""
    return movie_lib.find_hidden_gems(page=page)


@router.get("/genres", response_model=dict[int, str])
def list_genres() -> dict[int, str]:
    """List all available genre IDs and names."""
    return movie_lib.list_genres()


@router.get("/moods", response_model=list[str])
def list_moods() -> list[str]:
    """List all supported mood keywords."""
    return movie_lib.list_moods()


@router.get("/discover/mood", response_model=list[Movie])
def discover_by_mood(
    mood: str = Query(..., description="Mood keyword, e.g. 'happy'"),
    page: int = Query(1, ge=1),
) -> list[Movie]:
    """Find movies matching a mood (happy, sad, excited, etc.)."""
    try:
        return movie_lib.discover_by_mood(mood, page=page)
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/discover/genre", response_model=list[Movie])
def discover_by_genre(
    genre: str = Query(..., description="Genre name, e.g. 'Comedy'"),
    page: int = Query(1, ge=1),
) -> list[Movie]:
    """Find movies by genre name."""
    try:
        return movie_lib.discover_by_genre(genre, page=page)
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/discover/decade", response_model=list[Movie])
def discover_by_decade(
    decade: int = Query(..., description="Decade start year, e.g. 1990"),
    page: int = Query(1, ge=1),
) -> list[Movie]:
    """Find popular movies from a specific decade."""
    try:
        return movie_lib.discover_by_decade(decade, page=page)
    except ValueError as e:
        raise _bad_request(e) from e


@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(movie_id: int) -> MovieDetail:
    """Get full details for a specific movie by its TMDB ID."""
    try:
        return movie_lib.get_detail(movie_id)
    except Exception as e:
        raise _not_found(e) from e


@router.get("/{movie_id}/recommendations", response_model=list[Movie])
def get_recommendations(
    movie_id: int,
    page: int = Query(1, ge=1),
) -> list[Movie]:
    """Get movie recommendations based on a seed movie."""
    try:
        return movie_lib.get_recommendations(movie_id, page=page)
    except Exception as e:
        raise _not_found(e) from e
