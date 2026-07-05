from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    reply: str
    conversation_id: Optional[str] = None
    referenced_memories: Optional[List[str]] = None
