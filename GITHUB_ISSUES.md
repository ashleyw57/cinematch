# GitHub Issues — CineMatch Project Plan

Copy each block below to create issues in your repo (Settings → Issues → New Issue).
Assign according to the labor split suggested in each issue.

---

## Issue #1 — Project scaffolding and repository setup
**Labels:** `setup`
**Assignee:** Both

Set up the repository with the initial project structure:

- Create `cinematch/` package with `__init__.py`
- Add `pyproject.toml` with dependencies (`fastapi`, `uvicorn`, `httpx`, `pydantic`) and dev deps (`pytest`, `pytest-cov`, `ruff`)
- Configure `ruff` for linting (line length 88, select E/F/I/UP/B/SIM/ANN)
- Configure `pytest` with `testpaths` and `--cov` defaults
- Add `.gitignore`
- Add `.github/workflows/ci.yml` to run `ruff check` and `pytest` on every push and PR

**Acceptance criteria:**
- `pip install -e ".[dev]"` works
- `ruff check .` passes with no errors
- `pytest` runs (even with 0 tests) without errors
- CI workflow triggers on push

---

## Issue #2 — TMDB API client (`tmdb_client.py`)
**Labels:** `library`, `core`
**Assignee:** Person A

Implement the low-level TMDB HTTP client module `cinematch/tmdb_client.py`:

- `get(endpoint, params)` function that appends `api_key` from `TMDB_API_KEY` env var
- Rate limiting: enforce max ~4 requests/sec using `time.monotonic()`
- Raise `RuntimeError` if `TMDB_API_KEY` is not set
- Raise `httpx.HTTPStatusError` on non-2xx responses
- Full docstring on `get()`

**Acceptance criteria:**
- `ruff check` passes
- Function is importable from `cinematch.tmdb_client`
- Raises `RuntimeError` when env var is missing

---

## Issue #3 — Domain models (`models.py`)
**Labels:** `library`, `core`
**Assignee:** Person A

Implement `cinematch/models.py` with Pydantic v2 models:

- `Movie` — id, title, overview, release_date, vote_average, vote_count, popularity, genre_ids, poster_path; computed properties `poster_url` and `year`
- `MovieDetail(Movie)` — adds genres, runtime, tagline, budget, revenue, homepage, imdb_id; computed property `genre_names`
- `WatchlistItem` — movie_id, title, added_at (ISO 8601), watched, notes
- `Watchlist` — name, items list; methods `add()`, `remove()`, `mark_watched()`
- `GENRE_MAP` dict (genre_id → name, all 19 TMDB genres)
- `MOOD_TO_GENRES` dict (8 moods → genre ID lists)

**Acceptance criteria:**
- All models importable from `cinematch.models`
- `Movie.poster_url` returns full URL or `None`
- `Movie.year` extracts 4-digit year from `release_date`
- `Watchlist.add()` deduplicates by `movie_id`

---

## Issue #4 — Movie discovery library (`movies.py`)
**Labels:** `library`, `feature`
**Assignee:** Person A

Implement `cinematch/movies.py` with these public functions:

- `search(query, page)` — keyword search via `/search/movie`
- `get_detail(movie_id)` → `MovieDetail` via `/movie/{id}`
- `get_recommendations(movie_id, page)` via `/movie/{id}/recommendations`
- `discover_by_mood(mood, page)` — maps mood keyword → genre IDs → `/discover/movie`; raises `ValueError` for unknown moods
- `discover_by_genre(genre, page)` — maps genre name → ID; raises `ValueError` for unknown genres
- `discover_by_decade(decade, page)` — validates decade is a multiple of 10; uses date range params
- `find_hidden_gems(page)` — vote_average ≥ 7.5, vote_count ≥ 100, popularity ≤ 20
- `trending(time_window)` — `"day"` or `"week"` via `/trending/movie/{window}`
- `list_genres()` → `dict[int, str]`
- `list_moods()` → `list[str]` (sorted)

All functions must have full docstrings (Args, Returns, Raises).

