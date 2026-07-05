# Chronos — Backend

FastAPI backend for **Chronos**, the Living Memory Engine: an autonomous
long-term memory layer for AI assistants (à la ChatGPT Memory), backed by Gemini
and SQLite.

## What it does

Every chat turn concurrently (a) retrieves the most relevant memories via
semantic search and (b) runs an **autonomous memory pipeline** that decides —
without user intervention — whether to create, update, deduplicate, resolve a
conflict on, or forget a memory.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (or `pip` + venv)
- A Gemini API key (optional — the app boots without one and degrades to
  keyword search / no generation)

## Project structure

```
Backend/
├── app/
│   ├── main.py                 # App factory, CORS, router wiring, lifespan
│   ├── config.py               # Pydantic-settings (env-driven, CHRONOS_* prefix)
│   ├── db.py                   # SQLite connection mgmt + idempotent migrations
│   ├── routes/                 # HTTP layer: root, health, memories, chat,
│   │                           #   search, memory_resolve
│   ├── schemas/                # Pydantic request/response models
│   └── services/
│       ├── ai/                 # AIProvider interface + Gemini impl + factory
│       ├── embedding/          # EmbeddingProvider interface + Gemini + null
│       ├── memory_repository/  # Persistence interface + SQLite impl
│       ├── search_backends/    # SearchBackend interface + SQLite (cosine)
│       ├── chat.py             # Orchestrates retrieve → generate ‖ auto-memory
│       ├── auto_memory.py      # Autonomous create/update/dedup/conflict/forget
│       ├── memory_extraction.py# Gemini classifier + conflict adjudication
│       ├── memory.py           # Memory CRUD + embedding orchestration
│       ├── search.py           # Semantic search + keyword fallback
│       └── prompt_builder.py   # Deterministic prompt assembly
├── tests_mock.py               # Deterministic Mock AI/Embedding providers
├── test_*.py                   # Mock-driven pipeline tests (8, all passing)
└── pyproject.toml
```

### Architecture notes

- **Provider-agnostic:** routes/services depend only on the `AIProvider`,
  `EmbeddingProvider`, `SearchBackend`, and `MemoryRepository` interfaces. Swap
  Gemini for OpenAI/Ollama at the factory/composition root — no business-logic
  changes. Errors are wrapped in `AIProviderError` so no vendor SDK leaks out.
- **Resilient by design:** the memory pipeline (`auto_memory.process`) never
  raises into the chat flow — any failure logs and degrades to `ignored`.
- **Concurrent turn:** `chat.py` runs generation and the memory pipeline under a
  single `asyncio.gather`, so memory bookkeeping adds no latency to the reply.

## Setup & run

```bash
# 1. Create your local env file and add your key
cp .env.example .env          # then set GEMINI_API_KEY=...

# 2. Install deps
uv sync                        # or: pip install -e .

# 3. Run (auto-reload)
uv run uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000 · Interactive docs: http://127.0.0.1:8000/docs

## Endpoints

| Method | Path                        | Purpose                                   |
| ------ | --------------------------- | ----------------------------------------- |
| GET    | `/`                         | Liveness banner                           |
| GET    | `/health`                   | Health check                              |
| GET    | `/memories`                 | Paginated list (`page`, `limit`, `search`)|
| POST   | `/memory`                   | Manually ingest a memory                  |
| DELETE | `/memory/{id}`              | Delete a memory                           |
| POST   | `/memory/resolve-conflict`  | Apply/reject a pending conflict           |
| POST   | `/chat`                     | Chat + autonomous memory pipeline         |
| GET    | `/search`                   | Semantic search (`q`) w/ keyword fallback |

Full request/response shapes: [`../docs/API_CONTRACT.md`](../docs/API_CONTRACT.md).

## Testing & quality

```bash
uv run pytest -q          # 8 deterministic, mock-backed tests (no network)
uv run ruff check .       # lint
uv run ruff format --check .
```

Tests inject `MockAIProvider` / `MockEmbeddingProvider` (`tests_mock.py`) so the
full create/update/dedup/conflict/forget pipeline is verified without hitting
Gemini or the network.

## Configuration

All settings are env-driven (`CHRONOS_*` prefix), except the Gemini credentials
which use the standard unprefixed names. See `.env.example`. Key knobs:

| Var                        | Default             | Meaning                             |
| -------------------------- | ------------------- | ----------------------------------- |
| `GEMINI_API_KEY`           | *(unset)*           | Enables generation + embeddings     |
| `GEMINI_MODEL`             | `gemini-2.5-flash`  | Chat model                          |
| `CHRONOS_DATABASE_URL`     | `sqlite:///./chronos.db` | SQLite path                    |
| `CHRONOS_CORS_ORIGINS`     | `localhost:5173,3000` | Allowed frontend origins          |
| `CHRONOS_SIMILARITY_THRESHOLD` | `0.65`          | Min cosine for a semantic hit       |
| `CHRONOS_DUPLICATE_THRESHOLD`  | `0.92`          | Dedup trigger                       |
| `CHRONOS_CONFLICT_THRESHOLD`   | `0.75`          | Conflict/update trigger             |
