# Phase 3 — Autonomous Long-Term Memory Engine

Chronos now behaves like ChatGPT Memory: memories are created, updated,
deduplicated, and forgotten **automatically during conversation**. A client
never needs to call `POST /memory` — everything happens inside `/chat`.

This document covers the architecture, flow, database changes, API surface,
example requests/responses, test results, and future improvements.

---

## 1. Architecture

Phase 3 is **additive**. No completed Phase 1/2 file was rewritten; existing
classes, endpoints, DI factories, embeddings, and the prompt builder are
unchanged. New services layer on top of the existing provider-agnostic
abstractions (`AIProvider`, `EmbeddingProvider`, `MemoryRepository`,
`SearchBackend`).

```
                         ┌─────────────────────────────────────────────┐
   POST /chat  ─────────▶│                ChatService                   │
                         │  1. SearchService.search      (retrieval)    │
                         │  2. MemoryService.mark_used    (usage/access)│
                         │  3. PromptBuilder.build                      │
                         │  4. asyncio.gather(                          │
                         │        AIProvider.generate,   ← reply        │
                         │        AutoMemoryService.process ← memory    │
                         │     )                                        │
                         └───────────────┬──────────────────────────────┘
                                         │
                                         ▼
                         ┌─────────────────────────────────────────────┐
                         │             AutoMemoryService                │
                         │  classify → dedup → conflict/update → insert │
                         │           └────────────────────→ forget      │
                         └───┬─────────────────┬──────────────────┬─────┘
                             │                 │                  │
                  MemoryExtractionService  SearchService     MemoryService
                   (Gemini classify /      (raw-cosine       (create / update /
                    conflict decision)      similarity)       delete / mark_used)
                             │                 │                  │
                        AIProvider       SearchBackend      MemoryRepository
                         (Gemini)         (SQLite cosine)     (SQLite)
```

### New components
| File | Responsibility |
|---|---|
| `app/schemas/memory_engine.py` | Engine value objects: `MemoryExtraction`, `MemoryAction`, `ConflictDecision`, `ConflictResolution`, `MemoryCategory`. |
| `app/services/memory_extraction.py` | `MemoryExtractionService` — Gemini-backed message classification (save/forget/none) and conflict adjudication. JSON-only, robust parsing, never raises. |
| `app/services/auto_memory.py` | `AutoMemoryService` — orchestrates extract → dedup → conflict/update → insert / forget. Resilient (never breaks chat). |
| `app/routes/memory_resolve.py` | `POST /memory/resolve-conflict` — frontend confirmation for pending conflicts (Feature 6 tail). |

### Design principles honoured
- **SOLID / separation of concerns:** classification (extraction), matching
  (search), persistence (memory), and orchestration (auto-memory) are distinct
  services, each behind a factory for DI.
- **No duplicated logic:** cosine scoring lives once in `SQLiteSearchBackend` and
  is reused by both chat retrieval (`search`) and engine matching
  (`similarity_search`); embedding lives once in `MemoryService._embed`.
- **Backwards compatible:** every schema addition is optional; every new repo
  argument has a default; existing endpoints keep their contracts.

---

## 2. Flow diagram (per user message)

```
User message
   │
   ├─▶ Search memories (semantic → composite rank) ──▶ used_memories
   │        └─▶ mark_used(): usage_count++, last_accessed = now      [F8, F9]
   │
   ├─▶ Build prompt + generate reply (Gemini)                        [Phase 2]
   │
   └─▶ AutoMemoryService.process()                                   [Phase 3]
         │
         ├─ classify (Gemini, JSON only)                             [F1, F2, F3]
         │     action ∈ {save, forget, none}
         │
         ├─ none  ────────────────────────────────▶ status=ignored
         │
         ├─ forget ─▶ find_similar(target)
         │              └─ best ≥ forget_threshold ─▶ delete ─▶ deleted   [F7]
         │              └─ else                     ─▶ ignored
         │
         └─ save  ─▶ find_similar(fact)  (raw cosine)                 [F4]
                       ├─ near-identical (≥dup_thr & text match) ─▶ duplicate
                       ├─ similar (≥conflict_thr):                   [F5, F6]
                       │     decide_conflict (Gemini)
                       │       replace & conf > 0.90 ─▶ update ─▶ updated
                       │       else                  ─▶ conflict (pending)
                       └─ otherwise ─▶ insert ─▶ created
```

All steps emit INFO logs (Feature 12); no failure is silent.

---

## 3. Database changes (Feature 10)

Applied idempotently in `app/db.py::init_db()` via `ALTER TABLE ... ADD COLUMN`
(the same safe pattern used for the existing `embedding` column). **No user data
is deleted or migrated destructively.**

| Column | Type | Default | Purpose |
|---|---|---|---|
| `type` | TEXT | `'other'` | Memory category (Feature 2). |
| `importance` | REAL | `0.5` | Importance score 0.0–1.0 (Feature 3). |
| `usage_count` | INTEGER | `0` | Times retrieved (Feature 8). |
| `last_accessed` | TEXT | `NULL` | ISO timestamp of last retrieval (Feature 9). |
| `updated_at` | TEXT | `NULL` | ISO timestamp of last in-place update. |

