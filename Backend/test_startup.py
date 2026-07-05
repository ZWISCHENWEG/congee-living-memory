def test_startup():
    import os

    from app.config import get_settings

    settings = get_settings()
    print(f"CWD: {os.getcwd()}")
    print(f"Loaded Gemini model: {settings.gemini_model}")
    print(f"Gemini configured: {settings.gemini_configured}")
    if settings.gemini_api_key:
        # Print first 4 and last 4 chars to be safe
        key = settings.gemini_api_key
        safe_key = f"{key[:4]}********{key[-4:]}" if len(key) > 8 else "True"
        print(f"API key exists: {safe_key}")
    else:
        print("API key exists: False")
