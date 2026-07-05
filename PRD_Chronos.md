# Chronos — Product Requirements Document (PRD)

**Tagline (headline):** *The memory that remembers **why** your team made every decision — and rewrites itself when the reasoning changes.*
**Subtitle (demoted grand vision):** A Living Memory Engine, powered by Cognee.

**Hackathon:** WeMakeDevs × Cognee — *"Build AI that doesn't forget using Cognee."*
**Document status:** v1.0 — Build-ready. Discovery locked.
**Primary objective:** Win. Every decision in this doc is optimized against the six judging criteria.

---

## 0. TL;DR — What we are building in one paragraph

Chronos ingests two disjoint sources of project truth — **meeting transcripts** (the *why*) and **git commit history** (the *what*) — into Cognee's memory graph. Using a guided ontology, Cognee **synthesizes bridge concepts** (e.g. *"Improve Enterprise Conversion"*) that link a discussion to the code change it caused, **even when the two share no vocabulary**. A user asks *"Why was pricing removed?"* and Chronos reconstructs the full causal chain — Meeting → Decision → Business Concept → Commit → Deployment → Outcome — as a **living graph that animates the reasoning into existence**. When a later meeting reverses the decision, Chronos calls `forget()` to **supersede** (not delete) the old decision, preserving history while changing the current truth. The same question, asked again, returns an evolved answer.

**Without Cognee, this product does not exist.**

---

## 1. Product Vision

### 1.1 The problem
Freelance web developers and small agencies lose the **context of their own decisions**. A client asks *"Why did we remove the pricing section?"* and the answer is scattered across meetings, chats, docs, and commits — or lives only in a human memory that decays in weeks. Reconstructing the *why* costs 30–60 minutes per incident, erodes client trust, and is impossible to delegate.

### 1.2 The insight
The valuable artifact is not the document. It is the **reasoning** — the causal chain connecting a business concern to an implementation. Today, no tool stores reasoning. ChatGPT forgets at the context window boundary. Notion/RAG search retrieves the *what*, never the *why*. The only system that holds the "why" is the developer's brain, and it degrades.

### 1.3 The product
Chronos is a **decision-provenance engine**: a memory that stores *relationships and reasoning*, reconstructs the full "why" on demand, and **evolves** as reality changes. Memory connects itself (memify), and intentionally forgets by superseding outdated truth (forget).

### 1.4 Why now
Cognee makes graph-native, evolving memory a primitive (`remember`, `recall`, `memify`, `forget`) instead of a 6-month infrastructure project. Chronos is the first product to weaponize all four for decision archaeology.

### 1.5 Positioning
| Tool | What it remembers | What it forgets |
|---|---|---|
| ChatGPT | Nothing past the context window | Everything |
| Notion AI / RAG search | The *document* (the "what") | The *reasoning* (the "why") |
| Your brain | The "why" | Decays in weeks; can't be delegated |
| **Chronos** | **The "why", as an evolving graph** | **Only what it *chooses* to supersede** |

---

## 2. User Personas

### 2.1 Primary — "Arjun, the Solo Freelancer" (the demo persona)
- Full-stack freelance web developer, 3–4 concurrent clients.
- **Is** the PM, the developer, and the institutional memory — and the single point of failure.
- Pain: context-switching across clients; clients challenge past decisions weeks later; he re-derives the "why" manually.
- Success = never again lose a client's trust because he can't explain a past decision in under 10 seconds.

### 2.2 Secondary — "Maya, the 5-person Agency Lead"
- Runs delivery for a boutique agency; onboarding a new dev takes weeks because tribal knowledge is undocumented.
- Pain: decision history walks out the door when a contractor leaves.
- Success = organizational memory that survives team churn.

### 2.3 Tertiary (post-hackathon) — "The Client"
- Read-only stakeholder who can self-serve "why did we do X?" without a meeting.

> **Demo focuses exclusively on Arjun.** Maya and the client are roadmap, not MVP.

---

## 3. Unique Value Proposition & Differentiation

- **UVP:** *Chronos remembers why every decision was made — across sources that share no words — and rewrites itself when the reasoning changes.*
- **The moat that scores "Best Use of Cognee":** the **vocabulary-mismatch link**. Meeting says *"enterprise prospects hesitate at pricing tiers"*; commit says *"replace tier cards with Contact Sales CTA."* No shared keywords. Chronos links them through a **synthesized concept node**. This is provably *not* grep — it is graph-based memory reasoning.
- **The moat that scores "Creativity":** `forget()` reframed as **memory evolution / supersession**, not deletion — the counterintuitive twist in a hackathon literally themed *"AI that doesn't forget."*

---

## 4. MVP Scope

