import asyncio
import sys
import logging
from httpx import ASGITransport, AsyncClient
sys.path.append('.')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def run():
    from app.main import app
    from app.db import session, init_db
    from app.config import get_settings
    
    get_settings.cache_clear()
    init_db()
    with session() as conn:
        conn.execute("DELETE FROM memories")
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n--- POSTing Memory ---")
        resp = await client.post("/memory", json={"content": "My favorite programming language is Python.", "tags": ["coding"]})
        assert resp.status_code == 201
        
        print("\n--- GETting Search ---")
        resp = await client.get("/search?q=what language do i like")
        print("Search Response:", resp.json())

if __name__ == "__main__":
    asyncio.run(run())
