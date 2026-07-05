from app.db import session
from app.services.memory_repository.base import MemoryRepository

#: Columns returned for read operations (keeps SELECTs consistent).
_MEMORY_COLUMNS = (
    "id, content, created_at, tags, type, importance, usage_count, last_accessed, updated_at"
)


class SQLiteMemoryRepository(MemoryRepository):
    """SQLite implementation for memory persistence."""

    def insert_memory(
        self,
        memory_id: str,
        content: str,
        created_at: str,
        tags_json: str,
        embedding_json: str | None,
        type: str = "other",
        importance: float = 0.5,
    ) -> None:
        with session() as conn:
            conn.execute(
                """
                INSERT INTO memories
                (id, content, created_at, tags, embedding, type, importance, usage_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (memory_id, content, created_at, tags_json, embedding_json, type, importance),
            )

    def delete_memory(self, memory_id: str) -> None:
        with session() as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

    def get_by_id(self, memory_id: str) -> dict | None:
        with session() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {_MEMORY_COLUMNS} FROM memories WHERE id = ?", (memory_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_memory(
        self,
        memory_id: str,
        content: str,
        embedding_json: str | None,
        type: str,
        importance: float,
        updated_at: str,
    ) -> None:
        with session() as conn:
            conn.execute(
                """
                UPDATE memories
                SET content = ?, embedding = ?, type = ?, importance = ?, updated_at = ?
                WHERE id = ?
                """,
                (content, embedding_json, type, importance, updated_at, memory_id),
            )

    def mark_used(self, memory_id: str, last_accessed: str) -> None:
        with session() as conn:
            conn.execute(
                """
                UPDATE memories
                SET usage_count = COALESCE(usage_count, 0) + 1, last_accessed = ?
                WHERE id = ?
                """,
                (last_accessed, memory_id),
            )

    def get_memories(self, page: int, limit: int, search: str | None) -> tuple[list[dict], int]:
        with session() as conn:
            cursor = conn.cursor()

            where_clause = ""
            params = []
            if search:
                where_clause = "WHERE content LIKE ?"
                params.append(f"%{search}%")

            count_query = f"SELECT COUNT(*) as total FROM memories {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            offset = (page - 1) * limit
            query = (
                f"SELECT {_MEMORY_COLUMNS} FROM memories {where_clause} "
                "ORDER BY created_at DESC LIMIT ? OFFSET ?"
            )
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = [dict(row) for row in rows]
            return results, total
