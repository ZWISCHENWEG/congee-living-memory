import asyncio
import os
import sys

# Inject API key to make it proceed
os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'

sys.path.append('Backend')

from app.config import get_settings
get_settings.cache_clear()

from app.schemas.chat import ChatRequest
from app.routes.chat import handle_chat
from fastapi import HTTPException

async def main():
    req = ChatRequest(message="Hello", conversation_id="123")
    try:
        resp = await handle_chat(req)
        print("FAIL: Expected 502 with fake key, but got success")
        sys.exit(1)
    except HTTPException as e:
        if e.status_code == 502:
            print("PASS: Chat Service orchestrated AI and correctly threw 502 on fake key")
        else:
            print("FAIL: Chat Service threw wrong exception:", e.status_code)
            sys.exit(1)

asyncio.run(main())
