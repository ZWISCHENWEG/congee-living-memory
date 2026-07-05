"""Chronos FastAPI application entrypoint.

Run in development with:
    uv run uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routes import chat, health, memories, memory_resolve, root, search

# Configure basic logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    logger.info("Initializing database...")
    init_db()

    logger.info("Loaded Gemini model: %s", settings.gemini_model)
    logger.info("Gemini configured: %s", settings.gemini_configured)

    if settings.gemini_api_key:
        key = settings.gemini_api_key
        safe_key = f"{key[:4]}********{key[-4:]}" if len(key) > 8 else "True"
        logger.info("API key exists: %s", safe_key)
    else:
        logger.info("API key exists: False")

    logger.info("Chronos backend started successfully.")
    yield
    logger.info("Chronos backend shutting down.")


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

    # Routers: system (/, /health), memories CRUD, chat, search, and the
    # conflict-resolution endpoint for the autonomous memory engine.
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(memories.router)
    app.include_router(chat.router)
    app.include_router(search.router)
    app.include_router(memory_resolve.router)

    return app


app = create_app()
