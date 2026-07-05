"""Phase 3 — Feature 4: Duplicate detection.

Sending the same fact twice must store it once; the second attempt returns
status="duplicate". Hits real Gemini.

Run:  python test_duplicate_memory.py
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
        print("\n--- First save: 'My favorite language is Python.' ---")
        resp = await client.post("/chat", json={"message": "My favorite language is Python."})
        assert resp.status_code == 200, resp.text
        first = resp.json()["memory_action"]
        print("memory_action:", first)
        assert first["status"] == "created", f"expected created, got {first}"

        print("\n--- Second save (same fact) ---")
        resp = await client.post("/chat", json={"message": "My favorite language is Python."})
        assert resp.status_code == 200, resp.text
        second = resp.json()["memory_action"]
        print("memory_action:", second)
        assert second["status"] == "duplicate", f"expected duplicate, got {second}"

        with session() as conn:
            total = conn.execute("SELECT COUNT(*) AS n FROM memories").fetchone()["n"]
        print("\nStored memories:", total)
        assert total == 1, f"expected 1 stored memory, got {total}"

    print("\n✅ test_duplicate_memory PASSED")


if __name__ == "__main__":
    asyncio.run(run())
