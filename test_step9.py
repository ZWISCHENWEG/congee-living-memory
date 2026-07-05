import asyncio
import os
import sys
import json
import sqlite3

# Inject API key to make it proceed
os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'

sys.path.append('Backend')

from app.config import get_settings
get_settings.cache_clear()

from app.db import init_db, get_connection
init_db()  # Initialize the DB so tables and embedding column exist

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_db():
    conn = get_connection()
    # Clear for clean test
    conn.execute("DELETE FROM memories")
    
    # Insert memory without embedding
    conn.execute(
        "INSERT INTO memories (id, content, created_at) VALUES (?, ?, ?)",
        ("mem_1", "I love the color blue", "2024-01-01T00:00:00Z")
    )
    
    # Insert memory with valid embedding
    emb1 = json.dumps([1.0, 0.0, 0.0])
    conn.execute(
        "INSERT INTO memories (id, content, created_at, embedding) VALUES (?, ?, ?, ?)",
        ("mem_2", "I enjoy drinking tea", "2024-01-01T00:00:00Z", emb1)
    )
    
    # Insert memory with invalid dimensions (2 floats instead of 3 for testing)
    emb2 = json.dumps([1.0, 0.0])
    conn.execute(
        "INSERT INTO memories (id, content, created_at, embedding) VALUES (?, ?, ?, ?)",
        ("mem_3", "This is a dimension mismatch", "2024-01-01T00:00:00Z", emb2)
    )
    
    # Insert memory with invalid JSON
    conn.execute(
        "INSERT INTO memories (id, content, created_at, embedding) VALUES (?, ?, ?, ?)",
        ("mem_4", "Broken JSON embedding", "2024-01-01T00:00:00Z", "[1.0, broken]")
    )
    conn.commit()
    conn.close()

def main():
    setup_db()
    
    print("Testing semantic search route fallback (because GEMINI_API_KEY is fake)...")
    # Because Gemini API fails, it should fallback to LIKE
    resp = client.get("/search?q=blue")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    
    assert len(data['results']) > 0, "Fallback failed to find 'blue'"
    assert data['results'][0]['id'] == 'mem_1'
    print("✓ LIKE fallback works.")
    
    print("Testing Chat Route (will fail with 502 because gemini generate fails, but search succeeds)...")
    resp = client.post("/chat", json={"message": "I love the color blue"})
    assert resp.status_code == 502, f"Expected 502, got {resp.status_code}"
    print("✓ Chat route continues to orchestrate perfectly.")
    
    print("Testing internal SearchBackend logic directly...")
    from app.services.search_backends import SQLiteSearchBackend
    backend = SQLiteSearchBackend()
    
    # Simulate a query embedding [1.0, 0.0, 0.0]
    # It should perfectly match mem_2 (cosine=1.0) and ignore mem_3 (dim mismatch), mem_4 (invalid JSON)
    # mem_1 has NULL embedding, so it is ignored during semantic search phase.
    q_emb = [1.0, 0.0, 0.0]
    res = backend.search(query_embedding=q_emb, query_text="doesn't matter")
    assert len(res) == 1
    assert res[0].id == "mem_2"
    assert res[0].score == 1.0
    print("✓ Semantic search works.")
    print("✓ Dimension mismatch is ignored.")
    print("✓ Invalid JSON is ignored.")
    print("✓ NULL embeddings are ignored.")
    
    # Test threshold
    q_emb2 = [0.0, 1.0, 0.0] # orthogonal, cosine=0.0
    res2 = backend.search(query_embedding=q_emb2, query_text="tea")
    # since cosine=0.0 < 0.72 threshold, it should fallback and return mem_2 via LIKE!
    assert len(res2) == 1
    assert res2[0].id == "mem_2"
    assert res2[0].score == 0.0 # Score 0 indicates fallback was used
    print("✓ Threshold filters weak matches and triggers fallback.")

    print("ALL TESTS PASSED.")

main()
