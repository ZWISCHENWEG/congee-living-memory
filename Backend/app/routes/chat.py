import uuid
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def handle_chat(chat_req: ChatRequest):
    # Dummy implementation for MVP logic
    return ChatResponse(
        id=f"msg_{uuid.uuid4().hex[:12]}",
        reply=f"Chronos received: {chat_req.message}. I am a living memory engine.",
        conversation_id=chat_req.conversation_id or f"conv_{uuid.uuid4().hex[:12]}",
        referenced_memories=[]
    )
