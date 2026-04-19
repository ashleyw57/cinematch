"""CineMatch HTTP API – FastAPI application factory."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cinematch.routers import movies, watchlists

app = FastAPI(
    title="CineMatch",
    description=(
        "A movie discovery API powered by TMDB. "
        "Search by title, mood, genre, or decade. "
        "Manage personal watchlists."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])

_static = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_static), name="static")


@app.get("/", tags=["Health"], include_in_schema=False)
def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
