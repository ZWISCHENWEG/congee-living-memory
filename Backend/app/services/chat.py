import logging
from typing import Tuple, List

from fastapi import Depends
from app.schemas.search import SearchResultSchema
from app.services.search import get_search_service, SearchService
from app.services.ai import get_ai_provider
from app.services.ai.base import AIProvider, GenerationResult
from app.services.prompt_builder import get_prompt_builder, PromptBuilder

logger = logging.getLogger(__name__)

class ChatService:
    """Service for orchestrating memory retrieval and AI generation."""
    
    def __init__(self, provider: AIProvider, search_service: SearchService, prompt_builder: PromptBuilder):
        self.provider = provider
        self.search_service = search_service
        self.prompt_builder = prompt_builder

    async def generate_response(self, user_message: str) -> Tuple[GenerationResult, List[SearchResultSchema]]:
        """Process a user message by retrieving memories and generating an AI response."""
        
        # 1. Search memories
        memories = await self.search_service.search(user_message)
        logger.info("Retrieved %d memories for chat", len(memories))
        
        # 2. Build Prompt
        prompt = self.prompt_builder.build(user_message, memories)
        
        # 3. Call AI
        logger.info("Calling provider: %s", self.provider.name)
        result = await self.provider.generate(prompt)
        
        return result, memories

def get_chat_service(
    provider: AIProvider = Depends(get_ai_provider),
    search_service: SearchService = Depends(get_search_service),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder)
) -> ChatService:
    return ChatService(provider, search_service, prompt_builder)
