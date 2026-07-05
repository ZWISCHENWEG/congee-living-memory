from pydantic import BaseModel
from typing import List, Optional

class SearchResultSchema(BaseModel):
    id: str
    content: str
    score: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[SearchResultSchema]
