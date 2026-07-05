# Milestone 0 — Cognee Bridge-Concept Spike

**This is a throwaway probe, not product code.** It is fully independent from
`backend/`. Its only job is to answer the single riskiest question in Chronos:

> Can Cognee connect two **vocabulary-disjoint** sources — a meeting transcript
> (the *why*) and a git commit log (the *what*) — through a **synthesized shared
> business concept** that appears in *neither* source?

If yes → the core premise of Chronos is validated, build with confidence.
If no → we learn *today* that we need a guided ontology, while there's still time.

## Files

```
spike/
├── test_bridge.py                     # the probe (run this)
├── requirements.txt                   # isolated deps (cognee)
├── README.md
└── data/
    ├── meeting_01_hide_pricing.md     # source A — the WHY (no code words)
    └── commits_01.json                # source B — the WHAT (no business words)
```

## Prerequisites

Cognee needs an LLM to extract entities and relationships. Set **one** provider's
credentials before running.

**OpenAI (Cognee's default):**
```bash
export LLM_API_KEY="sk-..."
```

**Anthropic (Claude) — matches Chronos' target stack:**
```bash
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-sonnet-4-6"      # fast + cheap for the spike
export LLM_API_KEY="sk-ant-..."
# You may also need an embeddings provider key depending on your cognee version.
```

> The script only *reads* these vars and reports what it finds — it never hardcodes
> a key. If none is set, it will tell you exactly where extraction breaks.

## Run

Use an **isolated** virtual environment (Cognee is large — keep it away from the
backend venv):

```bash
cd spike

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt        # installs cognee (~500MB–2GB, be patient)

python test_bridge.py
```

## What you'll see

The script logs 13 verbose stages, then a **VERDICT**:

- 🎉 **PASS (strong)** — a node structurally links the meeting side to the commit
  side. Confirm one candidate reads like a business concept → premise validated.
- 🟡 **PARTIAL** — concept-ish nodes exist but don't cleanly span both sources →
  next step is a guided `graph_model` (Decision / BusinessConcept / Artifact).
- 🔴 **FAIL** — the two sources were never linked → guided ontology required.
- ⛔ **HARD FAIL** — no graph built → check the first ❌ (usually a missing key).

Whatever the outcome, capture the full stdout — it's the evidence that decides
the Day-1 architecture. **Do not build the backend memory layer until this runs.**

## Notes

- The two sample files are **deliberately** written to share almost no words, so a
  keyword/RAG match cannot bridge them. Only a semantic graph memory can.
- The probe is defensive: it introspects which Cognee functions exist (classic
  `add/cognify/memify/search` vs v1 `remember/recall/improve/forget`) and adapts.
- Re-running is safe: it prunes prior Cognee state at the start of each run.
