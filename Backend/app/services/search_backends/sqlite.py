import json
import logging
import math
from typing import List, Optional
from app.db import session
from app.schemas.search import SearchResultSchema
from app.services.search_backends.base import SearchBackend
from app.config import get_settings

logger = logging.getLogger(__name__)

class SQLiteSearchBackend(SearchBackend):
    """SQLite implementation of the SearchBackend.
    
    Computes semantic similarity in Python and falls back to LIKE.
    """
    
    def __init__(self, default_limit: int = 10, default_threshold: float = 0.72):
        self.default_limit = default_limit
        self.default_threshold = default_threshold
        
    @property
    def name(self) -> str:
        return "sqlite"
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
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

    def search(
        self,
        query_embedding: Optional[List[float]],
        query_text: str,
        limit: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[SearchResultSchema]:
        """Fetch memories, perform semantic search locally, fallback to LIKE."""
        
        limit = limit if limit is not None else self.default_limit
        similarity_threshold = similarity_threshold if similarity_threshold is not None else self.default_threshold
        
        with session() as conn:
            cursor = conn.cursor()
            
            # If we have a query embedding, attempt semantic search first
            if query_embedding:
                cursor.execute("SELECT id, content, embedding FROM memories")
                rows = cursor.fetchall()
                
                scored_results = []
                for row in rows:
                    if not row["embedding"]:
                        continue
                        
                    try:
                        mem_emb = json.loads(row["embedding"])
                        if not isinstance(mem_emb, list):
                            continue
                        # Validate all floats
                        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in mem_emb):
                            continue
                    except (json.JSONDecodeError, TypeError):
                        continue
                        
                    score = self._cosine_similarity(query_embedding, mem_emb)
                    if score >= similarity_threshold:
                        scored_results.append((score, row["id"], row["content"]))
                
                if scored_results:
                    logger.info("Semantic search used via sqlite backend")
                    scored_results.sort(key=lambda x: x[0], reverse=True)
                    top_k = scored_results[:limit]
                    return [
                        SearchResultSchema(id=rid, content=content, score=round(score, 4))
                        for score, rid, content in top_k
                    ]
            
            # Fallback to SQL LIKE
            logger.info("Fallback activated to LIKE search")
            query = "SELECT id, content FROM memories WHERE content LIKE ? LIMIT ?"
            cursor.execute(query, (f"%{query_text}%", limit))
            rows = cursor.fetchall()
            
            return [
                SearchResultSchema(id=row["id"], content=row["content"], score=0.0)
                for row in rows
            ]
