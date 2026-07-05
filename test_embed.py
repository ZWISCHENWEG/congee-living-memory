import asyncio
import os
from google import genai

os.environ['GEMINI_API_KEY'] = 'fake_key'

async def main():
    client = genai.Client()
    try:
        response = await client.aio.models.embed_content(
            model='text-embedding-004',
            contents="Hello world"
        )
        print("Embed success")
    except Exception as e:
        print("Embed failed:", type(e), e)

asyncio.run(main())