### 4.1 IN scope (must ship)
1. Ingest **meeting transcripts** (text/markdown) via `remember()`.
2. Ingest **git commit history** (JSON export or live `git log`) via `remember()`.
3. **Guided ontology** driving `memify()` to synthesize bridge concepts and cross-source edges.
4. **Causal recall**: `recall("why was X?")` returns a reconstructed chain with evidence citations.
5. **Living Graph (hero panel)**: animated causal-path illumination — the only panel that animates live.
6. **Memory evolution**: ingest a new meeting → `forget()` supersedes the prior decision → same query returns an evolved answer.
7. **Two supporting panels** (static/secondary): Decision Reconstruction (narrative + clickable evidence) and Timeline.

### 4.2 OUT of scope (explicitly deferred — say this out loud to judges)
- WhatsApp/Gmail/Slack/Figma/Jira integrations (roadmap; would add 9 OAuth failure modes).
- Multi-user auth, roles, permissions.
- Real-time transcript capture (we ingest finished transcripts).
- Mobile app.
- Production persistence/scale (single-project, single-user demo state is fine).

### 4.3 The scope-cut ladder (if we fall behind, cut from the bottom up)
1. Timeline panel → static image.
2. Decision Reconstruction → plain text, no clickable evidence.
3. Live second-half ingestion → pre-computed with "Memory Evolving…" theater + cached fallback.
4. **Never cut:** the animated causal-path reveal on the Living Graph, and the real Cognee-synthesized bridge concept. Those two ARE the product.

---

## 5. User Stories

**Epic A — Ingestion**
- A1. As Arjun, I upload a meeting transcript so its decisions become memory. *(remember)*
- A2. As Arjun, I import commit history so implementations become memory. *(remember)*
- A3. As Arjun, after ingestion the system infers business concepts linking discussions to code. *(memify)*

**Epic B — Reconstruction**
- B1. As Arjun, I ask "Why was pricing removed?" and see the causal chain animate. *(recall)*
- B2. As Arjun, every sentence in the explanation links to its source evidence. *(recall + provenance)*
- B3. As Arjun, I trust the link because I can see the bridge concept, not a keyword match.

**Epic C — Evolution**
- C1. As Arjun, I ingest a new meeting that reverses a decision. *(remember)*
- C2. As Arjun, Chronos supersedes the old decision without deleting it. *(forget)*
- C3. As Arjun, the same question now returns the current truth plus the history of why it changed. *(recall)*

**Acceptance test for the whole system (the demo, encoded):**
> Given the seed dataset, when I ask "What is our pricing strategy?" before and after ingesting the reversal meeting, the answer changes from "hidden for enterprise" to "transparent pricing restored," and the graph shows the old decision node marked `SUPERSEDED` with an edge to the new one.

---

## 6. Success Metrics

### 6.1 Judging-aligned (the ones that win)
| Criterion | Target signal in demo |
|---|---|
| Potential Impact | Judge nods at "30–60 min → 10 sec"; recognizes the pain |
| Creativity | Audible reaction to `forget()`-as-supersession |
| Technical Excellence | Bridge concept links vocabulary-disjoint sources live |
| Best Use of Cognee | All 4 APIs do visible, load-bearing work + guided ontology |
| User Experience | Graph animation reads as "watching a brain think" |
| Presentation | Story arc lands: setup → reconstruction → twist → evolved answer |

### 6.2 Technical acceptance metrics
- Bridge concept correctly links the two disjoint sources: **must pass Milestone 0**.
- Causal recall returns ≥1 correct chain with ≥3 nodes and cited evidence.
- Supersession changes the recall answer deterministically.
- Graph reveal animation completes < 6s; live re-ingestion shows a state within 500ms and completes < 30s (with fallback).

---

