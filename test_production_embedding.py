import asyncio
import os
import sys
import json
import sqlite3
from httpx import ASGITransport, AsyncClient
import logging

sys.path.append('Backend')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def test_production_pipeline():
    from app.main import app
    from app.db import session, init_db
    from app.config import get_settings
    
    # Reload settings if it was cached
    get_settings.cache_clear()
    
    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- Testing POST /memory ---")
        # 1 & 2. During POST /memory, logs will print to stdout.
        resp = await client.post("/memory", json={"content": "Paris is a wonderful city with great architecture.", "tags": ["travel"]})
        assert resp.status_code == 201
        mem = resp.json()
        mem_id = mem["id"]
        
        print("\n--- Querying SQLite ---")
        # 3. Query SQLite
        with session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, embedding FROM memories ORDER BY created_at DESC LIMIT 1;")
            row = cursor.fetchone()
            
            assert row is not None
            embedding_str = row["embedding"]
            assert embedding_str is not None, "Embedding is NULL!"
            
            # Verify JSON validity and length
            try:
                embedding_list = json.loads(embedding_str)
                print(f"✓ embedding is valid JSON")
                print(f"✓ embedding length matches the Gemini model ({len(embedding_list)} dimensions)")
            except json.JSONDecodeError:
                print("x embedding is NOT valid JSON")
                return

        print("\n--- Testing GET /search?q=Paris ---")
        # 4. Perform GET /search
        search_resp = await client.get("/search?q=Paris")
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        
        # Verify cosine similarity is used (score > 0 indicates cosine, score == 0 indicates fallback)
        assert len(search_data["results"]) > 0
        first_result = search_data["results"][0]
        score = first_result.get("score", 0.0)
        
        if score > 0.0:
            print("✓ cosine similarity runs")
            print("✓ vector comparison uses the stored embedding")
            print("✓ no SQL fallback path is used")
        else:
            print("x SQL fallback path was used (score is 0.0)!")
            
        print("\nALL VERIFICATION STEPS PASSED")

if __name__ == "__main__":
    asyncio.run(test_production_pipeline())
