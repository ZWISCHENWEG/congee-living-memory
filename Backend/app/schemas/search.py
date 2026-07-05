from pydantic import BaseModel


class SearchResultSchema(BaseModel):
    id: str
    content: str
    score: float | None = None


class SearchResponse(BaseModel):
    results: list[SearchResultSchema]
