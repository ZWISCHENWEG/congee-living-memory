"""Database connectivity for Chronos.

Thin SQLite layer using the standard library `sqlite3`. Business logic and
schema (tables) will be added later — this module only provides connection
management and lifecycle hooks so the app can start cleanly.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.config import settings


def _resolve_sqlite_path() -> Path:
    """Extract the filesystem path from a `sqlite:///` URL."""
    url = settings.database_url
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        raise ValueError(f"Unsupported database_url (expected sqlite:///): {url!r}")
    return Path(url[len(prefix):]).resolve()


def get_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with sane defaults."""
    path = _resolve_sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def session() -> Iterator[sqlite3.Connection]:
    """Context-managed connection that commits on success and rolls back on error."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database.

    Verifies connectivity at startup. Table creation will be added alongside
    the data models in a later milestone.
    """
    with session() as conn:
        conn.execute("SELECT 1;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                tags TEXT
            )
        """)
        try:
            conn.execute("ALTER TABLE memories ADD COLUMN embedding TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass
