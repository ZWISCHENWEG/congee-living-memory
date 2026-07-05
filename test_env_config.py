import asyncio
import os
import sys
import sqlite3
from httpx import ASGITransport, AsyncClient

sys.path.append('Backend')

def test_settings_loaded():
    from app.config import get_settings
    get_settings.cache_clear()
    settings = get_settings()
    
    assert settings.gemini_api_key == "<MY_NEW_API_KEY>", f"API Key not loaded correctly: {settings.gemini_api_key}"
    assert settings.gemini_model == "gemini-2.5-flash", "Model not loaded correctly"
    assert settings.gemini_configured is True, "Configured property should be true"
    print("✓ settings.gemini_api_key is populated at runtime")

async def test_api_behavior():
    from app.main import app
    from app.db import session, init_db
    
    # Ensure DB is fresh
    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # POST /memory
        print("Testing POST /memory with invalid API key (<MY_NEW_API_KEY>)...")
        resp = await client.post("/memory", json={"content": "Testing the .env configuration fallback", "tags": ["env"]})
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        mem = resp.json()
        mem_id = mem["id"]
        print("✓ POST /memory returns HTTP 201")
        
        # Verify DB stored NULL embedding
        with session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT embedding FROM memories WHERE id = ?", (mem_id,))
            emb = cursor.fetchone()[0]
            assert emb is None, "Embedding should be NULL due to invalid API key"
        print("✓ POST /memory stored the embedding as NULL gracefully")
        
        # Verify GET /search fallback
        print("Testing GET /search fallback...")
        search_resp = await client.get("/search?q=Testing")
        assert search_resp.status_code == 200, f"Expected 200, got {search_resp.status_code}"
        search_data = search_resp.json()
        assert len(search_data["results"]) == 1
        assert search_data["results"][0]["id"] == mem_id
        print("✓ GET /search gracefully fell back to keyword search (returns 200 OK)")

        # Verify GET /memories
        print("Testing GET /memories...")
        get_resp = await client.get("/memories")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["meta"]["total"] == 1
        print("✓ GET /memories still works")

async def main():
    test_settings_loaded()
    await test_api_behavior()
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
