"""Phase 3 — Feature 7: Natural forgetting.

Save a fact, then ask to forget it in natural language. The engine must locate
the matching memory semantically and delete it (status="deleted"). Hits real
Gemini.

Run:  python test_forget_memory.py
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

    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- Seed: 'I like Python.' ---")
        resp = await client.post("/chat", json={"message": "I like Python."})
        assert resp.status_code == 200, resp.text
        created = resp.json()["memory_action"]
        print("memory_action:", created)
        assert created["status"] == "created", f"expected created, got {created}"

        with session() as conn:
            before = conn.execute("SELECT COUNT(*) AS n FROM memories").fetchone()["n"]
        assert before == 1, f"expected 1 memory before forget, got {before}"

        print("\n--- Forget: 'Forget that I like Python.' ---")
        resp = await client.post("/chat", json={"message": "Forget that I like Python."})
        assert resp.status_code == 200, resp.text
        forgotten = resp.json()["memory_action"]
        print("memory_action:", forgotten)
        assert forgotten["status"] == "deleted", f"expected deleted, got {forgotten}"

        with session() as conn:
            after = conn.execute("SELECT COUNT(*) AS n FROM memories").fetchone()["n"]
        print("\nStored memories after forget:", after)
        assert after == 0, f"expected 0 memories after forget, got {after}"

    print("\n✅ test_forget_memory PASSED")


if __name__ == "__main__":
    asyncio.run(run())
