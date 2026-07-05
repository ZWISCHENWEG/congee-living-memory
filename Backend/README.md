# Chronos — Backend

FastAPI backend for **Chronos**, the Living Memory Engine.

> This milestone is scaffolding only: a clean, scalable project structure with
> `/` and `/health` endpoints. No business logic, no Cognee, no auth yet.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) package manager

## Project structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app factory + entrypoint (`app`)
│   ├── config.py         # Pydantic v2 settings (env-driven)
│   ├── db.py             # SQLite connection management
│   ├── models/           # Persistence models (placeholder)
│   ├── schemas/          # Pydantic request/response schemas
│   ├── routes/           # API routers (root, health)
│   ├── services/         # Business logic layer (placeholder)
│   └── utils/            # Shared helpers (placeholder)
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

### Architecture notes

- **Clean layering:** `routes` (HTTP) → `services` (logic, later) → `models`/`db`
  (persistence). `schemas` holds the Pydantic v2 API contracts. `config` centralizes
  environment-driven settings.
- **App factory:** `create_app()` in `main.py` wires config, CORS, and routers, so
  the app is easy to test and extend.
- **Settings:** all env vars are prefixed `CHRONOS_` and validated by Pydantic v2.

## Setup & run

From the `backend/` directory:

```bash
# 1. (Optional) create your local env file
cp .env.example .env

# 2. Install dependencies and create the virtual environment
uv sync

# 3. Start the development server (auto-reload)
uv run uvicorn app.main:app --reload
```

The API is now available at http://127.0.0.1:8000

## Endpoints

| Method | Path       | Response                                   |
| ------ | ---------- | ------------------------------------------ |
| GET    | `/`        | `{"project": "Chronos", "status": "running"}` |
| GET    | `/health`  | `{"status": "healthy"}`                    |

Interactive API docs: http://127.0.0.1:8000/docs

## Verify

```bash
curl http://127.0.0.1:8000/
# {"project":"Chronos","status":"running"}

curl http://127.0.0.1:8000/health
# {"status":"healthy"}
```
