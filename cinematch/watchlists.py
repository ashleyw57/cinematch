"""Watchlist management: create, read, update, delete watchlists on disk."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from cinematch.models import Watchlist, WatchlistItem

_DEFAULT_DIR = Path.home() / ".cinematch" / "watchlists"


def _dir(storage_dir: Path | None) -> Path:
    d = storage_dir or _DEFAULT_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _path(name: str, storage_dir: Path | None) -> Path:
    return _dir(storage_dir) / f"{name}.json"


def _load(name: str, storage_dir: Path | None) -> Watchlist:
    p = _path(name, storage_dir)
    if not p.exists():
        raise KeyError(f"Watchlist '{name}' does not exist.")
    return Watchlist.model_validate_json(p.read_text())


def _save(wl: Watchlist, storage_dir: Path | None) -> None:
    p = _path(wl.name, storage_dir)
    p.write_text(wl.model_dump_json(indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create(name: str, storage_dir: Path | None = None) -> Watchlist:
    """Create a new empty watchlist.

    Args:
        name: Unique watchlist name (used as the filename).
        storage_dir: Override storage directory (used in tests).

    Returns:
        The newly created :class:`Watchlist`.

    Raises:
        FileExistsError: If a watchlist with that name already exists.
    """
    p = _path(name, storage_dir)
    if p.exists():
        raise FileExistsError(f"Watchlist '{name}' already exists.")
    wl = Watchlist(name=name)
    _save(wl, storage_dir)
    return wl


def get(name: str, storage_dir: Path | None = None) -> Watchlist:
    """Load an existing watchlist by name.

    Args:
        name: Watchlist name.
        storage_dir: Override storage directory.

    Returns:
        The :class:`Watchlist`.

    Raises:
        KeyError: If the watchlist does not exist.
    """
    return _load(name, storage_dir)


def list_all(storage_dir: Path | None = None) -> list[str]:
    """Return the names of all saved watchlists.

    Args:
        storage_dir: Override storage directory.

    Returns:
        Sorted list of watchlist names.
    """
    return sorted(p.stem for p in _dir(storage_dir).glob("*.json"))


def delete(name: str, storage_dir: Path | None = None) -> None:
    """Delete a watchlist.

    Args:
        name: Watchlist name to delete.
        storage_dir: Override storage directory.

    Raises:
        KeyError: If the watchlist does not exist.
    """
    p = _path(name, storage_dir)
    if not p.exists():
        raise KeyError(f"Watchlist '{name}' does not exist.")
    p.unlink()


def add_movie(
    name: str,
    movie_id: int,
    title: str,
    notes: str = "",
    storage_dir: Path | None = None,
) -> Watchlist:
    """Add a movie to a watchlist.

    Args:
        name: Watchlist name.
        movie_id: TMDB movie ID.
        title: Movie title (stored for display without extra API calls).
        notes: Optional user notes.
        storage_dir: Override storage directory.

    Returns:
        Updated :class:`Watchlist`.

    Raises:
        KeyError: If the watchlist does not exist.
    """
    wl = _load(name, storage_dir)
    item = WatchlistItem(
        movie_id=movie_id,
        title=title,
        added_at=datetime.now(UTC).isoformat(),
        notes=notes,
    )
    wl.add(item)
    _save(wl, storage_dir)
    return wl


def remove_movie(
    name: str, movie_id: int, storage_dir: Path | None = None
) -> Watchlist:
    """Remove a movie from a watchlist.

    Args:
        name: Watchlist name.
        movie_id: TMDB movie ID to remove.
        storage_dir: Override storage directory.

    Returns:
        Updated :class:`Watchlist`.

    Raises:
        KeyError: If the watchlist or movie does not exist.
    """
    wl = _load(name, storage_dir)
    removed = wl.remove(movie_id)
    if not removed:
        raise KeyError(f"Movie {movie_id} not found in watchlist '{name}'.")
    _save(wl, storage_dir)
    return wl


def mark_watched(
    name: str, movie_id: int, storage_dir: Path | None = None
) -> Watchlist:
    """Mark a movie as watched in a watchlist.

    Args:
        name: Watchlist name.
        movie_id: TMDB movie ID to mark.
        storage_dir: Override storage directory.

    Returns:
        Updated :class:`Watchlist`.

    Raises:
        KeyError: If the watchlist or movie does not exist.
    """
    wl = _load(name, storage_dir)
    found = wl.mark_watched(movie_id)
    if not found:
        raise KeyError(f"Movie {movie_id} not found in watchlist '{name}'.")
    _save(wl, storage_dir)
    return wl
