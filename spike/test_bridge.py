"""
Chronos — Milestone 0 : Riskiest Assumption Test  (STANDALONE SPIKE)
====================================================================

GOAL
----
Discover — empirically — whether Cognee can connect TWO vocabulary-disjoint
sources through a *synthesized* shared business concept:

    meeting_01_hide_pricing.md   (the WHY — a discussion, no code words)
    commits_01.json              (the WHAT — code changes, no business words)

The bridge we HOPE Cognee synthesizes is something like:

    "Improve Enterprise Conversion"

...a concept that appears in NEITHER source, yet links both.

THIS IS NOT PRODUCTION CODE. It is a throwaway probe. The goal is NOT to make
it work — it is to learn *exactly* what this installed version of Cognee can and
cannot do, with brutally verbose logging so a human can read the raw truth.

WHAT THIS SCRIPT DOES
---------------------
 1. Introspects the installed Cognee API (which functions actually exist?).
 2. Resets any prior Cognee state (clean run).
 3. Loads the two sample files.
 4. Feeds both into Cognee            -> add()      / remember()
 5. Builds the knowledge graph        -> cognify()
 6. Enriches / derives new facts      -> memify()   / improve()
 7. Dumps the ENTIRE resulting graph  -> every node.
 8. Dumps every edge.
 9. Hunts for synthesized "bridge" concept nodes linking both sources.
10. Runs recall / search for:  "Why was pricing removed?"
11. Prints the full natural-language answer.
12. Prints every supporting node used.
13. Prints execution time for every stage.
14. Logs everything, verbosely.
15. If the bridge cannot be formed, explains — as precisely as possible — what
    failed and where.

RUN
---
    # 1. Cognee needs an LLM. Set ONE provider's credentials, e.g. OpenAI:
    export LLM_API_KEY="sk-..."
    # (or Anthropic — see README.md in this folder)

    # 2. Install cognee into an isolated venv (see spike/README.md), then:
    python test_bridge.py

Everything below is deliberately defensive: Cognee's API has shifted across
versions, so we probe for capabilities instead of assuming them.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
#  Paths & constants
# --------------------------------------------------------------------------- #
SPIKE_DIR = Path(__file__).resolve().parent
DATA_DIR = SPIKE_DIR / "data"
MEETING_FILE = DATA_DIR / "meeting_01_hide_pricing.md"
COMMITS_FILE = DATA_DIR / "commits_01.json"

RECALL_QUESTION = "Why was pricing removed?"

# Words that, if a node contains them, hint the node came from the MEETING side.
MEETING_HINTS = {
    "nadia", "arjun", "enterprise", "prospect", "hesitat", "sales team",
    "self-serve", "signpost", "account", "growth", "revenue", "buyer",
}
# Words that hint a node came from the COMMIT / code side.
COMMIT_HINTS = {
    "hero.tsx", "plancards", "commit", "sha", "cta", "tier card", "package menu",
    "hero.css", "plan-grid", ".tsx", ".css", "repository", "branch",
}
# Words that would indicate a *synthesized abstraction* (the prize).
CONCEPT_HINTS = {
    "conversion", "enterprise", "strategy", "decision", "goal", "objective",
    "positioning", "acquisition", "funnel", "growth",
}


# --------------------------------------------------------------------------- #
#  Verbose logging helpers
# --------------------------------------------------------------------------- #
_T0 = time.perf_counter()


def _elapsed() -> str:
    return f"{time.perf_counter() - _T0:7.2f}s"


def log(msg: str = "") -> None:
    print(f"[{_elapsed()}] {msg}", flush=True)


def banner(title: str) -> None:
    line = "=" * 78
    print(f"\n{line}\n[{_elapsed()}]  {title}\n{line}", flush=True)


def sub(title: str) -> None:
    print(f"\n[{_elapsed()}]  --- {title} ---", flush=True)


def kv(key: str, value: Any) -> None:
    print(f"           {key:<22}: {value}", flush=True)


def short(value: Any, limit: int = 240) -> str:
    text = str(value).replace("\n", " ⏎ ")
    return text if len(text) <= limit else text[:limit] + f"… (+{len(text) - limit} chars)"


# --------------------------------------------------------------------------- #
#  Generic async/sync caller — Cognee mixes sync & async across versions
# --------------------------------------------------------------------------- #
async def call(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Call `fn` whether it is sync or async, returning its result."""
    result = fn(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


def has(obj: Any, name: str) -> bool:
    return hasattr(obj, name) and callable(getattr(obj, name, None))


# --------------------------------------------------------------------------- #
#  Stage 0 — import + introspect Cognee
# --------------------------------------------------------------------------- #
def import_cognee() -> Any:
    banner("STAGE 0 — IMPORT & INTROSPECT COGNEE")
    try:
        import cognee  # noqa: WPS433 (local import is intentional for the spike)
    except Exception as exc:  # pragma: no cover - environment probe
        log("❌ Could not import `cognee`. Is it installed in this environment?")
        log(f"   Error: {exc!r}")
        log("   Fix: create a venv and `pip install cognee` (see spike/README.md).")
        raise SystemExit(1) from exc

    version = getattr(cognee, "__version__", "unknown")
    kv("cognee.__version__", version)
    kv("cognee module path", getattr(cognee, "__file__", "?"))

    sub("Public callables detected on `cognee`")
    interesting = [
        "add", "cognify", "memify", "search",          # classic granular API
        "remember", "recall", "improve", "forget",     # v1.0 high-level API
        "prune", "config", "visualize_graph",
    ]
    capabilities = {}
    for name in interesting:
        present = hasattr(cognee, name)
        capabilities[name] = present
        marker = "✅" if present else "  "
        kv(f"{marker} {name}", "present" if present else "absent")

    # Which ingestion strategy will we use?
    if capabilities.get("add") and capabilities.get("cognify"):
        strategy = "classic"  # add -> cognify -> memify -> search
    elif capabilities.get("remember"):
        strategy = "v1"       # remember -> recall
    else:
        log("❌ Neither classic (add+cognify) nor v1 (remember) API is available.")
        raise SystemExit(1)

    sub("Chosen ingestion strategy")
    kv("strategy", strategy)
    return cognee, capabilities, strategy


# --------------------------------------------------------------------------- #
#  Stage 1 — LLM configuration sanity check
# --------------------------------------------------------------------------- #
def check_llm_config() -> None:
    banner("STAGE 1 — LLM CONFIGURATION")
    # Cognee needs an LLM to extract entities/relationships. It reads these env
    # vars (names vary slightly across versions). We only *report* — we never
    # hardcode a key.
    candidates = [
        "LLM_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "LLM_PROVIDER", "LLM_MODEL",
    ]
    any_key = False
    for name in candidates:
        val = os.environ.get(name)
        if val:
            any_key = any_key or name.endswith("API_KEY")
            shown = val[:6] + "…" if name.endswith("API_KEY") else val
            kv(f"✅ {name}", shown)
        else:
            kv(f"   {name}", "(unset)")

    if not any_key:
        log("⚠️  No LLM API key found in the environment.")
        log("   Cognee's entity/relationship extraction will FAIL without one.")
        log("   Set LLM_API_KEY (OpenAI) or ANTHROPIC_API_KEY before running.")
        log("   Continuing anyway so you can see exactly where it breaks…")


# --------------------------------------------------------------------------- #
#  Stage 2 — reset prior state
# --------------------------------------------------------------------------- #
async def reset_state(cognee: Any) -> None:
    banner("STAGE 2 — RESET COGNEE STATE (clean run)")
    prune = getattr(cognee, "prune", None)
    if prune is None:
        log("… no `cognee.prune` available; skipping reset.")
        return
    try:
        if has(prune, "prune_data"):
            await call(prune.prune_data)
            log("✅ prune_data() — cleared ingested data.")
        if has(prune, "prune_system"):
            try:
                await call(prune.prune_system, metadata=True)
            except TypeError:
                await call(prune.prune_system)
            log("✅ prune_system() — cleared graph/vector/metadata.")
    except Exception as exc:
        log(f"⚠️  Reset failed (continuing): {exc!r}")


# --------------------------------------------------------------------------- #
#  Stage 3 — load the two sample sources
# --------------------------------------------------------------------------- #
def load_sources() -> tuple[str, str]:
    banner("STAGE 3 — LOAD SAMPLE SOURCES")
    for f in (MEETING_FILE, COMMITS_FILE):
        if not f.exists():
            log(f"❌ Missing sample file: {f}")
            raise SystemExit(1)

    meeting_text = MEETING_FILE.read_text(encoding="utf-8")

    # Flatten the commits JSON into readable prose so Cognee treats it as text.
    commits_raw = json.loads(COMMITS_FILE.read_text(encoding="utf-8"))
    lines = [f"Git history for repository '{commits_raw.get('repository', '?')}':", ""]
    for c in commits_raw.get("commits", []):
        lines.append(f"Commit {c.get('sha')} on {c.get('date')} by {c.get('author')}:")
        lines.append(f"  {c.get('message', '')}")
        if c.get("body"):
            lines.append(f"  {c['body']}")
        if c.get("files"):
            lines.append(f"  Files changed: {', '.join(c['files'])}")
        lines.append("")
    commits_text = "\n".join(lines)

    sub("Source A — meeting transcript")
    kv("path", MEETING_FILE.name)
    kv("chars", len(meeting_text))
    kv("preview", short(meeting_text, 300))

    sub("Source B — commit history (flattened)")
    kv("path", COMMITS_FILE.name)
    kv("chars", len(commits_text))
    kv("preview", short(commits_text, 300))

    log("\n   NOTE: by design these two texts share almost no vocabulary.")
    log("   A keyword search CANNOT bridge them. Only a semantic/graph memory can.")
    return meeting_text, commits_text


# --------------------------------------------------------------------------- #
#  Stage 4/5/6 — ingest, build graph, enrich
# --------------------------------------------------------------------------- #
async def ingest_and_build(
    cognee: Any, caps: dict, strategy: str, meeting_text: str, commits_text: str
) -> dict:
    timings: dict[str, float] = {}

    banner("STAGE 4 — INGEST (remember / add)")
    t = time.perf_counter()
    if strategy == "classic":
        # Tag each source with a distinct node_set so we can attribute nodes later.
        try:
            await call(cognee.add, meeting_text, node_set=["meeting"])
            await call(cognee.add, commits_text, node_set=["commits"])
            log("✅ cognee.add() x2 with node_set tags ['meeting'], ['commits'].")
        except TypeError:
            # Older signature without node_set.
            await call(cognee.add, meeting_text)
            await call(cognee.add, commits_text)
            log("✅ cognee.add() x2 (no node_set kwarg in this version).")
    else:  # v1
        await call(cognee.remember, meeting_text)
        await call(cognee.remember, commits_text)
        log("✅ cognee.remember() x2.")
    timings["ingest"] = time.perf_counter() - t
    kv("ingest seconds", f"{timings['ingest']:.2f}")

    # cognify is only needed in the classic strategy (remember() already ran it).
    if strategy == "classic" and caps.get("cognify"):
        banner("STAGE 5 — COGNIFY (build knowledge graph)")
        t = time.perf_counter()
        try:
            await call(cognee.cognify)
            log("✅ cognee.cognify() completed.")
        except Exception as exc:
            log(f"❌ cognify() FAILED: {exc!r}")
            traceback.print_exc()
            raise
        timings["cognify"] = time.perf_counter() - t
        kv("cognify seconds", f"{timings['cognify']:.2f}")

    # ---- enrichment: memify() (classic) or improve() (v1) ----
    banner("STAGE 6 — ENRICH (memify / improve)  ← where the bridge SHOULD form")
    t = time.perf_counter()
    enriched = False
    if caps.get("memify"):
        try:
            await call(cognee.memify)
            log("✅ cognee.memify() completed — derived-fact enrichment ran.")
            enriched = True
        except Exception as exc:
            log(f"⚠️  memify() raised: {exc!r} (continuing to inspect the graph).")
    if not enriched and caps.get("improve"):
        try:
            await call(cognee.improve)
            log("✅ cognee.improve() completed.")
            enriched = True
        except Exception as exc:
            log(f"⚠️  improve() raised: {exc!r}")
    if not enriched:
        log("⚠️  No enrichment step available/succeeded. The bridge, if any, must")
        log("    have come from cognify() alone. Noting this for the verdict.")
    timings["enrich"] = time.perf_counter() - t
    kv("enrich seconds", f"{timings['enrich']:.2f}")

    return {"timings": timings, "enriched": enriched}


# --------------------------------------------------------------------------- #
#  Graph extraction — normalize Cognee's graph into (nodes, edges)
# --------------------------------------------------------------------------- #
async def fetch_graph(cognee: Any) -> tuple[list[dict], list[dict]]:
    """Pull the raw graph out of Cognee's graph engine, normalized to dicts."""
    banner("STAGE 7 — EXTRACT THE RAW GRAPH")

    graph_engine = None
    # The graph engine lives in different places across versions — try several.
    import_paths = [
        "cognee.infrastructure.databases.graph",
        "cognee.infrastructure.databases.graph.get_graph_engine",
    ]
    get_graph_engine = None
    for path in import_paths:
        try:
            module = __import__(path, fromlist=["get_graph_engine"])
            get_graph_engine = getattr(module, "get_graph_engine", None)
            if get_graph_engine:
                kv("graph engine import", path)
                break
        except Exception:
            continue

    if get_graph_engine is None:
        log("❌ Could not locate cognee's get_graph_engine(). Cannot dump the graph.")
        return [], []

    try:
        graph_engine = await call(get_graph_engine)
        raw_nodes, raw_edges = await call(graph_engine.get_graph_data)
    except Exception as exc:
        log(f"❌ get_graph_data() failed: {exc!r}")
        traceback.print_exc()
        return [], []

    nodes = [_normalize_node(n) for n in (raw_nodes or [])]
    edges = [_normalize_edge(e) for e in (raw_edges or [])]
    kv("raw node count", len(nodes))
    kv("raw edge count", len(edges))
    return nodes, edges


def _normalize_node(raw: Any) -> dict:
    """Cognee nodes come as (id, props) tuples or dict-likes; unify them."""
    node_id, props = None, {}
    if isinstance(raw, tuple) and len(raw) == 2:
        node_id, props = raw[0], (raw[1] or {})
    elif isinstance(raw, dict):
        props = raw
        node_id = raw.get("id") or raw.get("uuid")
    else:
        props = getattr(raw, "__dict__", {}) or {}
        node_id = getattr(raw, "id", None)
    if not isinstance(props, dict):
        props = {"value": props}

    label = (
        props.get("name")
        or props.get("text")
        or props.get("description")
        or props.get("label")
        or props.get("content")
        or ""
    )
    ntype = (
        props.get("type")
        or props.get("node_type")
        or props.get("__type__")
        or props.get("label_type")
        or "Unknown"
    )
    return {"id": str(node_id), "label": str(label), "type": str(ntype), "props": props}


def _normalize_edge(raw: Any) -> dict:
    """Edges come as (src, tgt, rel[, props]) tuples or dict-likes; unify them."""
    src = tgt = rel = None
    props: dict = {}
    if isinstance(raw, tuple):
        if len(raw) >= 3:
            src, tgt, rel = raw[0], raw[1], raw[2]
        if len(raw) >= 4 and isinstance(raw[3], dict):
            props = raw[3]
            rel = props.get("relationship_name", rel)
    elif isinstance(raw, dict):
        src = raw.get("source") or raw.get("source_node_id") or raw.get("from")
        tgt = raw.get("target") or raw.get("target_node_id") or raw.get("to")
        rel = raw.get("relationship_name") or raw.get("relationship") or raw.get("type")
        props = raw
    return {"source": str(src), "target": str(tgt), "rel": str(rel), "props": props}


# --------------------------------------------------------------------------- #
#  Stage 7/8 — print every node & edge
# --------------------------------------------------------------------------- #
def dump_nodes(nodes: list[dict]) -> None:
    banner(f"STAGE 7 — EVERY NODE ({len(nodes)})")
    if not nodes:
        log("… (no nodes — the graph is empty)")
        return
    # Group by type for readability.
    by_type: dict[str, list[dict]] = {}
    for n in nodes:
        by_type.setdefault(n["type"], []).append(n)
    for ntype, group in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        sub(f"type = {ntype}   ({len(group)} nodes)")
        for n in group:
            print(f"           • [{n['id'][:8]}] {short(n['label'], 160)}", flush=True)


def dump_edges(edges: list[dict], nodes: list[dict]) -> None:
    banner(f"STAGE 8 — EVERY EDGE ({len(edges)})")
    if not edges:
        log("… (no edges — nothing is connected)")
        return
    label_of = {n["id"]: n["label"] for n in nodes}
    by_rel: dict[str, int] = {}
    for e in edges:
        by_rel[e["rel"]] = by_rel.get(e["rel"], 0) + 1
        s = short(label_of.get(e["source"], e["source"]), 46)
        t = short(label_of.get(e["target"], e["target"]), 46)
        print(f"           {s}  --[{e['rel']}]-->  {t}", flush=True)
    sub("edge relationship histogram")
    for rel, count in sorted(by_rel.items(), key=lambda kv: -kv[1]):
        kv(rel, count)


# --------------------------------------------------------------------------- #
#  Stage 9 — hunt for the synthesized bridge concept
# --------------------------------------------------------------------------- #
def _side_of(text: str) -> set[str]:
    """Which source(s) does this text lexically resemble?"""
    low = text.lower()
    sides = set()
    if any(h in low for h in MEETING_HINTS):
        sides.add("meeting")
    if any(h in low for h in COMMIT_HINTS):
        sides.add("commits")
    return sides


def _neighbors(node_id: str, edges: list[dict]) -> set[str]:
    out = set()
    for e in edges:
        if e["source"] == node_id:
            out.add(e["target"])
        elif e["target"] == node_id:
            out.add(e["source"])
    return out


def find_bridges(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """
    A 'bridge' is a node that connects the MEETING side to the COMMITS side.

    We use two independent signals and report both:
      (A) STRUCTURAL — a node whose graph neighbours include text resembling
          BOTH sources. This is the real prize: a link no keyword search finds.
      (B) LEXICAL    — a node whose own label reads like a synthesized business
          concept (e.g. contains 'conversion', 'strategy', 'enterprise').
    """
    banner("STAGE 9 — HUNT FOR SYNTHESIZED BRIDGE CONCEPT(S)")
    label_of = {n["id"]: n["label"] for n in nodes}

    bridges: list[dict] = []
    for n in nodes:
        neigh = _neighbors(n["id"], edges)
        neigh_sides: set[str] = set()
        for nb in neigh:
            neigh_sides |= _side_of(label_of.get(nb, ""))
        # also include the node's own lexical side
        own_sides = _side_of(n["label"])

        structural = {"meeting", "commits"}.issubset(neigh_sides | own_sides)
        lexical = any(h in n["label"].lower() for h in CONCEPT_HINTS)

        if structural or (lexical and neigh):
            bridges.append({
                "node": n,
                "structural": structural,
                "lexical": lexical,
                "neighbor_sides": sorted(neigh_sides | own_sides),
                "degree": len(neigh),
            })

    if not bridges:
        log("❌ NO bridge candidate found.")
        log("   No single node links the meeting side to the commit side, and no")
        log("   node reads like a synthesized business concept.")
        return bridges

    log(f"✅ {len(bridges)} bridge candidate(s) found:")
    # Strong bridges (structural + spanning both sides) first.
    bridges.sort(key=lambda b: (b["structural"], b["degree"]), reverse=True)
    for i, b in enumerate(bridges, 1):
        n = b["node"]
        sub(f"candidate #{i}")
        kv("node id", n["id"][:8])
        kv("label", short(n["label"], 160))
        kv("node type", n["type"])
        kv("spans sides", b["neighbor_sides"])
        kv("structural bridge", b["structural"])
        kv("reads-like-concept", b["lexical"])
        kv("degree (neighbours)", b["degree"])
    return bridges


# --------------------------------------------------------------------------- #
#  Stage 10/11/12 — recall / search
# --------------------------------------------------------------------------- #
async def run_recall(cognee: Any, caps: dict, nodes: list[dict]) -> None:
    banner(f"STAGE 10 — RECALL / SEARCH  →  {RECALL_QUESTION!r}")
    t = time.perf_counter()
    answer: Any = None
    used_fn = None

    # Prefer graph-aware completion. Try the richest APIs first.
    try:
        if caps.get("search"):
            used_fn = "cognee.search"
            # Resolve SearchType for GRAPH_COMPLETION if possible.
            search_type = _resolve_graph_completion()
            try:
                if search_type is not None:
                    answer = await call(
                        cognee.search,
                        query_text=RECALL_QUESTION,
                        query_type=search_type,
                    )
                else:
                    answer = await call(cognee.search, query_text=RECALL_QUESTION)
            except TypeError:
                # Very old positional signature: search(search_type, query)
                answer = await call(cognee.search, RECALL_QUESTION)
        elif caps.get("recall"):
            used_fn = "cognee.recall"
            answer = await call(cognee.recall, RECALL_QUESTION)
        else:
            log("❌ Neither search() nor recall() is available.")
            return
    except Exception as exc:
        log(f"❌ recall/search FAILED via {used_fn}: {exc!r}")
        traceback.print_exc()
        return

    seconds = time.perf_counter() - t
    kv("recall via", used_fn)
    kv("recall seconds", f"{seconds:.2f}")

    banner("STAGE 11 — FULL ANSWER")
    _print_answer(answer)

    banner("STAGE 12 — SUPPORTING NODES REFERENCED IN THE ANSWER")
    _print_supporting(answer, nodes)


def _resolve_graph_completion() -> Any:
    """Find the SearchType.GRAPH_COMPLETION enum across possible module paths."""
    paths = [
        "cognee.modules.search.types.SearchType",
        "cognee.api.v1.search.SearchType",
        "cognee.shared.data_models.SearchType",
    ]
    for p in paths:
        try:
            mod_path, cls_name = p.rsplit(".", 1)
            module = __import__(mod_path, fromlist=[cls_name])
            search_type_cls = getattr(module, cls_name)
            for candidate in ("GRAPH_COMPLETION", "GRAPH", "COMPLETION"):
                if hasattr(search_type_cls, candidate):
                    kv("SearchType resolved", f"{p}.{candidate}")
                    return getattr(search_type_cls, candidate)
        except Exception:
            continue
    log("… could not resolve SearchType.GRAPH_COMPLETION; will call search() plainly.")
    return None


def _print_answer(answer: Any) -> None:
    if answer is None:
        log("… answer is None (empty result).")
        return
    if isinstance(answer, (list, tuple)):
        kv("result items", len(answer))
        for i, item in enumerate(answer):
            print(f"\n           [result {i}] {short(item, 1200)}", flush=True)
    else:
        print(f"\n{short(answer, 2000)}", flush=True)


def _print_supporting(answer: Any, nodes: list[dict]) -> None:
    """Best-effort: surface any node labels that appear in the answer text."""
    text = json.dumps(answer, default=str).lower() if answer is not None else ""
    if not text:
        log("… no answer text to attribute.")
        return
    hits = []
    for n in nodes:
        label = n["label"].strip().lower()
        if len(label) >= 4 and label in text:
            hits.append(n)
    if not hits:
        log("… no graph node labels were found verbatim in the answer.")
        log("  (This does not prove nothing was used — Cognee may paraphrase.)")
        return
    log(f"✅ {len(hits)} node label(s) appear in the answer:")
    for n in hits[:40]:
        print(f"           • [{n['type']}] {short(n['label'], 120)}", flush=True)


# --------------------------------------------------------------------------- #
#  Verdict
# --------------------------------------------------------------------------- #
def verdict(nodes: list[dict], edges: list[dict], bridges: list[dict], enriched: bool) -> None:
    banner("VERDICT — WHAT DID WE LEARN?")
    graph_built = bool(nodes)
    connected = bool(edges)
    strong = [b for b in bridges if b["structural"]]

    kv("graph built (nodes > 0)", graph_built)
    kv("graph connected (edges)", connected)
    kv("enrichment ran", enriched)
    kv("bridge candidates", len(bridges))
    kv("STRUCTURAL bridges", len(strong))

    print()
    if strong:
        log("🎉 PASS (strong): Cognee produced at least one node that structurally")
        log("   links the meeting side to the commit side — a connection no keyword")
        log("   search could make. Inspect the candidates above and confirm one reads")
        log("   like a business concept (e.g. 'enterprise conversion'). If so, the")
        log("   core premise of Chronos is VALIDATED. Proceed to build.")
    elif bridges:
        log("🟡 PARTIAL: Concept-like or weakly-bridging nodes exist, but none cleanly")
        log("   span BOTH sources structurally. Likely next step: guide cognify() with")
        log("   a custom `graph_model` (Decision / BusinessConcept / Artifact) so the")
        log("   LLM is told which abstractions to synthesize. Still legitimate Cognee")
        log("   use — we define the vocabulary; Cognee does the reasoning.")
    elif graph_built and not connected:
        log("🔴 FAIL (disconnected): Cognee extracted nodes but did NOT connect the two")
        log("   sources at all. The two documents live as isolated islands. A shared")
        log("   ontology / graph_model is almost certainly required — test that next.")
    elif graph_built:
        log("🔴 FAIL (no bridge): The graph is connected internally but the meeting and")
        log("   the commits were never linked. Cognee's default extraction did not find")
        log("   the shared business concept. Next: guided ontology, or an explicit")
        log("   enrichment step that scores candidate cross-source links.")
    else:
        log("⛔ HARD FAIL: No graph was built at all. Check the log above for the first")
        log("   ❌ — most commonly a missing LLM API key or a cognify() exception.")

    print()
    log("Remember: the point of this spike was to LEARN, not to win. Whatever the")
    log("result, we now know exactly what to build on top of — on Day 1, not Day 3.")


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
async def main() -> None:
    banner("CHRONOS · MILESTONE 0 · COGNEE BRIDGE-CONCEPT SPIKE")
    log(f"python           : {sys.version.split()[0]}")
    log(f"working dir      : {SPIKE_DIR}")
    log(f"recall question  : {RECALL_QUESTION!r}")

    cognee, caps, strategy = import_cognee()
    check_llm_config()

    stage_timings: dict[str, float] = {}
    try:
        await reset_state(cognee)
        meeting_text, commits_text = load_sources()
        build = await ingest_and_build(cognee, caps, strategy, meeting_text, commits_text)
        stage_timings = build["timings"]

        nodes, edges = await fetch_graph(cognee)
        dump_nodes(nodes)
        dump_edges(edges, nodes)
        bridges = find_bridges(nodes, edges)
        await run_recall(cognee, caps, nodes)
        verdict(nodes, edges, bridges, build["enriched"])
    except SystemExit:
        raise
    except Exception as exc:
        banner("UNHANDLED EXCEPTION — the spike crashed")
        log(f"❌ {exc!r}")
        traceback.print_exc()
    finally:
        banner("STAGE 13 — EXECUTION TIME SUMMARY")
        for stage, secs in stage_timings.items():
            kv(stage, f"{secs:.2f}s")
        kv("TOTAL wall-clock", f"{time.perf_counter() - _T0:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
