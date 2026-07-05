import asyncio
import os
import sys
import json
import sqlite3

# Inject API key to make it proceed
os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'

sys.path.append('Backend')

from fastapi.testclient import TestClient
from app.main import app
from app.db import get_connection, session

client = TestClient(app)

def main():
    print("Testing Memory Creation API...")
    
    # We will mock the gemini provider to return a real vector so we can test semantic search
    from app.services.embedding import get_embedding_provider, EmbeddingProvider
    from app.services.embedding.gemini import GeminiEmbeddingProvider
    
    class MockProvider(GeminiEmbeddingProvider):
        async def generate_embedding(self, text: str) -> list[float]:
            if "dimension" in text:
                return [1.0, 0.0] # dim mismatch
            return [1.0, 0.0, 0.0]
    
    # override dependency
    app.dependency_overrides[get_embedding_provider] = lambda: MockProvider("fake")

    # 1. Clear database
    with session() as conn:
        conn.execute("DELETE FROM memories")
    
    # 2. Test Create Memory
    resp = client.post("/memory", json={"content": "I like fast cars.", "tags": ["cars"]})
    assert resp.status_code == 201
    created_mem = resp.json()
    assert created_mem["content"] == "I like fast cars."
    print("✓ POST /memory succeeds")
    
    # 3. Verify embedding stored in database
    with session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT embedding FROM memories WHERE id = ?", (created_mem["id"],))
        emb = cursor.fetchone()[0]
        assert emb is not None
        assert json.loads(emb) == [1.0, 0.0, 0.0]
    print("✓ POST /memory correctly generates and stores embedding via Service architecture")
    
    # 4. Test Semantic Search using newly created memory
    # We send a query. The MockProvider will return [1.0, 0.0, 0.0] for the query.
    # The cosine similarity will be 1.0 (perfect match).
    # Since it's > 0.72, it should return our new memory!
    search_resp = client.get("/search?q=cars")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert len(search_data["results"]) == 1
    assert search_data["results"][0]["id"] == created_mem["id"]
    print("✓ Semantic search returns newly created memories")
    
    # 5. Test GET /memories unchanged
    get_resp = client.get("/memories")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["meta"]["total"] == 1
    print("✓ GET /memories unchanged")
    
    # 6. Test DELETE
    del_resp = client.delete(f"/memory/{created_mem['id']}")
    assert del_resp.status_code == 204
    get_resp2 = client.get("/memories")
    assert get_resp2.json()["meta"]["total"] == 0
    print("✓ DELETE unchanged")
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    main()
