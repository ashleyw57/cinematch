"""Movie search, discovery, and detail retrieval logic."""

from __future__ import annotations

from cinematch import tmdb_client
from cinematch.models import GENRE_MAP, MOOD_TO_GENRES, Movie, MovieDetail


def search(query: str, page: int = 1) -> list[Movie]:
    """Search for movies by title keyword.

    Args:
        query: Free-text search string.
        page: Results page (1-indexed).

    Returns:
        List of matching :class:`Movie` objects.
    """
    data = tmdb_client.get("/search/movie", {"query": query, "page": page})
    return [Movie(**r) for r in data.get("results", [])]


def get_detail(movie_id: int) -> MovieDetail:
    """Fetch full details for a single movie.

    Args:
        movie_id: TMDB numeric movie ID.

    Returns:
        :class:`MovieDetail` with extended metadata.
    """
    data = tmdb_client.get(f"/movie/{movie_id}")
    return MovieDetail(**data)


def get_recommendations(movie_id: int, page: int = 1) -> list[Movie]:
    """Get TMDB recommendations based on a seed movie.

    Args:
        movie_id: Seed TMDB movie ID.
        page: Results page.

    Returns:
        List of recommended :class:`Movie` objects.
    """
    data = tmdb_client.get(f"/movie/{movie_id}/recommendations", {"page": page})
    return [Movie(**r) for r in data.get("results", [])]


def discover_by_mood(mood: str, page: int = 1) -> list[Movie]:
    """Find movies that match a given mood keyword.

    Supported moods: happy, sad, excited, scared, romantic, thoughtful,
    adventurous, chill.

    Args:
        mood: One of the supported mood strings (case-insensitive).
        page: Results page.

    Returns:
        List of :class:`Movie` objects matching the mood.

    Raises:
        ValueError: If the mood is not recognised.
    """
    mood = mood.lower()
    genre_ids = MOOD_TO_GENRES.get(mood)
    if genre_ids is None:
        valid = ", ".join(sorted(MOOD_TO_GENRES))
        raise ValueError(f"Unknown mood '{mood}'. Valid moods: {valid}")
    genre_str = "|".join(str(g) for g in genre_ids)
    data = tmdb_client.get(
        "/discover/movie",
        {"with_genres": genre_str, "sort_by": "popularity.desc", "page": page},
    )
    return [Movie(**r) for r in data.get("results", [])]


def discover_by_genre(genre: str, page: int = 1) -> list[Movie]:
    """Find movies by genre name.

    Args:
        genre: Genre name (case-insensitive), e.g. ``"comedy"``.
        page: Results page.

    Returns:
        List of :class:`Movie` objects in the genre.

    Raises:
        ValueError: If the genre name is not recognised.
    """
    genre_lower = genre.lower()
    genre_id = next(
        (gid for gid, name in GENRE_MAP.items() if name.lower() == genre_lower),
        None,
    )
    if genre_id is None:
        valid = ", ".join(sorted(GENRE_MAP.values()))
        raise ValueError(f"Unknown genre '{genre}'. Valid genres: {valid}")
    data = tmdb_client.get(
        "/discover/movie",
        {"with_genres": genre_id, "sort_by": "popularity.desc", "page": page},
    )
    return [Movie(**r) for r in data.get("results", [])]


def discover_by_decade(decade: int, page: int = 1) -> list[Movie]:
    """Find popular movies from a given decade.

    Args:
        decade: Start year of the decade, e.g. ``1990`` for the 90s.
        page: Results page.

    Returns:
        List of :class:`Movie` objects from that decade.

    Raises:
        ValueError: If decade is outside 1880–2020.
    """
    if decade < 1880 or decade > 2030 or decade % 10 != 0:
        raise ValueError("decade must be a multiple of 10, e.g. 1990")
    data = tmdb_client.get(
        "/discover/movie",
        {
            "primary_release_date.gte": f"{decade}-01-01",
            "primary_release_date.lte": f"{decade + 9}-12-31",
            "sort_by": "popularity.desc",
            "page": page,
        },
    )
    return [Movie(**r) for r in data.get("results", [])]


def find_hidden_gems(page: int = 1) -> list[Movie]:
    """Find high-quality movies with low mainstream popularity.

    Criteria: vote_average ≥ 7.5, vote_count ≥ 100, popularity < 20.

    Args:
        page: Results page.

    Returns:
        List of hidden-gem :class:`Movie` objects.
    """
    data = tmdb_client.get(
        "/discover/movie",
        {
            "vote_average.gte": 7.5,
            "vote_count.gte": 100,
            "popularity.lte": 20,
            "sort_by": "vote_average.desc",
            "page": page,
        },
    )
    return [Movie(**r) for r in data.get("results", [])]


def trending(time_window: str = "week") -> list[Movie]:
    """Fetch trending movies.

    Args:
        time_window: ``"day"`` or ``"week"``.

    Returns:
        List of trending :class:`Movie` objects.

    Raises:
        ValueError: If time_window is invalid.
    """
    if time_window not in ("day", "week"):
        raise ValueError("time_window must be 'day' or 'week'")
    data = tmdb_client.get(f"/trending/movie/{time_window}")
    return [Movie(**r) for r in data.get("results", [])]


def list_genres() -> dict[int, str]:
    """Return the full genre ID → name mapping.

    Returns:
        Dict mapping genre integer IDs to human-readable names.
    """
    return dict(GENRE_MAP)


def list_moods() -> list[str]:
    """Return the list of supported mood keywords.

    Returns:
        Sorted list of mood strings.
    """
    return sorted(MOOD_TO_GENRES)
