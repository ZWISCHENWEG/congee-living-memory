from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

from app.schemas.search import SearchResultSchema
from app.schemas.memory_engine import MemoryAction

class ChatResponse(BaseModel):
    response: str
    used_memories: List[SearchResultSchema]
    conversation_id: Optional[str] = None
    # Phase 3: outcome of the automatic memory pipeline for this turn. Optional
    # and defaults to None, so existing clients are unaffected.
    memory_action: Optional[MemoryAction] = None
