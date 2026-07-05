import logging
import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.append(".")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@pytest.mark.anyio
async def test_chat_memory():
    from app.main import app
    from app.services.ai import get_ai_provider
    from app.services.embedding.factory import get_embedding_provider
    from tests_mock import MockAIProvider, MockEmbeddingProvider

    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()

    from app.db import init_db, session

    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- Seeding Memory ---")
        mem_text = "My favorite language is Python."
        resp = await client.post("/memory", json={"content": mem_text, "tags": []})
        assert resp.status_code == 201, f"Failed to seed memory: {resp.text}"

        print("\n--- Chatting ---")
        chat_req = {"message": "What language do I like?"}
        resp = await client.post("/chat", json=chat_req)
        assert resp.status_code == 200, f"Chat failed: {resp.text}"

        data = resp.json()
        print("\n--- Chat Response ---")
        print("Response:", data.get("response"))
        used_memories = data.get("used_memories", [])
        print("Used Memories count:", len(used_memories))

        # Verify the used memory matches our seeded memory
        found = any(m.get("content") == mem_text for m in used_memories)
        assert found, "Seeded memory was not found in used_memories!"

        print("\nALL VERIFICATIONS PASSED")
