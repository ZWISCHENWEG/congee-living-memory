import json
import logging
import math
from datetime import UTC, datetime

from app.config import get_settings
from app.db import session
from app.schemas.search import SearchResultSchema
from app.services.search_backends.base import SearchBackend

logger = logging.getLogger(__name__)


class SQLiteSearchBackend(SearchBackend):
    """SQLite implementation of the SearchBackend.

    Computes semantic similarity in Python. For chat retrieval, qualifying
    results (those above the similarity threshold) are re-ranked by a composite
    score (Feature 11). Falls back to LIKE when no semantic result is available.
    """

    def __init__(self, default_limit: int = 10, default_threshold: float = 0.72):
        self.default_limit = default_limit
        self.default_threshold = default_threshold

    @property
    def name(self) -> str:
        return "sqlite"

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        val = dot_product / (norm_a * norm_b)
        if math.isnan(val) or math.isinf(val):
            return 0.0

        return val

    def _parse_embedding(self, raw: str | None) -> list[float] | None:
        """Decode and validate a stored embedding, or None if unusable."""
        if not raw:
            return None
        try:
            emb = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(emb, list) or not emb:
            return None
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in emb):
            return None
        return emb

    def _score_rows(self, query_embedding: list[float], rows: list) -> list[tuple[float, dict]]:
        """Score every embedded row against the query. Returns (cosine, row)."""
        scored = []
        for row in rows:
            mem_emb = self._parse_embedding(row["embedding"])
            if mem_emb is None:
                continue
            cosine = self._cosine_similarity(query_embedding, mem_emb)
            scored.append((cosine, dict(row)))
        return scored

    @staticmethod
    def _recency(created_at: str | None) -> float:
        """Age-decay recency in (0, 1]; newest ≈ 1. Robust to bad timestamps."""
        if not created_at:
            return 0.0
        try:
            ts = datetime.fromisoformat(created_at)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
        except ValueError:
            return 0.0
        age_days = max(0.0, (datetime.now(UTC) - ts).total_seconds() / 86400.0)
        return 1.0 / (1.0 + age_days)

    def _composite_score(self, cosine: float, row: dict, max_usage: int) -> float:
        """Blend similarity, importance, recency, and usage (Feature 11)."""
        s = get_settings()
        similarity = max(0.0, min(1.0, cosine))
        importance = row["importance"] if row["importance"] is not None else 0.5
        usage = row["usage_count"] if row["usage_count"] is not None else 0
        usage_norm = (usage / max_usage) if max_usage > 0 else 0.0
        recency = self._recency(row["created_at"])
        return (
            s.rank_weight_similarity * similarity
            + s.rank_weight_importance * importance
            + s.rank_weight_recency * recency
            + s.rank_weight_usage * usage_norm
        )

    def search(
        self,
        query_embedding: list[float] | None,
        query_text: str,
        limit: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[SearchResultSchema]:
        """Fetch memories, perform semantic search locally, fallback to LIKE."""

        limit = limit if limit is not None else self.default_limit
        similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else self.default_threshold
        )

        with session() as conn:
            cursor = conn.cursor()

            if query_embedding:
                cursor.execute(
                    "SELECT id, content, embedding, importance, usage_count, "
                    "created_at, last_accessed FROM memories"
                )
                rows = cursor.fetchall()

                logger.info("Executing cosine similarity")
                scored = self._score_rows(query_embedding, rows)

                # Preserve the existing threshold filter unchanged (which memories qualify).
                qualifying = [
                    (cosine, row) for cosine, row in scored if cosine >= similarity_threshold
                ]
                logger.info("Similarity results count: %d", len(qualifying))

                if qualifying:
                    logger.info("Semantic search used via sqlite backend")
                    # Feature 11: re-rank qualifying results by composite score.
                    max_usage = max((r["usage_count"] or 0 for _, r in qualifying), default=0)
                    ranked = [
                        (self._composite_score(cosine, row, max_usage), row)
                        for cosine, row in qualifying
                    ]
                    ranked.sort(key=lambda x: x[0], reverse=True)
                    logger.info("Semantic search complete (composite ranking applied)")
                    return [
                        SearchResultSchema(
                            id=row["id"], content=row["content"], score=round(score, 4)
                        )
                        for score, row in ranked[:limit]
                    ]
                else:
                    logger.info(
                        "Fallback reason: No memories scored above the similarity threshold of %f",
                        similarity_threshold,
                    )
            else:
                logger.info("Fallback reason: query_embedding is None")

            # Fallback to SQL LIKE (unchanged Phase 1/2 behavior).
            logger.info("Fallback activated to LIKE search")
            query = "SELECT id, content FROM memories WHERE content LIKE ? LIMIT ?"
            cursor.execute(query, (f"%{query_text}%", limit))
            rows = cursor.fetchall()

            return [
                SearchResultSchema(id=row["id"], content=row["content"], score=0.0) for row in rows
            ]

    def similarity_search(
        self,
        query_embedding: list[float] | None,
        top_k: int = 5,
    ) -> list[SearchResultSchema]:
        """Top_k memories by raw cosine similarity (no threshold, no composite)."""
        if not query_embedding:
            return []

        with session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, embedding FROM memories")
            rows = cursor.fetchall()

        scored = self._score_rows(query_embedding, rows)
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            SearchResultSchema(id=row["id"], content=row["content"], score=round(cosine, 4))
            for cosine, row in scored[:top_k]
        ]
