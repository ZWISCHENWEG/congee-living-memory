import json
import logging
from typing import List

from app.services.ai.base import AIProvider, GenerationResult, ProviderHealth
from app.services.embedding.base import EmbeddingProvider

logger = logging.getLogger(__name__)

class MockEmbeddingProvider(EmbeddingProvider):
    @property
    def name(self) -> str:
        return "mock_embedding"

    async def generate_embedding(self, text: str) -> List[float]:
        # Hash the text to seed a deterministic random vector
        import hashlib
        import math
        
        # Group phrases to simulate semantic similarity
        normalized = text
        if "What language do I like" in text or "I like Python" in text or "My favorite language is Python" in text:
            normalized = "python_preference"
        elif "Forget that I like Python" in text:
            normalized = "python_preference"
        elif "favorite color is blue" in text or "favorite color is green" in text:
            normalized = "color_preference"
        elif "Ahmedabad" in text or "Surat" in text:
            normalized = "location"
            
        h = int(hashlib.md5(normalized.encode()).hexdigest()[:8], 16)
        angle = (h % 360) * (3.14159 / 180.0)
        
        vec = []
        for i in range(384):
            vec.append(math.cos(angle))
            vec.append(math.sin(angle))
            
        return vec

class MockAIProvider(AIProvider):
    name = "mock"

    async def generate(self, prompt: str) -> GenerationResult:
        logger.info(f"MockAIProvider generating for prompt length {len(prompt)}")
        
        # Chat prompt
        if "What language do I like?" in prompt and "User:\nWhat language do I like?" in prompt:
            text = "You like Python."
            return GenerationResult(text=text, model="mock", provider="mock", raw={})
            
        # Classification/Conflict prompts (search for the actual message injected)
        if 'User message:\n"""My name is Prince."""' in prompt:
            text = '{"action": "save", "memory": "My name is Prince.", "type": "identity", "importance": 1.0}'
        elif 'User message:\n"""How are you?"""' in prompt:
            text = '{"action": "none"}'
        elif 'User message:\n"""Actually my favorite color is green."""' in prompt:
            text = '{"action": "save", "memory": "Actually my favorite color is green.", "type": "preference", "importance": 0.75}'
        elif 'New memory: "Actually my favorite color is green."' in prompt:
            text = '{"replace": true, "confidence": 0.8, "reason": "updated color"}'
        elif 'User message:\n"""My favorite color is blue."""' in prompt:
            text = '{"action": "save", "memory": "My favorite color is blue.", "type": "preference", "importance": 0.75}'
        elif 'User message:\n"""My favorite language is Python."""' in prompt:
            text = '{"action": "save", "memory": "My favorite language is Python.", "type": "preference", "importance": 0.75}'
        elif 'User message:\n"""Forget that I like Python."""' in prompt:
            text = '{"action": "forget", "memory": "I like Python.", "type": "other", "importance": 0.0}'
        elif 'User message:\n"""I like Python."""' in prompt:
            text = '{"action": "save", "memory": "I like Python.", "type": "preference", "importance": 0.75}'
        elif 'User message:\n"""I moved to Surat."""' in prompt:
            text = '{"action": "save", "memory": "I moved to Surat.", "type": "location", "importance": 0.85}'
        elif 'New memory: "I moved to Surat."' in prompt:
            text = '{"replace": true, "confidence": 0.95, "reason": "moved"}'
        elif 'User message:\n"""I live in Ahmedabad."""' in prompt:
            text = '{"action": "save", "memory": "I live in Ahmedabad.", "type": "location", "importance": 0.85}'
        else:
            if "action =" in prompt:
                text = '{"action": "none"}'
            else:
                text = "Mock response"
                
        return GenerationResult(text=text, model="mock", provider="mock", raw={})

    async def health(self) -> ProviderHealth:
        return ProviderHealth(healthy=True, provider=self.name, detail="Mock OK")
