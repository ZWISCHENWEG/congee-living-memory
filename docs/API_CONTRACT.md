# Congee API Contract

## Overview
This document defines the API contract between the Chronos (FastAPI backend) and
the Congee frontend. It reflects the **implemented** behaviour of `Backend/app`.

## Base URL
No version prefix. Endpoints are mounted at the backend root, e.g.
`http://127.0.0.1:8000/chat`. In development the Vite dev server proxies
`/api/*` → `http://127.0.0.1:8000/*` (see `Frontend/vite.config.ts`).

## Authentication
None. All routes are currently public — the engine is a single-user demo.
Auth (Bearer tokens / `fastapi-users`) is on the roadmap; see "Known limitations".

---

## Endpoints

### System

#### `GET /`
Basic liveness / project banner.
- **Response `200 OK`:**
  ```json
  { "project": "Chronos", "status": "running" }
  ```

#### `GET /health`
Health check.
- **Response `200 OK`:**
  ```json
  { "status": "ok", "version": "1.0.0" }
  ```

### Memories

#### `GET /memories`
Retrieve a paginated list of memories (newest first).
- **Query Params:** `page` (int, default 1), `limit` (int, default 20), `search` (string, optional; SQL `LIKE` on content)
- **Response `200 OK`:**
  ```json
  {
    "data": [
      {
        "id": "mem_1a2b3c4d5e6f",
        "content": "My favorite language is Python.",
        "created_at": "2026-07-05T10:00:00+00:00",
        "tags": ["coding"],
        "type": "preference",
        "importance": 0.75,
        "usage_count": 3,
        "last_accessed": "2026-07-05T12:00:00+00:00",
        "updated_at": null
      }
    ],
    "meta": { "total": 1, "page": 1, "limit": 20 }
  }
  ```

#### `POST /memory`
Manually ingest a new memory. Generates and stores an embedding.
- **Request Body:** (`type` and `importance` optional; default to `"other"` / `0.5`)
  ```json
  { "content": "string", "tags": ["string"], "type": "preference", "importance": 0.75 }
  ```
- **Response `201 Created`:** a single `MemorySchema` (same shape as an item in `GET /memories`).

#### `DELETE /memory/{id}`
Delete a memory by ID.
- **Response `204 No Content`** (idempotent — no error if the id is absent).

#### `POST /memory/resolve-conflict`
Resolve a pending conflict surfaced by a chat turn whose `memory_action.status == "conflict"`.
- **Request Body:**
  ```json
  {
    "existing_id": "mem_1a2b3c4d5e6f",
    "new_content": "I moved to Surat.",
    "decision": "replace",           // or "keep"
    "type": "location",
    "importance": 0.85
  }
  ```
- **Response `200 OK`:** a `MemoryAction` (`status` = `"updated"` on replace, `"ignored"` on keep).
- **Errors:** `404 Not Found` if `existing_id` no longer exists.

### Chat

#### `POST /chat`
Send a message. The backend retrieves relevant memories, generates a reply, and
**concurrently** runs the autonomous memory pipeline (extract → dedup →
conflict/update/insert/forget).
- **Request Body:**
  ```json
  { "message": "What language do I like?", "conversation_id": "conv_123" }
  ```
  `conversation_id` is optional; one is generated if omitted.
- **Response `200 OK`:**
  ```json
  {
    "response": "You like Python.",
    "used_memories": [
      { "id": "mem_1a2b3c4d5e6f", "content": "My favorite language is Python.", "score": 0.91 }
    ],
    "conversation_id": "conv_123",
    "memory_action": {
      "status": "created",
      "memory": "My favorite language is Python.",
      "memory_id": "mem_1a2b3c4d5e6f",
      "type": "preference",
      "importance": 0.75,
      "detail": null
    }
  }
  ```
  `memory_action.status` ∈ `created | updated | duplicate | conflict | deleted | ignored`.
- **Errors:** `503` if no AI provider is configured; `502` if generation fails upstream.

### Search

#### `GET /search`
Semantic search over memories, with keyword (`LIKE`) fallback when embeddings are
unavailable.
- **Query Params:** `q` (string, required, min length 1)
- **Response `200 OK`:**
  ```json
  {
    "results": [
      { "id": "mem_1a2b3c4d5e6f", "content": "My favorite language is Python.", "score": 0.95 }
    ]
  }
  ```
  `score` is the composite rank for semantic hits, or `0.0` for keyword-fallback hits.

---

## Error format
Errors use FastAPI's default envelope:
```json
{ "detail": "AI service is currently unavailable." }
```
Validation errors (`422`) return FastAPI's structured `detail` array.
