"""CineMatch – Movie discovery and watchlist library."""

from cinematch import movies, watchlists
from cinematch.models import Movie, MovieDetail, Watchlist, WatchlistItem

__all__ = [
    "movies",
    "watchlists",
    "Movie",
    "MovieDetail",
    "Watchlist",
    "WatchlistItem",
]