## 7. System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + TS)                     │
│  ┌────────────────┐  ┌────────────────────┐  ┌─────────────────┐  │
│  │  Living Graph  │  │ Decision Reconstruct│  │    Timeline     │  │
│  │  (React Flow)  │  │  (narrative+cites)  │  │ (vertical)      │  │
│  │  HERO / animated│  │  supporting         │  │ supporting      │  │
│  └───────┬────────┘  └─────────┬──────────┘  └────────┬────────┘  │
│          └──────────── Zustand store (graph+answer state) ───────┘ │
│                          │  REST + WebSocket                        │
└──────────────────────────┼─────────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI, Python)                      │
│  /ingest  /recall  /evolve  /graph  /reset   + WS /ws/evolve       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │             Chronos Memory Service (thin orchestration)        │ │
│  │  remember() • recall() • memify()/improve() • forget()         │ │
│  └───────────────────────────┬──────────────────────────────────┘ │
│                              ▼                                     │
│  ┌───────────────┐   ┌────────────────────────┐   ┌────────────┐  │
│  │   COGNEE      │   │  Ontology / Enrichment  │   │  App DB    │  │
│  │ graph+vector  │   │  (Decision, Concept,    │   │ (SQLite)   │  │
│  │  memory       │   │   Artifact, Outcome)    │   │ metadata   │  │
│  └───────────────┘   └────────────────────────┘   └────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 7.1 Stack decisions (and why)
- **Cognee** — the memory core. Python-native, so the backend is Python.
- **Backend: FastAPI** — async, WebSocket-friendly for the "Memory Evolving…" state, minimal boilerplate.
- **Frontend: React + TypeScript + Vite** — fast, hackathon-standard.
- **Graph: React Flow** — the hero. Declarative nodes/edges, built-in animation hooks, easy programmatic highlighting. (Alt: Cytoscape.js if we need heavier layout.)
- **State: Zustand** — trivial to drive synchronized panels off one store.
- **App DB: SQLite** — store source metadata, decision status (`active`/`superseded`), and cached graph snapshots for the fallback. Cognee holds the memory graph; SQLite holds app-level bookkeeping.
- **LLM for Cognee**: default to the latest Claude model (`claude-opus-4-8` or `claude-sonnet-4-6` for speed) wherever Cognee's pipeline calls an LLM, configured via env.

### 7.2 Data flow — reconstruction (first half)
1. Frontend `POST /recall {question}` →
2. Backend calls Cognee `recall()` with ontology-aware query →
3. Backend shapes the returned subgraph into `{nodes, edges, path[], answer, citations[]}` →
4. Frontend receives ordered `path[]`, animates nodes in sequence, then reveals the narrative.

### 7.3 Data flow — evolution (second half, live)
1. Frontend `POST /evolve {new_transcript}` and opens `WS /ws/evolve` →
2. Backend emits `stage: "remembering"` → `remember(new_transcript)` →
3. emits `stage: "memifying"` → `memify()` re-infers concepts →
4. emits `stage: "superseding"` → `forget(old_decision)` marks supersession + links new→old →
5. emits `stage: "done"` with the updated subgraph → frontend re-animates the delta.
6. **Fallback:** if any stage exceeds a timeout, backend serves the cached post-evolution snapshot and frontend shows "restored from same pipeline result."

---

## 8. Cognee Integration Plan (the heart)

### 8.1 API mapping (every API is load-bearing)
| Cognee API | Chronos use | Demo beat |
|---|---|---|
| `remember()` | Ingest transcripts + commits as memory nodes | Setup (pre-warmed) + live new meeting |
| `memify()` / `improve()` | Synthesize **bridge concept** nodes + cross-source causal edges from the ontology | The "it's not grep" moment |
| `recall()` | Reconstruct the causal chain for a "why" question | The graph animates |
| `forget()` | **Supersede** contradicted decisions; preserve as history | The twist / evolution |

### 8.2 Guided-ontology strategy (the legitimacy argument)
We do **not** hardcode the final edges. We **define the world's vocabulary** and let Cognee reason:
- Provide Cognee a domain ontology (Section 9) so `memify()` knows the entity types that matter (Decision, BusinessConcept, Artifact, Outcome) and the relations that connect them (`MOTIVATED_BY`, `IMPLEMENTED_BY`, `SUPERSEDES`, …).
- Cognee performs the actual inference of *which* concept exists and *which* sources attach to it.
- **Say this explicitly in the presentation:** "A serious memory ships with a schema. We taught Cognee what kind of world it lives in; Cognee did the reasoning." This converts a limitation into a signal of depth.

### 8.3 Milestone 0 — Riskiest Assumption Test (DO THIS FIRST, before any UI)
A throwaway script that:
1. `remember()` the two disjoint seed sources (Appendix A).
2. Run `memify()`/`improve()`.
3. **Inspect the raw graph**: did a `BusinessConcept` node (~"Improve Enterprise Conversion") appear, with edges to *both* the meeting decision and the commit?
4. `recall("why was pricing removed")` — does it reconstruct the link without keyword overlap?

**Decision gate:**
- ✅ Bridge appears unsupervised → proceed, celebrate.
- ⚠️ Appears only with ontology guidance → adopt the ontology (still legitimate) → proceed.
- ❌ Won't appear even guided → pivot the linking to an explicit enrichment step where Cognee scores/justifies candidate links (still Cognee-reasoned, not hardcoded) → proceed.
- 🚫 Cognee cannot relate them at all → escalate; this invalidates the premise. Better to know on Day 1.

---

## 9. Ontology

