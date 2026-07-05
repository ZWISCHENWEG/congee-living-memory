"""Chronos FastAPI application entrypoint.

Run in development with:
    uv run uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routes import health, root


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup: verify database connectivity.
    init_db()
    yield
    # Shutdown: nothing to tear down yet.


def create_app() -> FastAPI:
    """Application factory. Wires configuration, middleware, and routers."""
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description="Chronos — The Living Memory Engine.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers (only "/" and "/health" for now).
    app.include_router(root.router)
    app.include_router(health.router)
    
    from app.routes import memories, chat, search
    app.include_router(memories.router)
    app.include_router(chat.router)
    app.include_router(search.router)

    return app


app = create_app()
