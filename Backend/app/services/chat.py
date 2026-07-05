import asyncio
import logging

from fastapi import Depends

from app.schemas.memory_engine import MemoryAction
from app.schemas.search import SearchResultSchema
from app.services.ai import get_ai_provider
from app.services.ai.base import AIProvider, GenerationResult
from app.services.auto_memory import AutoMemoryService, get_auto_memory_service
from app.services.memory import MemoryService, get_memory_service
from app.services.prompt_builder import PromptBuilder, get_prompt_builder
from app.services.search import SearchService, get_search_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for orchestrating memory retrieval, AI generation, and the
    autonomous memory pipeline."""

    def __init__(
        self,
        provider: AIProvider,
        search_service: SearchService,
        prompt_builder: PromptBuilder,
        auto_memory: AutoMemoryService,
        memory_service: MemoryService,
    ):
        self.provider = provider
        self.search_service = search_service
        self.prompt_builder = prompt_builder
        self.auto_memory = auto_memory
        self.memory_service = memory_service

    async def generate_response(
        self, user_message: str
    ) -> tuple[GenerationResult, list[SearchResultSchema], MemoryAction]:
        """Process a user message: retrieve memories, generate a reply, and run
        the autonomous memory pipeline concurrently with generation."""

        # 1. Search memories (unchanged Phase 2 retrieval).
        logger.info("Received user message")
        logger.info("Searching memories")
        try:
            memories = await self.search_service.search(user_message)
        except Exception as e:
            logger.warning("Search failed, continuing without memories: %s", e)
            memories = []

        memories = memories[:5]
        logger.info("Retrieved %d memories", len(memories))

        # 2. Record usage of retrieved memories (Features 8 & 9). Best-effort.
        self.memory_service.mark_used([m.id for m in memories])

        # 3. Build the prompt (unchanged).
        logger.info("Building prompt")
        prompt = self.prompt_builder.build(user_message, memories)

        # 4. Generate the reply AND run the memory pipeline concurrently.
        logger.info("Calling Gemini")
        result, memory_action = await asyncio.gather(
            self.provider.generate(prompt),
            self.auto_memory.process(user_message),
        )
        logger.info("Received Gemini response")
        logger.info("Memory action: %s", memory_action.status)

        return result, memories, memory_action


def get_chat_service(
    provider: AIProvider = Depends(get_ai_provider),
    search_service: SearchService = Depends(get_search_service),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    auto_memory: AutoMemoryService = Depends(get_auto_memory_service),
    memory_service: MemoryService = Depends(get_memory_service),
) -> ChatService:
    return ChatService(provider, search_service, prompt_builder, auto_memory, memory_service)
