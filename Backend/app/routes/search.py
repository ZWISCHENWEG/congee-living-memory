from fastapi import APIRouter, Query
from app.db import session
from app.schemas.search import SearchResponse, SearchResultSchema

router = APIRouter(tags=["search"])

@router.get("/search", response_model=SearchResponse)
def search_memories(q: str = Query(..., min_length=1)):
    with session() as conn:
        cursor = conn.cursor()
        query = "SELECT id, content FROM memories WHERE content LIKE ? LIMIT 10"
        cursor.execute(query, (f"%{q}%",))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(SearchResultSchema(
                id=row["id"],
                content=row["content"],
                score=0.99  # Mocked similarity score
            ))
            
        return SearchResponse(results=results)
