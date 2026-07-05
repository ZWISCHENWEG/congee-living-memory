import sys
sys.path.append('Backend')

import os
from app.config import get_settings
from app.services.ai.factory import get_ai_provider
from app.services.ai.base import AIProviderUnavailableError

def reset_settings():
    get_settings.cache_clear()

# Test 1: No key
os.environ.pop('GEMINI_API_KEY', None)
reset_settings()
try:
    p = get_ai_provider()
    print("FAIL: Expected AIProviderUnavailableError but got provider")
except AIProviderUnavailableError:
    print("PASS: Raises without key")

# Test 2: With key
os.environ['GEMINI_API_KEY'] = 'test-key'
reset_settings()
try:
    p = get_ai_provider()
    if p.name == 'gemini':
        print("PASS: Returns GeminiProvider")
    else:
        print("FAIL: Returned wrong provider")
except Exception as e:
    print("FAIL: Exception raised:", e)