Resulting schema:
```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    tags TEXT,
    embedding TEXT,
    type TEXT DEFAULT 'other',
    importance REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    last_accessed TEXT,
    updated_at TEXT
);
```

---

## 4. Search ranking (Feature 11)

Chat retrieval keeps the existing cosine **similarity threshold filter**
unchanged (which memories qualify), then **re-ranks** the qualifying set by a
composite score:

```
score = 0.60·similarity + 0.20·importance + 0.10·recency + 0.10·usage_norm
```

- `similarity` — cosine, clamped to [0, 1].
- `importance` — stored value (default 0.5).
- `recency` — age decay `1 / (1 + age_days)` ∈ (0, 1].
- `usage_norm` — `usage_count / max(usage_count in result set)`.

Weights are configurable in `app/config.py`. The LIKE fallback path is
unchanged. Duplicate/conflict/forget matching deliberately uses **raw cosine**
(`SearchBackend.similarity_search`), not the composite, because those thresholds
are calibrated against pure similarity.

---

## 5. API changes

### `POST /chat` (unchanged request; response gains one optional field)
`ChatResponse` now includes an optional `memory_action` (defaults `null`, so
existing clients are unaffected):

```jsonc
{
  "response": "Understood, Prince. I'll remember that.",
  "used_memories": [ { "id": "mem_...", "content": "...", "score": 0.87 } ],
  "conversation_id": "conv_...",
  "memory_action": {                     // NEW, optional
    "status": "created",                 // created|updated|duplicate|conflict|deleted|ignored
    "memory": "My name is Prince.",
    "memory_id": "mem_96d0a1cdc792",
    "type": "identity",
    "importance": 1.0,
    "detail": null
  }
}
```

### `POST /memory/resolve-conflict` (new)
Confirms or rejects a pending conflict returned by a chat turn.

```jsonc
// request
{
  "existing_id": "mem_...",
  "new_content": "My favorite color is green.",
  "decision": "replace",                 // "replace" | "keep"
  "type": "preference",
  "importance": 0.75
}
// response  -> MemoryAction  (status "updated" on replace, "ignored" on keep)
```

### Existing endpoints — unchanged contracts
`GET /memories`, `POST /memory`, `DELETE /memory/{id}`, `POST /search`,
`GET /health`, `/`. (`GET /memories` and `POST /memory` now also carry the
optional Phase 3 metadata fields.)

---

## 6. Example chat session

| # | User says | `memory_action.status` | Effect |
|---|---|---|---|
| 1 | "My name is Prince." | `created` | New `identity` memory, importance 1.0 |
| 2 | "How are you?" | `ignored` | Chit-chat, nothing stored |
| 3 | "My favorite language is Python." | `created` | New `preference` memory |
| 4 | "My favorite language is Python." | `duplicate` | No second copy |
| 5 | "I live in Ahmedabad." | `created` | New `location` memory |
| 6 | "I moved to Surat." | `updated` | Same memory, content → Surat |
| 7 | "Actually my favorite color is green." (vs stored blue, low confidence) | `conflict` | Pending; frontend confirms via resolve-conflict |
| 8 | "Forget that I like Python." | `deleted` | Matching memory removed |

---

## 7. Test results

Automated tests (standalone `httpx.AsyncClient` scripts hitting real Gemini),
one per feature:

| Test | Feature | Asserts |
|---|---|---|
| `test_auto_memory.py` | 1 — auto extraction | fact → `created` (identity); chit-chat → `ignored`; 1 row stored |
| `test_duplicate_memory.py` | 4 — duplicate detection | same fact twice → 2nd is `duplicate`; 1 row |
| `test_memory_update.py` | 5 — update | "moved to Surat" → `updated`, same id, `updated_at` set, 1 row |
| `test_forget_memory.py` | 7 — forgetting | "forget I like Python" → `deleted`; 0 rows |
| `test_conflict_memory.py` | 6 — conflict + resolve | conflicting value → `conflict`; resolve-conflict `replace` → `updated` |

Regression (Phase 1/2): `test_chat_memory.py`, `test_semantic_fallback.py` pass
unchanged (schema additions are optional).

> **Note on the free-tier quota:** `gemini-2.5-flash` free tier allows only
> **5 `generate_content` requests/minute**. Each chat turn makes 2–3 such calls
> (reply + classify [+ conflict]). Run the tests spaced ~75s apart (as in
> `phase3_test_results.log`) or on a paid tier to avoid `429 RESOURCE_EXHAUSTED`.
> When quota is hit, the memory subsystem degrades gracefully to `ignored`
> (classification failure is swallowed); only the Phase 2 reply generation
> surfaces the upstream error as `502`, exactly as before Phase 3.

---

## 8. Future improvements
- **Background extraction:** move `AutoMemoryService.process` to a fire-and-forget
  task/queue so memory writes never share the request's latency budget.
- **Batch/consolidate:** periodically merge fragmented memories and decay
  importance of stale, unused facts.
- **Vector index:** replace the in-Python cosine scan with `sqlite-vec`/FAISS for
  O(log n) retrieval at scale.
- **Provider-agnostic structured output:** use native JSON/function-calling modes
  where the provider supports them, instead of prompt-enforced JSON.
- **Per-user partitioning:** scope memories by user/tenant id.
- **Retry/backoff** on transient `429`/`503` in the AI provider for smoother
  free-tier behaviour.
