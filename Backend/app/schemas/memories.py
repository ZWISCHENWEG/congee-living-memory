from pydantic import BaseModel, Field
from typing import List, Optional

class MemorySchema(BaseModel):
    id: str
    content: str
    created_at: str
    tags: Optional[List[str]] = None

class MetaSchema(BaseModel):
    total: int
    page: int
    limit: int

class MemoriesResponse(BaseModel):
    data: List[MemorySchema]
    meta: MetaSchema

class MemoryCreate(BaseModel):
    content: str
    tags: Optional[List[str]] = None
