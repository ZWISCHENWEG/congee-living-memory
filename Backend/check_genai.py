import asyncio
from google import genai
from google.genai import errors

async def main():
    print(dir(genai.Client))
    client = genai.Client(api_key="FAKE")
    print(dir(client.aio.models))
    print(dir(errors))
    
asyncio.run(main())
