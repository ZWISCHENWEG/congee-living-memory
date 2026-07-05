import logging
import sys

import pytest
from httpx import ASGITransport, AsyncClient

"""Phase 3 — Feature 5: Memory update.

"I live in Ahmedabad." followed by "I moved to Surat." must UPDATE the existing
location memory in place (status="updated"), not create a second one. Hits real
Gemini.

Run:  python test_memory_update.py
"""



sys.path.append(".")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@pytest.mark.anyio
async def test_memory_update():
    from app.db import init_db, session
    from app.main import app
    from app.services.ai import get_ai_provider
    from app.services.embedding.factory import get_embedding_provider
    from tests_mock import MockAIProvider, MockEmbeddingProvider

    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()

    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- Seed: 'I live in Ahmedabad.' ---")
        resp = await client.post("/chat", json={"message": "I live in Ahmedabad."})
        assert resp.status_code == 200, resp.text
        created = resp.json()["memory_action"]
        print("memory_action:", created)
        assert created["status"] == "created", f"expected created, got {created}"
        original_id = created["memory_id"]

        print("\n--- Update: 'I moved to Surat.' ---")
        resp = await client.post("/chat", json={"message": "I moved to Surat."})
        assert resp.status_code == 200, resp.text
        updated = resp.json()["memory_action"]
        print("memory_action:", updated)
        assert updated["status"] == "updated", f"expected updated, got {updated}"
        assert updated["memory_id"] == original_id, "update should reuse the same memory id"

        with session() as conn:
            rows = conn.execute("SELECT content, updated_at FROM memories").fetchall()
        print("\nStored memories:", [dict(r) for r in rows])
        assert len(rows) == 1, f"expected 1 stored memory, got {len(rows)}"
        assert "surat" in rows[0]["content"].lower(), "content should now reference Surat"
        assert rows[0]["updated_at"] is not None, "updated_at should be stamped"

    print("\n✅ test_memory_update PASSED")