Entity types and relations Chronos declares to Cognee.

### 9.1 Node types
| Type | Description | Key properties |
|---|---|---|
| `Meeting` | A transcript ingestion unit | id, title, date, participants[] |
| `Decision` | A choice made in a meeting | id, statement, status(`active`/`superseded`), date |
| `BusinessConcept` | Synthesized abstraction linking why↔what | id, label, description *(memify-inferred)* |
| `Artifact` | A concrete change (commit/PR) | id, sha, message, files[], date |
| `Deployment` | A release event (optional) | id, env, date |
| `Outcome` | Observed result (optional) | id, metric, value, date |
| `Person` | Participant/author | id, name, role |

### 9.2 Relation types (edges)
| Edge | From → To | Meaning |
|---|---|---|
| `DISCUSSED_IN` | Decision → Meeting | where a decision was made |
| `MOTIVATED_BY` | Decision → BusinessConcept | the *why* abstraction |
| `REALIZES` | BusinessConcept → Artifact | concept implemented by code |
| `IMPLEMENTED_BY` | Decision → Artifact | decision → code (may be inferred via concept) |
| `DEPLOYED_AS` | Artifact → Deployment | shipped |
| `RESULTED_IN` | Deployment → Outcome | measured effect |
| `SUPERSEDES` | Decision → Decision | new decision replaces old |
| `AUTHORED_BY` | Artifact → Person | commit author |

### 9.3 The causal chain (what recall reconstructs)
```
Meeting ──DISCUSSED_IN── Decision ──MOTIVATED_BY── BusinessConcept ──REALIZES── Artifact ──DEPLOYED_AS── Deployment ──RESULTED_IN── Outcome
```
Supersession adds: `Decision(new) ──SUPERSEDES──► Decision(old, status=superseded)`.

---

## 10. Graph Schema (frontend contract)

The backend normalizes Cognee's output into this stable shape the UI renders:

```jsonc
// GET /graph  and  POST /recall response
{
  "nodes": [
    { "id": "dec_1", "type": "Decision", "label": "Hide pricing for enterprise",
      "status": "superseded", "date": "2026-05-02", "meta": {...} },
    { "id": "concept_1", "type": "BusinessConcept", "label": "Improve Enterprise Conversion",
      "synthesized": true },
    { "id": "art_1", "type": "Artifact", "label": "Replace tier cards with Contact Sales CTA",
      "sha": "a1b2c3d", "files": ["hero.tsx"] }
  ],
  "edges": [
    { "id": "e1", "source": "dec_1", "target": "concept_1", "type": "MOTIVATED_BY" },
    { "id": "e2", "source": "concept_1", "target": "art_1", "type": "REALIZES" }
  ],
  "path": ["meet_1","dec_1","concept_1","art_1","dep_1","out_1"], // ordered reveal
  "answer": "Pricing was hidden for enterprise because ...",
  "citations": [
    { "sentenceIndex": 0, "nodeId": "meet_1", "quote": "enterprise prospects hesitate..." }
  ]
}
```

`path` drives the animation order. `synthesized:true` flags memify-created nodes so the UI can render them distinctly (glow / dashed halo) — visual proof of inference.

---

## 11. API Design (backend)

Base: `/api`

| Method | Route | Body | Returns | Notes |
|---|---|---|---|---|
| POST | `/ingest` | `{type:"meeting"\|"commits", payload}` | `{ok, nodeIds[]}` | calls `remember()` |
| POST | `/memify` | `{}` | `{ok, synthesized[]}` | calls `improve()`/`memify()`; used in setup |
| POST | `/recall` | `{question}` | Graph-schema object (§10) | calls `recall()`, shapes subgraph + path |
| POST | `/evolve` | `{new_transcript}` | `{jobId}` | kicks off async evolution; watch WS |
| WS | `/ws/evolve` | — | `{stage, progress, subgraph?}` | stages: remembering→memifying→superseding→done |
| GET | `/graph` | — | full current Graph-schema object | initial load |
| POST | `/reset` | — | `{ok}` | reload seed state (demo re-runs) |

**Design principles**
- Backend is a **thin orchestration layer**; all reasoning lives in Cognee. Routes are small.
- Every recall response is **self-describing** (nodes+edges+path+answer+citations) so the frontend never queries the graph a second time to animate.
- WebSocket exists solely to make the live evolution feel alive and to enable the "Memory Evolving…" state.

---

## 12. Database Design (App DB — SQLite)

Cognee owns the memory graph. SQLite owns app bookkeeping + fallback cache.

