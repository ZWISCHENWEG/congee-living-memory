from google import genai
from app.services.embedding.base import EmbeddingProvider, EmbeddingGenerationError

class GeminiEmbeddingProvider(EmbeddingProvider):
    """Google Gemini embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gemini-embedding-2"):
        self.api_key = api_key
        self.model = model
        self._client = genai.Client(api_key=self.api_key)
        
    @property
    def name(self) -> str:
        return "gemini_embedding"
        
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a semantic embedding vector for the text using Gemini API."""
        try:
            response = await self._client.aio.models.embed_content(
                model=self.model,
                contents=text
            )
            if not response.embeddings or not response.embeddings[0].values:
                raise EmbeddingGenerationError("Received empty embedding from Gemini.")
            return response.embeddings[0].values
        except Exception as e:
            if isinstance(e, EmbeddingGenerationError):
                raise
            raise EmbeddingGenerationError(f"Gemini API error during embedding: {e}") from e
