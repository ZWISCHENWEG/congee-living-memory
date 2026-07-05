"""Phase 3 — Feature 6: Conflict detection + resolution.

When a new fact conflicts with an existing one but the auto-replace confidence
bar isn't met, the engine returns status="conflict" (pending frontend
confirmation) instead of silently overwriting. The frontend then confirms via
POST /memory/resolve-conflict.

To exercise this deterministically we raise the auto-replace confidence bar to a
value Gemini won't clear, forcing the conflict branch. Hits real Gemini.

Run:  python test_conflict_memory.py
"""

import asyncio
import logging
import sys

from httpx import ASGITransport, AsyncClient

sys.path.append(".")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def run():
    from app.config import settings
    from app.db import init_db, session
    from app.main import app

    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    # Force the conflict branch: the auto-replace check is `confidence > bar`, so
    # a bar of 1.0 can never be cleared (even a max-confidence 1.0) — any detected
    # replacement is surfaced as a conflict rather than auto-applied.
    original_bar = settings.conflict_confidence
    settings.conflict_confidence = 1.0

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            print("\n--- Seed: 'My favorite color is blue.' ---")
            resp = await client.post("/chat", json={"message": "My favorite color is blue."})
            assert resp.status_code == 200, resp.text
            created = resp.json()["memory_action"]
            print("memory_action:", created)
            assert created["status"] == "created", f"expected created, got {created}"
            existing_id = created["memory_id"]

            print("\n--- Conflicting: 'Actually my favorite color is green.' ---")
            resp = await client.post(
                "/chat", json={"message": "Actually my favorite color is green."}
            )
            assert resp.status_code == 200, resp.text
            conflict = resp.json()["memory_action"]
            print("memory_action:", conflict)
            assert conflict["status"] == "conflict", f"expected conflict, got {conflict}"
            assert conflict["memory_id"] == existing_id

            # Still exactly one memory, unchanged, pending user confirmation.
            with session() as conn:
                rows = conn.execute("SELECT content FROM memories").fetchall()
            assert len(rows) == 1 and "blue" in rows[0]["content"].lower(), rows

            print("\n--- Resolve: user confirms replacement ---")
            resp = await client.post(
                "/memory/resolve-conflict",
                json={
                    "existing_id": existing_id,
                    "new_content": "My favorite color is green.",
                    "decision": "replace",
                    "type": "preference",
                    "importance": 0.75,
                },
            )
            assert resp.status_code == 200, resp.text
            resolved = resp.json()
            print("resolution:", resolved)
            assert resolved["status"] == "updated", f"expected updated, got {resolved}"

            with session() as conn:
                rows = conn.execute("SELECT content FROM memories").fetchall()
            print("\nStored memories:", [dict(r) for r in rows])
            assert len(rows) == 1, f"expected 1 memory, got {len(rows)}"
            assert "green" in rows[0]["content"].lower(), "content should now reference green"
    finally:
        settings.conflict_confidence = original_bar

    print("\n✅ test_conflict_memory PASSED")


if __name__ == "__main__":
    asyncio.run(run())
