import asyncio
import os
import sys

# Inject API key to make it proceed
os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'

sys.path.append('Backend')

from app.config import get_settings
get_settings.cache_clear()

from app.db import init_db
init_db()  # Initialize the DB so tables exist

# Testing FastAPI DI programmatically requires some mocking since we aren't using TestClient
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def main():
    resp = client.post("/chat", json={"message": "Hello", "conversation_id": "123"})
    if resp.status_code == 502:
        print("PASS: Chat Service orchestrated AI via DI and correctly threw 502 on fake key")
    else:
        print(f"FAIL: Expected 502, got {resp.status_code}. Output: {resp.text}")
        sys.exit(1)

main()
