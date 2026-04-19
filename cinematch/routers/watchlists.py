"""HTTP router for watchlist endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cinematch import watchlists as wl_lib
from cinematch.models import Watchlist

router = APIRouter()


class AddMovieRequest(BaseModel):
    movie_id: int
    title: str
    notes: str = ""


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


def _conflict(exc: Exception) -> HTTPException:
    return HTTPException(status_code=409, detail=str(exc))


@router.get("/", response_model=list[str])
def list_watchlists() -> list[str]:
    """List the names of all saved watchlists."""
    return wl_lib.list_all()


@router.post("/", response_model=Watchlist, status_code=201)
def create_watchlist(name: str) -> Watchlist:
    """Create a new empty watchlist with the given name."""
    try:
        return wl_lib.create(name)
    except FileExistsError as e:
        raise _conflict(e) from e


@router.get("/{name}", response_model=Watchlist)
def get_watchlist(name: str) -> Watchlist:
    """Get a watchlist and its contents by name."""
    try:
        return wl_lib.get(name)
    except KeyError as e:
        raise _not_found(e) from e


@router.delete("/{name}", status_code=204)
def delete_watchlist(name: str) -> None:
    """Delete a watchlist by name."""
    try:
        wl_lib.delete(name)
    except KeyError as e:
        raise _not_found(e) from e


@router.post("/{name}/movies", response_model=Watchlist)
def add_movie_to_watchlist(name: str, body: AddMovieRequest) -> Watchlist:
    """Add a movie to a watchlist."""
    try:
        return wl_lib.add_movie(name, body.movie_id, body.title, body.notes)
    except KeyError as e:
        raise _not_found(e) from e


@router.delete("/{name}/movies/{movie_id}", response_model=Watchlist)
def remove_movie_from_watchlist(name: str, movie_id: int) -> Watchlist:
    """Remove a movie from a watchlist."""
    try:
        return wl_lib.remove_movie(name, movie_id)
    except KeyError as e:
        raise _not_found(e) from e


@router.patch("/{name}/movies/{movie_id}/watched", response_model=Watchlist)
def mark_movie_watched(name: str, movie_id: int) -> Watchlist:
    """Mark a movie in a watchlist as watched."""
    try:
        return wl_lib.mark_watched(name, movie_id)
    except KeyError as e:
        raise _not_found(e) from e
