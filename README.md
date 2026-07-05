<div align="center">

# 🧠 Congee — Chronos Memory Engine

**An autonomous long-term memory engine for AI assistants.**
Chronos *decides on its own* what to remember, update, deduplicate, reconcile, and forget — no buttons, no manual tagging. Just talk to it.

`FastAPI` · `SQLite` · `Gemini` · `React 19` · `TypeScript`

</div>

---

## Why it matters

LLMs forget everything the moment a conversation ends. Bolt-on "memory" features
usually just dump raw messages into a vector store. **Chronos treats memory as an
active subsystem:** every message is classified, embedded, and reconciled against
what's already known — so the assistant's knowledge of you *evolves* instead of
just accumulating.

> You say *"I live in Ahmedabad."* → remembered.
> Later: *"Actually, I moved to Surat."* → Chronos detects the **conflict**, asks
> Gemini whether it's the same fact updated, and **supersedes** the old memory.
> Ask *"Forget my address"* → it finds the closest match semantically and removes it.

## Core capabilities

| # | Feature | How |
| - | ------- | --- |
| 1 | **Automatic extraction** | Gemini classifies each message into `save` / `forget` / `none` and normalizes it to a clean first-person fact. |
| 2 | **Typed & scored** | Every memory gets one of 12 categories + an importance score. |
| 3 | **Semantic embeddings** | 3072-dim Gemini embeddings stored per memory. |
| 4 | **Duplicate detection** | High similarity **and** normalized-text equality → skip. |
| 5 | **Update in place** | Similar-but-different fact about the same attribute → replace. |
| 6 | **Conflict resolution** | Gemini adjudicates; low-confidence conflicts surface to the user for confirmation. |
| 7 | **Natural forgetting** | "Forget X" is matched semantically, not by keyword. |
| 8–9 | **Usage & recency tracking** | Retrieved memories bump `usage_count` / `last_accessed`. |
| 10 | **Search** | Semantic search with automatic keyword (`LIKE`) fallback. |
| 11 | **Composite ranking** | Retrieval blends similarity + importance + recency + usage. |
| — | **Async & resilient** | Memory pipeline runs *concurrently* with reply generation and never breaks the chat. |

## Architecture

```
┌──────────────┐   HTTP    ┌───────────────────────────── FastAPI backend ─────────────────────────────┐
│  React 19 UI │  /api ──▶ │                                                                            │
│  (Vite proxy)│           │  routes/ ──▶ services/                                                     │
└──────────────┘           │             ├─ chat.py ──── asyncio.gather ─┬─▶ AIProvider ── Gemini       │
                           │             │                               └─▶ AutoMemoryService         │
                           │             │                                     │                        │
                           │             │   extract → dedup → conflict → save/update/forget            │
                           │             │        │            │                                        │
                           │             │  MemoryExtraction  SearchService ── EmbeddingProvider(Gemini)│
                           │             │  (Gemini classify)  (cosine + composite rank)                │
                           │             └─────────────┬───────────────────────────────────────────────┘
                           │                     MemoryRepository / SearchBackend                       │
                           │                              │                                             │
                           │                          SQLite (chronos.db)                               │
                           └────────────────────────────────────────────────────────────────────────────┘
```

**Everything behind an interface.** `AIProvider`, `EmbeddingProvider`,
`SearchBackend`, and `MemoryRepository` are abstract — Gemini/SQLite are just the
default implementations, swappable at the factory with zero business-logic
changes. No vendor SDK leaks past the service boundary.

### One chat turn

```
user message
     │
     ├─▶ SearchService.search ─▶ embed query ─▶ cosine over memories ─▶ composite rank ─▶ top-5
     │         (mark retrieved memories as used)                                          │
     │                                                                                    ▼
     │                                                                        PromptBuilder.build
     │                                                                                    │
     └─▶ asyncio.gather ┬─▶ AIProvider.generate(prompt) ─────────────────────────────────┴─▶ reply
                        │
                        └─▶ AutoMemoryService.process
                               │  classify (Gemini)
                               ├─ action=none   ─▶ ignored
                               ├─ action=forget ─▶ semantic match ≥ forget_threshold ─▶ delete
                               └─ action=save   ─▶ find_similar
                                       ├─ ≥ duplicate_threshold & same text ─▶ duplicate
                                       ├─ ≥ conflict_threshold ─▶ Gemini decides ─▶ update | conflict
                                       └─ else ─▶ create
```

### Database schema (`memories`)

| Column | Type | Notes |
| ------ | ---- | ----- |
| `id` | TEXT PK | `mem_<12 hex>` |
| `content` | TEXT | the normalized fact |
| `created_at` | TEXT | ISO-8601 UTC |
| `tags` | TEXT | JSON array |
| `embedding` | TEXT | JSON float array (3072-dim) |
| `type` | TEXT | one of 12 categories |
| `importance` | REAL | 0.0–1.0 |
| `usage_count` | INTEGER | retrieval counter |
| `last_accessed` | TEXT | ISO-8601 UTC |
| `updated_at` | TEXT | set on supersede |

Phase-3 columns are added by **idempotent** `ALTER TABLE` migrations in
`db.py:init_db()` — safe to re-run against an existing database.

## Quick start

**Backend** (`http://127.0.0.1:8000`, docs at `/docs`):
```bash
cd Backend
cp .env.example .env          # set GEMINI_API_KEY=...
uv sync
uv run uvicorn app.main:app --reload
```

**Frontend** (`http://localhost:5173`):
```bash
cd Frontend
cp .env.example .env          # leave VITE_API_URL unset for local dev (uses /api proxy)
npm install
npm run dev
```

## Testing & quality

```bash
cd Backend
uv run pytest -q              # 8 deterministic tests, fully mocked — no network
uv run ruff check .           # lint
uv run ruff format --check .  # format
```

Tests inject `MockAIProvider` / `MockEmbeddingProvider` so the entire
create/update/dedup/conflict/forget pipeline is verified without touching Gemini.

## Tech stack

- **Backend:** FastAPI · Pydantic v2 · SQLite (`sqlite3`) · `google-genai` · Ruff · Pytest
- **Frontend:** React 19 · TypeScript · Vite 8 · TanStack Query · Base UI · Tailwind v4 · Zustand · Zod

## API

See [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) for full request/response
shapes. Endpoints: `GET /`, `GET /health`, `GET /memories`, `POST /memory`,
`DELETE /memory/{id}`, `POST /memory/resolve-conflict`, `POST /chat`, `GET /search`.

## Known limitations & roadmap

- **Single-user / no auth.** All routes are public — intended for a local demo.
  `fastapi-users` + Bearer tokens are the next step.
- **Similarity is computed in Python** over all rows per query — perfect for a
  demo dataset, O(N·D) at scale. Swap `SearchBackend` for `sqlite-vec` / a vector
  DB when memory count grows.
- **No rate limiting** on the Gemini-backed endpoints.
- **Prompt-injection surface:** user text flows into classifier/chat prompts; the
  classifier output is schema-validated, which contains the blast radius.

## Repository layout

```
Congee/
├── Backend/     # FastAPI memory engine (see Backend/README.md)
├── Frontend/    # React + TS client
├── docs/        # API contract + coding standard
├── spike/       # Research spikes (Cognee bridge-concept experiment)
└── PRD_Chronos.md
```
