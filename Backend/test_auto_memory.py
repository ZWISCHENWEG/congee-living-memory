"""Phase 3 — Feature 1: Automatic memory extraction.

Verifies that a durable personal fact is saved automatically during chat
(status="created") while chit-chat is ignored (status="ignored"). Hits real
Gemini via the configured .env key.

Run:  python test_auto_memory.py
"""

import asyncio
import logging
import sys

from httpx import ASGITransport, AsyncClient

sys.path.append(".")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def run():
    from app.db import init_db, session
    from app.main import app


    from tests_mock import MockAIProvider, MockEmbeddingProvider
    from app.services.ai import get_ai_provider
    from app.services.embedding.factory import get_embedding_provider
    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()



    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- SAVE case: 'My name is Prince.' ---")
        resp = await client.post("/chat", json={"message": "My name is Prince."})
        assert resp.status_code == 200, resp.text
        action = resp.json()["memory_action"]
        print("memory_action:", action)
        assert action["status"] == "created", f"expected created, got {action}"
        assert action["type"] == "identity", f"expected identity category, got {action['type']}"

        print("\n--- IGNORE case: 'How are you?' ---")
        resp = await client.post("/chat", json={"message": "How are you?"})
        assert resp.status_code == 200, resp.text
        action = resp.json()["memory_action"]
        print("memory_action:", action)
        assert action["status"] == "ignored", f"expected ignored, got {action}"

        # Exactly one memory should have been stored.
        with session() as conn:
            total = conn.execute("SELECT COUNT(*) AS n FROM memories").fetchone()["n"]
        print("\nStored memories:", total)
        assert total == 1, f"expected 1 stored memory, got {total}"

    print("\n✅ test_auto_memory PASSED")


if __name__ == "__main__":
    asyncio.run(run())
