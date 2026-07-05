# Congee API Contract

## Overview
This document defines the strict API contract between the Chronos (FastAPI backend) and the Congee frontend. Both the frontend and backend teams must adhere to these specifications.

## Base URL
`/api/v1` (Relative to backend URL, e.g., `http://127.0.0.1:8000/api/v1`)

## Authentication
All protected routes require a Bearer token in the `Authorization` header:
`Authorization: Bearer <token>`

---

## State Transition Flow (UI)
Every endpoint must handle the following UI state transitions on the frontend:
`Request` -> `Loading (Skeleton)` -> `Success (Data)` -> `Empty (Empty State)` -> `Error (Toast/Boundary)` -> `Unauthorized (Redirect)` -> `Retry`

---

## Endpoints

### System

#### `GET /health`
Check API health status.
- **Request Body:** None
- **States:** Loading -> Success -> Error -> Retry
- **Response:** `200 OK`
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

### Memories

#### `GET /memories`
Retrieve a paginated list of memories.
- **Query Params:**
  - `page` (int, default: 1)
  - `limit` (int, default: 20)
  - `search` (string, optional)
- **States:** Loading -> Skeleton -> Success -> Cards -> No Memories -> Empty State -> 500 -> Toast -> Retry
- **Response:** `200 OK`
  ```json
  {
    "data": [
      {
        "id": "mem_123",
        "content": "Had a great meeting about the new AI features.",
        "created_at": "2026-07-05T10:00:00Z",
        "tags": ["meeting", "ai"]
      }
    ],
    "meta": {
      "total": 1,
      "page": 1,
      "limit": 20
    }
  }
  ```

#### `POST /memory`
Ingest a new memory.
- **Request Body:**
  ```json
  {
    "content": "string",
    "tags": ["string"] // optional
  }
  ```
- **States:** Loading (Optimistic UI) -> Success -> Error (Rollback) -> Toast -> Retry
- **Response:** `201 Created`
  ```json
  {
    "id": "mem_124",
    "content": "string",
    "created_at": "2026-07-05T10:15:00Z",
    "tags": ["string"]
  }
  ```

#### `DELETE /memory/{id}`
Delete a memory by ID.
- **Request Params:** `id` (string)
- **States:** Loading (Optimistic UI) -> Success -> Error (Rollback) -> Toast -> Retry
- **Response:** `204 No Content`

### Chat

#### `POST /chat`
Send a message to the AI and receive a response, potentially creating or retrieving memories in the background.
- **Request Body:**
  ```json
  {
    "message": "What did we discuss about AI features?",
    "conversation_id": "conv_123" // optional
  }
  ```
- **States:** Loading (Typing indicator) -> Success (Message Bubble) -> Error -> Toast -> Retry
- **Response:** `200 OK`
  ```json
  {
    "id": "msg_456",
    "reply": "You discussed the new AI features earlier today.",
    "conversation_id": "conv_123",
    "referenced_memories": ["mem_123"]
  }
  ```

### Search

#### `GET /search`
Perform a semantic search across memories.
- **Query Params:** `q` (string)
- **States:** Loading -> Skeleton -> Success -> Results -> No Results -> Empty State -> Error -> Toast
- **Response:** `200 OK`
  ```json
  {
    "results": [
      {
        "id": "mem_123",
        "content": "Had a great meeting about the new AI features.",
        "score": 0.95
      }
    ]
  }
  ```

---
## Error Format
All errors will follow this standard format:
- **Response:** `400 / 401 / 403 / 404 / 422 / 500`
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Invalid request parameters",
      "details": {
        "content": "Field is required"
      }
    }
  }
  ```