```sql
CREATE TABLE sources (
  id TEXT PRIMARY KEY,
  type TEXT CHECK(type IN ('meeting','commits')),
  title TEXT,
  raw_text TEXT,
  ingested_at TEXT
);

CREATE TABLE decisions (            -- mirror for fast status queries + supersession UI
  id TEXT PRIMARY KEY,
  statement TEXT,
  status TEXT CHECK(status IN ('active','superseded')) DEFAULT 'active',
  superseded_by TEXT,               -- decision id
  source_id TEXT REFERENCES sources(id),
  created_at TEXT
);

CREATE TABLE graph_snapshots (      -- fallback cache for the live-demo safety net
  id TEXT PRIMARY KEY,
  label TEXT,                       -- 'pre_evolution' | 'post_evolution'
  payload_json TEXT,                -- full Graph-schema object
  created_at TEXT
);
```

Rationale: `graph_snapshots` is the **demo insurance policy** — if live `/evolve` stalls, serve `post_evolution` snapshot instantly.

---

## 13. UI/UX Specification

### 13.1 Layout — three synchronized panels
```
┌───────────────────────────────────────────────────────────────────────┐
│  CHRONOS   ● project: Acme Corp Website        [Ask why…____________]  🔍│
├───────────────────────────────────┬───────────────────────────────────┤
│                                   │  DECISION RECONSTRUCTION            │
│        LIVING GRAPH (HERO)        │  ───────────────────────────────   │
│                                   │  Pricing was hidden for enterprise  │
│   [Meeting]                       │  because enterprise prospects were  │
│       │ DISCUSSED_IN              │  hesitating at tiered pricing¹.     │
│   [Decision]  ⬤ (glows)          │  It was implemented by replacing    │
│       │ MOTIVATED_BY              │  the tier cards with a Contact      │
│   [Concept ✦ synthesized]        │  Sales CTA².                        │
│       │ REALIZES                  │  ─ evidence ─                       │
│   [Commit]                        │  ¹ Meeting 05-02 “…hesitate…”       │
│       │ DEPLOYED_AS               │  ² commit a1b2c3d hero.tsx          │
│   [Deploy] → [Outcome]           ├───────────────────────────────────┤
│                                   │  TIMELINE                           │
│   (only panel that animates)      │  05-02 ● Decision: hide pricing     │
│                                   │  05-03 ● Commit: contact sales CTA  │
│                                   │  05-24 ● Decision: RESTORE (new)    │
│                                   │         ↑ supersedes 05-02          │
└───────────────────────────────────┴───────────────────────────────────┘
```

### 13.2 Interaction spec — the reconstruction (first half)
1. User types/asks "Why was pricing removed?" → hero graph dims to neutral.
2. Nodes illuminate **in `path` order**, ~600ms each, edge draws with a flowing gradient.
3. `synthesized:true` concept node gets a distinct **pulse/glow** — call it out verbally: *"Chronos invented this concept — it's in neither source."*
4. Only after the path completes, the **Reconstruction panel** types out the answer.
5. Hovering a sentence highlights its source node (citation ↔ node linkage).

### 13.3 Interaction spec — the evolution (second half)
1. User clicks **"Ingest new meeting"** → picks the reversal transcript.
2. UI enters **"Memory Evolving…"** state: hero graph shows a soft shimmer overlay, WS stages annotate progress ("Remembering… Improving… Superseding…").
3. On `done`: the old `Decision` node **desaturates + gets a `SUPERSEDED` badge**, a new `Decision` node animates in, and a `SUPERSEDES` edge draws from new→old.
4. User re-asks *"What is our pricing strategy?"* → answer now reflects the restore, with a "why it changed" trailer.

### 13.4 Visual design principles
- **Dark canvas**, high-contrast node types (color-coded by ontology type), one accent color for the active causal path.
- Motion communicates meaning: **reasoning = illumination**, **evolution = desaturation + rerouting**. No decorative animation.
- Node type legend always visible so judges can read the graph instantly.
- Empty/loading states never look frozen — always a labeled state.

### 13.5 Accessibility / demo-room realities
- Large fonts, high contrast (projector-safe).
- Nothing critical relies on hover-only (also expose a "trace path" button).
- Reduced-motion fallback: instant path highlight instead of sequential (safety).

---

## 14. Wireframes

**W1 — Landing / project load**
```
┌──────────────────────────────┐
│ CHRONOS                       │
│ The memory that remembers WHY │
│ [ Load demo project ▸ ]       │
│ [ + New project ]             │
└──────────────────────────────┘
```

**W2 — Main workspace:** see §13.1.

**W3 — Evolution modal**
```
┌──────── Ingest new meeting ────────┐
│ [ drop transcript / paste text ]   │
│ preview: "2026-05-24 standup…"     │
│           [ Remember ▸ ]           │
└────────────────────────────────────┘
        ↓ (WS stages)
   ● Remembering…  ● Improving…  ● Superseding…  ✓ Done
```

