from pydantic import BaseModel


class MemorySchema(BaseModel):
    id: str
    content: str
    created_at: str
    tags: list[str] | None = None
    # Phase 3 metadata (all optional for backwards compatibility).
    type: str | None = None
    importance: float | None = None
    usage_count: int | None = None
    last_accessed: str | None = None
    updated_at: str | None = None


class MetaSchema(BaseModel):
    total: int
    page: int
    limit: int


class MemoriesResponse(BaseModel):
    data: list[MemorySchema]
    meta: MetaSchema


class MemoryCreate(BaseModel):
    content: str
    tags: list[str] | None = None
    # Phase 3: optional category + importance. Manual POST /memory callers may
    # omit these; the automatic pipeline always supplies them.
    type: str | None = None
    importance: float | None = None
