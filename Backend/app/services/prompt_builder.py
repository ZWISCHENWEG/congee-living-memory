from typing import List
from app.schemas.search import SearchResultSchema

class PromptBuilder:
    """Builds the AI prompt by combining system instructions, memories, and user messages."""
    
    def __init__(self, max_memories: int = 10):
        self.max_memories = max_memories

    def build(self, user_message: str, memories: List[SearchResultSchema]) -> str:
        """Construct the prompt using a strict layout without polluting the AI provider."""
        system_instruction = "System:\nYou are Congee, a living memory engine. Use the provided memories to answer the user's message accurately and contextually."
        
        # Enforce strict retrieval limit to prevent massive prompts
        safe_memories = memories[:self.max_memories]
        
        if safe_memories:
            memory_texts = "\n".join([f"- {m.content}" for m in safe_memories])
            memory_section = f"Relevant Memories:\n{memory_texts}"
        else:
            memory_section = "Relevant Memories:\n(No relevant memories found)"
            
        user_section = f"User:\n{user_message}"
        
        return f"{system_instruction}\n\n{memory_section}\n\n{user_section}"

def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()
