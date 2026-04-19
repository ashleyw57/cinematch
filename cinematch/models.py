"""Pydantic models for CineMatch domain objects."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: int
    title: str
    overview: str = ""
    release_date: str = ""
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    genre_ids: list[int] = Field(default_factory=list)
    poster_path: str | None = None

    @property
    def poster_url(self) -> str | None:
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def year(self) -> str:
        return self.release_date[:4] if self.release_date else "Unknown"


class MovieDetail(Movie):
    genres: list[dict] = Field(default_factory=list)
    runtime: int | None = None
    tagline: str = ""
    budget: int = 0
    revenue: int = 0
    homepage: str | None = None
    imdb_id: str | None = None

    @property
    def genre_names(self) -> list[str]:
        return [g["name"] for g in self.genres]


class WatchlistItem(BaseModel):
    movie_id: int
    title: str
    added_at: str  # ISO 8601 timestamp
    watched: bool = False
    notes: str = ""


class Watchlist(BaseModel):
    name: str
    items: list[WatchlistItem] = Field(default_factory=list)

    def add(self, item: WatchlistItem) -> None:
        if not any(i.movie_id == item.movie_id for i in self.items):
            self.items.append(item)

    def remove(self, movie_id: int) -> bool:
        before = len(self.items)
        self.items = [i for i in self.items if i.movie_id != movie_id]
        return len(self.items) < before

    def mark_watched(self, movie_id: int) -> bool:
        for item in self.items:
            if item.movie_id == movie_id:
                item.watched = True
                return True
        return False


# TMDB genre ID → name mapping (static, avoids extra API call)
GENRE_MAP: dict[int, str] = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

MOOD_TO_GENRES: dict[str, list[int]] = {
    "happy": [35, 10751, 16],
    "sad": [18, 10749],
    "excited": [28, 12, 878],
    "scared": [27, 9648, 53],
    "romantic": [10749, 18],
    "thoughtful": [18, 99, 36],
    "adventurous": [12, 28, 14],
    "chill": [35, 16, 10749],
}
