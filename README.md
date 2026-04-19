# 🎬 CineMatch

A Python movie discovery library and REST API powered by the [TMDB API](https://www.themoviedb.org/documentation/api).

Search by title, mood, genre, or decade. Discover hidden gems. Manage personal watchlists. All through a clean HTTP interface — or call the library directly from Python.

---

## Architecture

```
cinematch/
├── cinematch/               # Python library (business logic — no HTTP)
│   ├── tmdb_client.py       # Low-level TMDB HTTP client + rate limiting
│   ├── models.py            # Pydantic domain models (Movie, Watchlist, …)
│   ├── movies.py            # Movie search & discovery functions
│   ├── watchlists.py        # Watchlist CRUD (persisted as JSON on disk)
│   ├── app.py               # FastAPI application factory
│   └── routers/
│       ├── movies.py        # /movies/* HTTP endpoints
│       └── watchlists.py    # /watchlists/* HTTP endpoints
├── tests/
│   ├── conftest.py          # Shared fixtures + mock TMDB payloads
│   ├── test_movies.py       # Unit tests for movies library
│   ├── test_watchlists.py   # Unit tests for watchlists library
│   └── test_api.py          # Integration tests for HTTP endpoints
├── .github/workflows/ci.yml # GitHub Actions: lint + test on every push/PR
└── pyproject.toml           # Project metadata, ruff config, pytest config
```

The HTTP layer (`app.py`, `routers/`) is intentionally thin — it only validates inputs and translates library results into HTTP responses. All logic lives in `movies.py` and `watchlists.py`.

---

## Quickstart

### 1. Get a free TMDB API key

Sign up at [themoviedb.org](https://www.themoviedb.org/settings/api) — it's free and instant.

### 2. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/cinematch.git
cd cinematch
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Set your API key

```bash
export TMDB_API_KEY=your_key_here  # Windows: set TMDB_API_KEY=your_key_here
```

### 4. Run the API server

```bash
uvicorn cinematch.app:app --reload
```

Open **http://localhost:8000/docs** to explore the interactive API documentation.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/movies/search?q=...` | Search movies by title |
| `GET` | `/movies/trending` | Trending movies (day/week) |
| `GET` | `/movies/hidden-gems` | High-rated, low-popularity picks |
| `GET` | `/movies/genres` | List all genre IDs and names |
| `GET` | `/movies/moods` | List supported mood keywords |
| `GET` | `/movies/discover/mood?mood=happy` | Discover by mood |
| `GET` | `/movies/discover/genre?genre=Comedy` | Discover by genre |
| `GET` | `/movies/discover/decade?decade=1990` | Discover by decade |
| `GET` | `/movies/{id}` | Full movie details |
| `GET` | `/movies/{id}/recommendations` | Recommendations from a seed movie |
| `GET` | `/watchlists/` | List all watchlists |
| `POST` | `/watchlists/?name=...` | Create a watchlist |
| `GET` | `/watchlists/{name}` | Get watchlist contents |
| `DELETE` | `/watchlists/{name}` | Delete a watchlist |
| `POST` | `/watchlists/{name}/movies` | Add a movie to a watchlist |
| `DELETE` | `/watchlists/{name}/movies/{id}` | Remove a movie |
| `PATCH` | `/watchlists/{name}/movies/{id}/watched` | Mark a movie as watched |

**Supported moods:** `happy`, `sad`, `excited`, `scared`, `romantic`, `thoughtful`, `adventurous`, `chill`

---

## Using the library directly (no HTTP)

```python
import os
os.environ["TMDB_API_KEY"] = "your_key"

from cinematch import movies, watchlists

# Search
results = movies.search("Inception")
print(results[0].title, results[0].year)

# Discover
gems = movies.find_hidden_gems()
happy_films = movies.discover_by_mood("happy")
nineties = movies.discover_by_decade(1990)

# Watchlist
watchlists.create("weekend")
watchlists.add_movie("weekend", movie_id=550, title="Fight Club")
watchlists.mark_watched("weekend", movie_id=550)
wl = watchlists.get("weekend")
print(wl.items)
```

---

## Running the tests

```bash
pytest
```

Tests run with `--cov` automatically (configured in `pyproject.toml`). An HTML coverage report is generated at `htmlcov/index.html`.

All tests mock the TMDB API — **no real API key is needed to run tests**.

```bash
TMDB_API_KEY=fake pytest   # explicit, in case env var is not set
```

---

## Linting and formatting

```bash
ruff check .          # lint
ruff format .         # format
ruff check --fix .    # auto-fix lint issues
```

CI runs both on every push and pull request.

---

## AI Usage Disclosure

This project was built with the assistance of Claude (Anthropic). The following were generated with AI:

- Initial project file structure and module layout
  
---

## Contributor
Ashley Wang &
Michael Zhang

---

## Contributing

1. Create a branch from `main`
2. Make changes and add tests
3. Run `ruff check .` and `pytest` — both must pass
4. Open a pull request and request review 
