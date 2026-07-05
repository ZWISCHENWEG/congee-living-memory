"""Database connectivity for Chronos.

Thin SQLite layer using the standard library `sqlite3`. Provides connection
management (`get_connection`, `session`) and startup initialization (`init_db`),
which creates the `memories` table and applies the additive Phase 3 column
migrations idempotently.
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
    return Path(url[len(prefix) :]).resolve()


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


#: Phase 3 columns added to `memories` via idempotent migration. Each is applied
#: independently so re-runs (and partially-migrated databases) are safe. Existing
#: rows inherit the DEFAULT; no user data is ever dropped.
_MEMORY_MIGRATIONS: tuple[str, ...] = (
    "ALTER TABLE memories ADD COLUMN embedding TEXT",
    "ALTER TABLE memories ADD COLUMN type TEXT DEFAULT 'other'",
    "ALTER TABLE memories ADD COLUMN importance REAL DEFAULT 0.5",
    "ALTER TABLE memories ADD COLUMN usage_count INTEGER DEFAULT 0",
    "ALTER TABLE memories ADD COLUMN last_accessed TEXT",
    "ALTER TABLE memories ADD COLUMN updated_at TEXT",
)


def init_db() -> None:
    """Initialize the database.

    Verifies connectivity at startup, ensures the `memories` table exists, and
    applies the additive Phase 3 column migrations idempotently.
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
        for statement in _MEMORY_MIGRATIONS:
            try:
                conn.execute(statement)
            except sqlite3.OperationalError:
                # Column already exists — migration is a no-op.
                pass
