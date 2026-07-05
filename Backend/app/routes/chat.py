import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import get_chat_service, ChatService
from app.services.ai import AIGenerationError, AIProviderUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def handle_chat(
    chat_req: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """Process a chat message using the configured AI provider."""
    try:
        result, memories = await chat_service.generate_response(chat_req.message)
    except AIProviderUnavailableError as e:
        logger.exception("AI provider unavailable: %s", e)
        # 503 is appropriate because a required backend service (the AI model) is unconfigured/unavailable
        raise HTTPException(status_code=503, detail="AI service is currently unavailable.")
    except AIGenerationError as e:
        logger.exception("AI generation failed: %s", e)
        # 502 Bad Gateway is appropriate because the upstream AI service failed
        raise HTTPException(status_code=502, detail="AI generation failed. Please try again later.")

    return ChatResponse(
        id=f"msg_{uuid.uuid4().hex[:12]}",
        reply=result.text,
        conversation_id=chat_req.conversation_id or f"conv_{uuid.uuid4().hex[:12]}",
        referenced_memories=[m.id for m in memories]
    )
