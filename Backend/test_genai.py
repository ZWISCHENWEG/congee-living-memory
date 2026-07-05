import asyncio
from google import genai
from google.genai import errors
from google.genai import types

async def main():
    print("--- errors ---")
    print([e for e in dir(errors) if not e.startswith('_')])
    
    # We will instantiate a dummy response
    # to see its attributes and serialization methods.
    try:
        from google.genai.types import GenerateContentResponse
        print("--- GenerateContentResponse methods ---")
        print([m for m in dir(GenerateContentResponse) if not m.startswith('_')])
    except ImportError as e:
        print("ImportError:", e)
        print("--- types ---")
        print([t for t in dir(types) if not t.startswith('_')])
        
asyncio.run(main())
