"""CineMatch HTTP API – FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/", tags=["Health"])
def root() -> dict:
    """Health check / welcome endpoint."""
    return {"status": "ok", "message": "Welcome to CineMatch 🎬"}