**W4 — Evidence popover** (click a citation) → shows original source excerpt + jump-to-node.

---

## 15. Folder Structure

```
chronos/
├── README.md
├── PRD_Chronos.md
├── docker-compose.yml            # cognee + backend + frontend (optional)
├── .env.example                  # LLM keys, COGNEE config, model ids
│
├── spike/                        # Milestone 0 — riskiest assumption test
│   ├── test_bridge.py            # remember→memify→inspect→recall
│   └── inspect_graph.py          # dump raw Cognee graph
│
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py               # FastAPI app + routes
│   │   ├── config.py             # env, model ids, cognee init
│   │   ├── memory/
│   │   │   ├── service.py        # thin orchestration over Cognee
│   │   │   ├── ontology.py       # node/edge type defs handed to Cognee
│   │   │   ├── remember.py       # ingest transcripts + commits
│   │   │   ├── memify.py         # improve/synthesize bridge concepts
│   │   │   ├── recall.py         # query + shape subgraph → Graph-schema
│   │   │   └── forget.py         # supersession logic
│   │   ├── shaping.py            # cognee output → §10 Graph-schema
│   │   ├── ws.py                 # /ws/evolve stage emitter
│   │   ├── db.py                 # sqlite (sources, decisions, snapshots)
│   │   └── seed/
│   │       ├── meeting_01_hide_pricing.md
│   │       ├── commits_01.json
│   │       └── meeting_02_restore_pricing.md   # the reversal
│   └── tests/
│       ├── test_recall_chain.py
│       └── test_supersede.py
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── store/graphStore.ts        # Zustand: nodes, edges, path, answer, phase
        ├── api/client.ts              # REST + WS wrappers
        ├── components/
        │   ├── LivingGraph.tsx        # HERO — React Flow + path animation
        │   ├── Reconstruction.tsx     # narrative + clickable citations
        │   ├── Timeline.tsx           # vertical decision timeline
        │   ├── AskBar.tsx             # question input
        │   ├── EvolveModal.tsx        # new-meeting ingestion + WS stages
        │   └── EvidencePopover.tsx
        ├── graph/
        │   ├── nodeTypes.tsx          # per-ontology-type node renderers
        │   ├── layout.ts              # deterministic layout for demo repeatability
        │   └── animatePath.ts         # sequential illumination controller
        └── styles/theme.css
```

---

## 16. Implementation Roadmap

Assumes a ~2–3 day hackathon and a 2–3 person team. **Milestone 0 is a hard gate.**

### Phase 0 — Riskiest Assumption Test (first 2–4 hrs) — GATE
- [ ] `spike/test_bridge.py`: remember 2 disjoint sources → memify → inspect graph → recall.
- [ ] Confirm bridge concept + cross-source edges exist. Decide unsupervised vs guided.
- **Gate:** do not proceed to UI until this is green or the ontology path is chosen.

### Phase 1 — Backend memory core (Day 1)
- [ ] Cognee init + config + model wiring.
- [ ] `remember.py` for transcripts + commits; seed data loaded.
- [ ] `ontology.py` finalized (§9).
- [ ] `memify.py` synthesizes concepts; verified on seed.
- [ ] `recall.py` returns a real causal chain; `shaping.py` → §10 schema.
- [ ] `POST /recall` and `GET /graph` working end-to-end (curl-testable).

### Phase 2 — Living Graph hero (Day 1 → Day 2)
- [ ] React Flow canvas, ontology-typed nodes, deterministic layout.
- [ ] `animatePath.ts`: sequential illumination driven by `path[]`.
- [ ] Synthesized-node glow treatment.
- [ ] AskBar → /recall → animate → reveal reconstruction.

### Phase 3 — Evolution / forget (Day 2)
- [ ] `forget.py` supersession + `SUPERSEDES` edge.
- [ ] `POST /evolve` + `WS /ws/evolve` stage emitter.
- [ ] EvolveModal + "Memory Evolving…" state + node desaturation/reroute.
- [ ] Snapshot the pre/post graph into `graph_snapshots` (fallback insurance).

### Phase 4 — Supporting panels + polish (Day 2 → Day 3)
- [ ] Reconstruction panel with clickable citations.
- [ ] Timeline panel.
- [ ] Theme, legend, projector-safe typography, reduced-motion fallback.

### Phase 5 — Demo hardening (final hours) — CRITICAL
- [ ] `POST /reset` to reload clean seed state between runs.
- [ ] Pre-warm script: full ingest+memify done before stage.
- [ ] Rehearse the exact script (§18) ≥5 times.
- [ ] Verify fallback: kill the network mid-evolve, confirm cached snapshot serves.
- [ ] Record a backup screen-capture of a perfect run (ultimate insurance).

