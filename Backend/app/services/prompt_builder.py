from typing import List
from app.schemas.search import SearchResultSchema

class PromptBuilder:
    """Builds the AI prompt by combining system instructions, memories, and user messages."""
    
    def __init__(self, max_memories: int = 5):
        self.max_memories = max_memories

    def build(self, user_message: str, memories: List[SearchResultSchema]) -> str:
        """Construct the production prompt using the strict layout."""
        system_instruction = (
            "You are Chronos.\n"
            "You are an intelligent assistant with long-term memory.\n"
            "You are provided with memories retrieved from semantic search.\n"
            "Use them naturally.\n"
            "Never mention vector search.\n"
            "Never say \"according to memory database.\"\n"
            "If memories conflict,\n"
            "prefer the newest one.\n"
            "If no memories are relevant,\n"
            "ignore the memory section."
        )
        
        safe_memories = memories[:self.max_memories]
        
        if safe_memories:
            memory_texts = "\n".join([f"• {m.content}" for m in safe_memories])
            memory_section = f"Relevant Memories\n{memory_texts}"
        else:
            memory_section = ""
            
        user_section = f"User:\n{user_message}\n\nAssistant:"
        
        parts = [system_instruction]
        if memory_section:
            parts.append(memory_section)
        parts.append(user_section)
        
        return "\n\n----------------------------------\n\n".join(parts)

def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()
