import asyncio
import os
import sys

sys.path.append('Backend')

from app.config import get_settings
from app.schemas.chat import ChatRequest
from app.routes.chat import handle_chat
from fastapi import HTTPException

import logging
logging.basicConfig(level=logging.ERROR)

async def test_no_key():
    get_settings.cache_clear()
    if 'GEMINI_API_KEY' in os.environ:
        del os.environ['GEMINI_API_KEY']
    
    req = ChatRequest(message="Hello", conversation_id="123")
    try:
        await handle_chat(req)
        print("FAIL: No key test expected HTTPException")
        sys.exit(1)
    except HTTPException as e:
        if e.status_code == 503 and e.detail == "AI service is currently unavailable.":
            print("PASS: 503 without leaking details")
        else:
            print("FAIL: No key test got wrong HTTP response", e.status_code, e.detail)
            sys.exit(1)

async def test_fake_key():
    get_settings.cache_clear()
    os.environ['GEMINI_API_KEY'] = 'fake_key'
    
    req = ChatRequest(message="Hello", conversation_id="123")
    try:
        await handle_chat(req)
        print("FAIL: Fake key test expected HTTPException")
        sys.exit(1)
    except HTTPException as e:
        if e.status_code == 502 and e.detail == "AI generation failed. Please try again later.":
            print("PASS: 502 without leaking details")
        else:
            print("FAIL: Fake key test got wrong HTTP response", e.status_code, e.detail)
            sys.exit(1)

async def main():
    await test_no_key()
    await test_fake_key()

asyncio.run(main())
