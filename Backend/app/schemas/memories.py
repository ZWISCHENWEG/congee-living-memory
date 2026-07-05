from pydantic import BaseModel, Field
from typing import List, Optional

class MemorySchema(BaseModel):
    id: str
    content: str
    created_at: str
    tags: Optional[List[str]] = None
    # Phase 3 metadata (all optional for backwards compatibility).
    type: Optional[str] = None
    importance: Optional[float] = None
    usage_count: Optional[int] = None
    last_accessed: Optional[str] = None
    updated_at: Optional[str] = None

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
    # Phase 3: optional category + importance. Manual POST /memory callers may
    # omit these; the automatic pipeline always supplies them.
    type: Optional[str] = None
    importance: Optional[float] = None
