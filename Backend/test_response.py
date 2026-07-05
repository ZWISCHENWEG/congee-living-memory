import asyncio
from google import genai
from google.genai import types

async def main():
    # Construct empty response
    resp = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                finish_reason="SAFETY",
                content=types.Content(parts=[])
            )
        ]
    )
    
    try:
        t = resp.text
        print("Text:", t)
    except Exception as e:
        print("Text Error:", type(e), e)
        
    try:
        print("Dict:", resp.model_dump(mode="json"))
    except Exception as e:
        print("model_dump error:", type(e), e)

asyncio.run(main())
