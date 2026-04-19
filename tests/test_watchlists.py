"""Tests for cinematch.watchlists business logic."""

from __future__ import annotations

import pytest

from cinematch import watchlists


def test_create_watchlist(tmp_watchlist_dir):
    wl = watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    assert wl.name == "mylist"
    assert wl.items == []


def test_create_duplicate_raises(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    with pytest.raises(FileExistsError):
        watchlists.create("mylist", storage_dir=tmp_watchlist_dir)


def test_get_nonexistent_raises(tmp_watchlist_dir):
    with pytest.raises(KeyError):
        watchlists.get("ghost", storage_dir=tmp_watchlist_dir)


def test_list_all(tmp_watchlist_dir):
    watchlists.create("alpha", storage_dir=tmp_watchlist_dir)
    watchlists.create("beta", storage_dir=tmp_watchlist_dir)
    names = watchlists.list_all(storage_dir=tmp_watchlist_dir)
    assert names == ["alpha", "beta"]


def test_delete_watchlist(tmp_watchlist_dir):
    watchlists.create("gone", storage_dir=tmp_watchlist_dir)
    watchlists.delete("gone", storage_dir=tmp_watchlist_dir)
    assert "gone" not in watchlists.list_all(storage_dir=tmp_watchlist_dir)


def test_delete_nonexistent_raises(tmp_watchlist_dir):
    with pytest.raises(KeyError):
        watchlists.delete("nope", storage_dir=tmp_watchlist_dir)


def test_add_movie(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    wl = watchlists.add_movie(
        "mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir
    )
    assert len(wl.items) == 1
    assert wl.items[0].movie_id == 550
    assert wl.items[0].title == "Fight Club"
    assert not wl.items[0].watched


def test_add_movie_duplicate_ignored(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir)
    wl = watchlists.add_movie(
        "mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir
    )
    assert len(wl.items) == 1  # still just one


def test_add_movie_persists(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir)
    reloaded = watchlists.get("mylist", storage_dir=tmp_watchlist_dir)
    assert reloaded.items[0].movie_id == 550


def test_remove_movie(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir)
    wl = watchlists.remove_movie("mylist", 550, storage_dir=tmp_watchlist_dir)
    assert len(wl.items) == 0


def test_remove_nonexistent_movie_raises(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    with pytest.raises(KeyError):
        watchlists.remove_movie("mylist", 9999, storage_dir=tmp_watchlist_dir)


def test_mark_watched(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir)
    wl = watchlists.mark_watched("mylist", 550, storage_dir=tmp_watchlist_dir)
    assert wl.items[0].watched is True


def test_mark_watched_nonexistent_raises(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    with pytest.raises(KeyError):
        watchlists.mark_watched("mylist", 9999, storage_dir=tmp_watchlist_dir)


def test_add_with_notes(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    wl = watchlists.add_movie(
        "mylist", 550, "Fight Club", notes="Classic!", storage_dir=tmp_watchlist_dir
    )
    assert wl.items[0].notes == "Classic!"


def test_multiple_movies(tmp_watchlist_dir):
    watchlists.create("mylist", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 550, "Fight Club", storage_dir=tmp_watchlist_dir)
    watchlists.add_movie("mylist", 680, "Pulp Fiction", storage_dir=tmp_watchlist_dir)
    wl = watchlists.get("mylist", storage_dir=tmp_watchlist_dir)
    assert len(wl.items) == 2