**Acceptance criteria:**
- All functions importable from `cinematch.movies`
- `ruff check` passes
- Unit tests in `tests/test_movies.py` pass (see Issue #7)

---

## Issue #5 — Watchlist persistence library (`watchlists.py`)
**Labels:** `library`, `feature`
**Assignee:** Person B

Implement `cinematch/watchlists.py` — file-based watchlist storage (JSON in `~/.cinematch/watchlists/`):

- `create(name, storage_dir)` → `Watchlist`; raises `FileExistsError` if name taken
- `get(name, storage_dir)` → `Watchlist`; raises `KeyError` if not found
- `list_all(storage_dir)` → `list[str]` (sorted names)
- `delete(name, storage_dir)`; raises `KeyError` if not found
- `add_movie(name, movie_id, title, notes, storage_dir)` → `Watchlist`
- `remove_movie(name, movie_id, storage_dir)` → `Watchlist`; raises `KeyError` if movie absent
- `mark_watched(name, movie_id, storage_dir)` → `Watchlist`; raises `KeyError` if movie absent

`storage_dir` parameter (default `None` → uses `~/.cinematch/watchlists/`) enables test isolation.

**Acceptance criteria:**
- Watchlists persist across process restarts (read back from disk)
- Duplicate adds are silently ignored
- Unit tests in `tests/test_watchlists.py` pass (see Issue #7)

---

## Issue #6 — HTTP API layer (FastAPI routers)
**Labels:** `api`, `feature`
**Assignee:** Person B

Implement the FastAPI HTTP interface:

**`cinematch/app.py`**
- Create `FastAPI` app with title, description, version
- Add CORS middleware (`allow_origins=["*"]`)
- Register both routers with prefixes `/movies` and `/watchlists`
- `GET /` health check returning `{"status": "ok"}`

**`cinematch/routers/movies.py`** — thin wrappers around `cinematch.movies`:
- `GET /movies/search?q=&page=`
- `GET /movies/trending?time_window=`
- `GET /movies/hidden-gems?page=`
- `GET /movies/genres`
- `GET /movies/moods`
- `GET /movies/discover/mood?mood=&page=`
- `GET /movies/discover/genre?genre=&page=`
- `GET /movies/discover/decade?decade=&page=`
- `GET /movies/{movie_id}`
- `GET /movies/{movie_id}/recommendations?page=`

**`cinematch/routers/watchlists.py`** — thin wrappers around `cinematch.watchlists`:
- `GET /watchlists/`
- `POST /watchlists/?name=` → 201
- `GET /watchlists/{name}`
- `DELETE /watchlists/{name}` → 204
- `POST /watchlists/{name}/movies` (body: `{movie_id, title, notes}`)
- `DELETE /watchlists/{name}/movies/{movie_id}`
- `PATCH /watchlists/{name}/movies/{movie_id}/watched`

Map `ValueError` → 400, `KeyError`/not found → 404, `FileExistsError` → 409.

**Acceptance criteria:**
- `uvicorn cinematch.app:app` starts without errors
- `/docs` renders interactive Swagger UI
- API tests in `tests/test_api.py` pass (see Issue #7)

---

## Issue #7 — Tests
**Labels:** `testing`
**Assignee:** Both (split by module)

Write comprehensive tests in `tests/`:

**`tests/conftest.py`** (shared):
- Sample TMDB payloads (`MOVIE_PAYLOAD`, `DETAIL_PAYLOAD`, `SEARCH_RESPONSE`, `DISCOVER_RESPONSE`)
- Fixtures: `client` (FastAPI TestClient), `tmp_watchlist_dir`, `mock_tmdb_*`

**`tests/test_movies.py`** (Person A):
- Test all functions in `cinematch.movies` using mocked `tmdb_client.get`
- Cover happy paths and all `ValueError`/`raises` branches

**`tests/test_watchlists.py`** (Person B):
- Test all functions in `cinematch.watchlists` using `tmp_watchlist_dir` fixture
- Cover: create, get, list, delete, add (incl. deduplication), remove, mark_watched, persistence

**`tests/test_api.py`** (Person B):
- Integration tests for every endpoint using `TestClient`
- Patch `tmdb_client.get` for movie endpoints
- Patch `_DEFAULT_DIR` via `monkeypatch` for watchlist endpoints
- Cover 4xx error responses

**Acceptance criteria:**
- `pytest` passes with 0 failures
- Coverage ≥ 85% across `cinematch/` (excluding `app.py` bootstrap)

---

## Issue #8 — Documentation and README
**Labels:** `docs`
**Assignee:** Both

Write `README.md` covering:

- Project name and one-line description
- Architecture diagram (directory tree + role of each module)
- Quickstart: get TMDB key → install → set env var → run server → open `/docs`
- Full endpoint table
- Example: using the library directly from Python
- How to run tests (`pytest`)
- How to lint (`ruff check .`, `ruff format .`)
- AI usage disclosure (tools used, how used, what produced)

**Acceptance criteria:**
- A teammate who has never seen the repo can run the server without asking questions
- AI usage section is complete and honest

---

## Issue #9 — Final QA and submission
**Labels:** `release`
**Assignee:** Both

Pre-submission checklist:

- [ ] All CI checks green on `main`
- [ ] `pytest` passes locally with `TMDB_API_KEY=<real_key>`
- [ ] Server starts, `/docs` works, at least 3 endpoints tested manually
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] README reviewed by both partners
- [ ] All group members have authored commits (no emailing code)
- [ ] All issues closed or linked to PRs
- [ ] Canvas submission link points to correct repo
