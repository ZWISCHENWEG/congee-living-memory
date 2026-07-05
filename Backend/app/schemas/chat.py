from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


from app.schemas.memory_engine import MemoryAction
from app.schemas.search import SearchResultSchema


class ChatResponse(BaseModel):
    response: str
    used_memories: list[SearchResultSchema]
    conversation_id: str | None = None
    # Phase 3: outcome of the automatic memory pipeline for this turn. Optional
    # and defaults to None, so existing clients are unaffected.
    memory_action: MemoryAction | None = None
