import asyncio
import os
import sys

# Inject a fake API key
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
        print("FAIL: Expected HTTPException")
        sys.exit(1)
    except HTTPException as e:
        if e.status_code == 502:
            print("PASS: 502 received for SDK error")
        else:
            print("FAIL: Expected 502, got", e.status_code)
            sys.exit(1)
    except Exception as e:
        print("FAIL: Unexpected error", e)
        sys.exit(1)

asyncio.run(main())
