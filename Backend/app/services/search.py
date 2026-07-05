from app.db import session
from app.schemas.search import SearchResultSchema
from typing import List

class SearchService:
    """Service for searching memories in the database."""
    
    def search(self, query_text: str) -> List[SearchResultSchema]:
        """Search memories using the existing SQL abstraction."""
        with session() as conn:
            cursor = conn.cursor()
            # Reusing the exact existing search logic from the route
            query = "SELECT id, content FROM memories WHERE content LIKE ? LIMIT 10"
            cursor.execute(query, (f"%{query_text}%",))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append(SearchResultSchema(
                    id=row["id"],
                    content=row["content"],
                    score=0.99  # Mocked similarity score preserved
                ))
                
        return results

def get_search_service() -> SearchService:
    return SearchService()