---

## 17. Testing Strategy

### 17.1 Milestone-0 test (the one that de-risks everything)
Assert that after remember+memify on disjoint sources, a `BusinessConcept` node exists with edges to both the meeting-derived `Decision` and the `Artifact`.

### 17.2 Backend integration tests
- `test_recall_chain.py`: `recall("why was pricing removed")` returns `path` of ≥3 nodes including the synthesized concept, with ≥1 citation.
- `test_supersede.py`: after evolve, old decision `status=='superseded'`, `SUPERSEDES` edge exists, and recall answer text changes.

### 17.3 Demo-reliability tests (most important for winning)
- **Reset idempotency:** run the full demo twice back-to-back via `/reset`; identical results.
- **Determinism:** layout + path order stable across runs (judges see the same beautiful thing you rehearsed).
- **Fallback drill:** simulate `/evolve` timeout → cached snapshot serves < 500ms.
- **Cold-projector check:** run on the actual demo screen/resolution once.

### 17.4 What we deliberately do NOT test
Auth, scale, concurrency, edge-case inputs — out of MVP scope; testing them burns time that belongs to the demo.

---

## 18. Demo Script (≈4–5 minutes)

**[0:00 — The hook] (say the pain, don't explain the tech)**
> "Every freelance dev has lived this. Weeks into a project, the client asks: *'Why did we remove the pricing section?'* You made the change — but the *why* is scattered across a meeting, a Slack thread, and a commit. You lose an hour reconstructing it. Chronos reconstructs it in ten seconds — and here's the part that matters: it works even when *nothing was written down the same way twice.*"

**[0:30 — Setup] (show the two disjoint sources)**
> Show the meeting transcript ("enterprise prospects hesitate at pricing tiers") and the commit ("replace tier cards with Contact Sales CTA"). *Point out: no shared words.*

**[1:00 — The reconstruction] (HERO moment)**
> Ask: *"Why was pricing removed?"* The graph illuminates node by node: Meeting → Decision → **[pause]** → **the synthesized concept "Improve Enterprise Conversion"** → Commit → Deploy.
> **The line:** *"Chronos invented that middle node. It's in neither the meeting nor the commit. That's not search — that's memory reasoning. Cognee synthesized the concept that links a business worry to a line of code."*

**[2:00 — Evidence]**
> Reconstruction panel types the answer; hover a sentence, its source lights up. *"Every claim is traceable to the original source."*

**[2:30 — The twist: memory evolves] (the live beat)**
> "But real projects change their mind." Click **Ingest new meeting** — the reversal ("enterprise research shows buyers want transparent pricing — put it back").
> UI shows **"Memory Evolving…"** → the old decision desaturates, a `SUPERSEDED` badge appears, a new decision node routes in.
> *(If it stalls: "and here's the result of that same pipeline" → cached snapshot. Seamless.)*

**[3:15 — The payoff] (same question, evolved answer)**
> Re-ask the **exact same question**: *"What is our pricing strategy?"* The answer is now *different* — transparent pricing restored — **and** it explains *why it changed*, preserving the history.
> **The closing line:** *"Chronos didn't just store a decision. It watched reality change and updated what's true — without forgetting how it got here. That's memory that doesn't just persist. It lives."*

**[3:45 — Cognee callout] (bank the 'Best Use' points)**
> One slide: `remember` (ingested both sources) · `memify` (synthesized the bridge concept) · `recall` (reconstructed the chain) · `forget` (superseded, not deleted). *"All four, each doing real work. Without Cognee, Chronos can't exist."*

**[4:00 — Impact close]**
> "For a freelancer, this is the difference between 'let me get back to you' and answering instantly. For an agency, it's institutional memory that survives team churn. Chronos remembers the one thing every other tool forgets: **why.**"

---

## 19. Judging Strategy (map to the six criteria)

| Criterion | How we win it | The moment / artifact |
|---|---|---|
| **Potential Impact** | Concrete, relatable pain (30–60 min → 10 s); clear expansion path (agencies, more sources) | Opening hook + impact close |
| **Creativity & Innovation** | `forget()` as *supersession/evolution* in a "doesn't forget" hackathon — counterintuitive | The twist beat |
| **Technical Excellence** | Vocabulary-mismatch link via synthesized concept; guided ontology; graph-shaping layer | The synthesized-node reveal |
| **Best Use of Cognee** | All 4 APIs load-bearing + explicit ontology-guidance narrative | The one-slide Cognee callout |
| **User Experience** | Reasoning rendered as motion; "reasoning = illumination, evolution = reroute" | The animated hero graph |
| **Presentation Quality** | Story arc (setup→reconstruct→twist→evolved answer); rehearsed; bulletproof fallback | The whole 4-min script |

**Framing tactics to say out loud:**
1. *"This is not RAG."* — pre-empt the skeptic; show the vocabulary mismatch.
2. *"We taught Cognee its world, Cognee did the reasoning."* — legitimize the ontology.
3. *"Real data, choreographed reveal."* — own the demo posture confidently.
4. Name the anti-positioning: *"Not a chatbot, not a notes app, not a vector DB UI."*

---

## 20. Stretch Goals (mention as roadmap; build only if ahead)

1. **Third source, live link:** add Slack/GitHub-issues ingestion to show 3-way concept convergence.
2. **Confidence & provenance scoring:** each edge shows Cognee's justification/confidence — deepens "not grep."
3. **Contradiction detection:** Chronos proactively flags *"this new decision conflicts with decision X — supersede?"*
4. **"Ask the memory" over voice:** speak the question; transcription → recall.
5. **Decision digest:** auto-generated "what changed and why this week" per project.
6. **Multi-project memory:** switch projects; cross-project concept reuse.
7. **Client-facing read-only portal:** the tertiary persona self-serves "why."

---

## 21. Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| Cognee won't synthesize the bridge unsupervised | **Critical** | Milestone 0 gate; guided ontology; enrichment-scoring fallback |
| `memify()` latency on stage | High | Pre-warm first half; "Memory Evolving…" state; cached snapshot fallback |
| Graph animation eats all the time | High | Hero panel only animates; others static; scope-cut ladder (§4.3) |
| Three-panel sync complexity | Medium | Single Zustand store; recall response is self-describing (no re-query) |
| Live evolve fails at the podium | Medium | Cached `post_evolution` snapshot + confident scripted line |
| Demo not repeatable between runs | Medium | `/reset` + deterministic layout; rehearse ≥5× |
| "It's just ChatGPT/RAG" perception | Medium | Vocabulary-mismatch reveal + explicit "not RAG" framing |
| Model/API key/network on venue wifi | Medium | Local fallback, pre-warmed state, recorded backup video |

---

## Appendix A — Seed Data (engineered for vocabulary mismatch)

**`meeting_01_hide_pricing.md`** (the why — no word "pricing section", no "remove"):
> *Date 2026-05-02. Participants: Arjun, Client (Nadia).*
> Nadia: "Our enterprise prospects keep hesitating. When they land on the site and immediately see the number tiers up top, they think we're too small-time for their scale. The sales team says the bigger accounts want to talk to a human, not self-serve."
> Arjun: "So the tier cards up front are actively costing us the enterprise deals. Let's route those buyers to sales instead of showing them retail-style tiers."
> Decision: prioritize enterprise conversion over self-serve signposting on the landing hero.

**`commits_01.json`** (the what — no word "enterprise", no "conversion"):
```json
[
  { "sha": "a1b2c3d", "date": "2026-05-03",
    "message": "hero.tsx: drop tier cards, add Contact Sales CTA",
    "files": ["src/components/hero.tsx"], "author": "Arjun" }
]
```

**`meeting_02_restore_pricing.md`** (the reversal — for the live evolution beat):
> *Date 2026-05-24. Participants: Arjun, Client (Nadia).*
> Nadia: "We ran interviews with the enterprise buyers we lost. Surprise — they actually *distrust* vendors who hide numbers. Opaque pricing read as 'expensive and negotiable', which slowed procurement. They want transparent, published pricing they can take to finance."
> Arjun: "So hiding it backfired. Let's bring back visible pricing — but framed for enterprise, with an annual/enterprise column."
> Decision: restore transparent pricing on the hero; supersede the 05-02 decision to hide tiers.

**Shared bridge concept (memify must synthesize, not us):** *"Improve Enterprise Conversion."*
Both meetings and the commit attach to it; the two decisions are linked by `SUPERSEDES`.

---

## Appendix B — Definition of Done (MVP)

- [ ] Milestone 0 passed (bridge concept verified real).
- [ ] `recall("why was pricing removed")` animates a ≥5-node causal path including the synthesized concept, with citations.
- [ ] Live evolve supersedes the old decision and re-answers the same question differently.
- [ ] Fallback snapshot verified under simulated failure.
- [ ] `/reset` gives a clean, repeatable demo.
- [ ] 4-minute script rehearsed ≥5×; backup video recorded.

---

*End of PRD v1.0 — build-ready. First action: `spike/test_bridge.py`. Do not build UI until the bridge concept is verified.*
