import requests
import json
import os
import sys

URL = "http://127.0.0.1:8000/chat"
headers = {"Content-Type": "application/json"}
payload = {"message": "Hello", "conversation_id": "test_conv"}

# Test 1: No API key (should be 503)
print("--- Test 1: No API Key ---")
try:
    resp = requests.post(URL, json=payload)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
    if resp.status_code != 503:
        sys.exit(1)
except Exception as e:
    print("Error:", e)
    sys.exit(1)

print("PASS: 503 received.")

