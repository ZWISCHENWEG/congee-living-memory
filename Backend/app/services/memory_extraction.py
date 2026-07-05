"""Gemini-backed classification for the autonomous memory engine.

This service turns a raw user message into a structured decision — save a new
fact, forget an existing one, or do nothing — and, separately, judges whether a
new fact should replace a conflicting one. It depends only on the provider-
agnostic `AIProvider.generate` contract, so no vendor SDK leaks in here.
"""

import json
import logging

from fastapi import Depends
from pydantic import ValidationError

from app.schemas.memory_engine import ConflictDecision, MemoryExtraction
from app.services.ai import AIProvider, get_ai_provider
from app.services.ai.base import AIProviderError

logger = logging.getLogger(__name__)


# Instructs the model to act as a memory classifier and emit JSON ONLY.
_CLASSIFY_PROMPT = """\
You are the memory subsystem of an AI assistant with long-term memory.
Analyze the user's message and decide whether it contains information worth
remembering long-term about the user, or whether the user is asking to forget
something previously stored.

Return JSON ONLY. No markdown, no code fences, no commentary.

Rules:
- action = "save"  -> the message states a durable personal fact about the user
  (name, location, birthday, job, preferences, goals, projects, relationships,
  health, skills, etc.).
- action = "forget" -> the user asks to delete/forget/remove something
  (e.g. "forget my birthday", "delete my address", "remove my phone number").
  Put the thing to forget in "memory".
- action = "none"  -> greetings, chit-chat, questions, thanks, or anything not
  worth storing (e.g. "hello", "how are you", "tell me a joke", "what is Python",
  "thanks", "good morning").

For action = "save", normalize "memory" into a clean first-person statement
(e.g. "My favorite language is Python.").

"type" must be one of:
identity, location, education, career, preference, goal, project,
relationship, health, skill, work, other

"importance" is a float 0.0-1.0. Guidelines:
- identity (name): 1.0
- birthday: 0.98
- goals: 0.92
- projects: 0.90
- location / career / education: 0.85
- preferences: 0.75
- skills / relationships / health: 0.70
- temporary or trivial facts: 0.20

Response shapes:
{"action": "save", "memory": "<fact>", "type": "<category>", "importance": <float>}
{"action": "forget", "memory": "<thing to forget>", "type": "other", "importance": 0.0}
{"action": "none"}

User message:
\"\"\"%s\"\"\"
"""


_CONFLICT_PROMPT = """\
You maintain an AI assistant's long-term memory. A new fact may conflict with an
existing stored fact about the same attribute of the user.

Existing memory: "%s"
New memory: "%s"

Decide whether the new memory should REPLACE the existing one (i.e. they describe
the same attribute and the new one supersedes it — e.g. a moved city, a renamed
preference, a corrected name). If they are about different things, do not replace.

Return JSON ONLY, no markdown:
{"replace": <true|false>, "confidence": <float 0.0-1.0>, "reason": "<short>"}
"""


def _strip_json(text: str) -> str:
    """Best-effort extraction of a JSON object from a model response.

    Handles ```json fences and surrounding prose by slicing to the outermost
    braces. Returns the original text if no object is found.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Drop the opening fence line (``` or ```json) and any trailing fence.
        cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


class MemoryExtractionService:
    """Classifies user messages and adjudicates memory conflicts via the LLM."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def classify(self, user_message: str) -> MemoryExtraction:
        """Classify a message into save/forget/none. Never raises.

        Any generation or parse failure degrades to ``action="none"`` so the
        chat flow is never broken by the memory subsystem.
        """
        logger.info("Running memory extraction")
        prompt = _CLASSIFY_PROMPT % user_message
        try:
            result = await self.provider.generate(prompt)
        except AIProviderError as e:
            logger.warning("Memory classification generation failed: %s", type(e).__name__)
            return MemoryExtraction(action="none")

        try:
            payload = json.loads(_strip_json(result.text))
            extraction = MemoryExtraction.model_validate(payload)
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            logger.warning(
                "Failed to parse memory classification (%s): %r", type(e).__name__, result.text
            )
            return MemoryExtraction(action="none")

        logger.info(
            "Gemini classified memory: action=%s type=%s importance=%.2f",
            extraction.action,
            extraction.type,
            extraction.importance,
        )
        return extraction

    async def decide_conflict(self, existing: str, new: str) -> ConflictDecision:
        """Ask the LLM whether `new` should replace `existing`. Never raises."""
        prompt = _CONFLICT_PROMPT % (existing, new)
        try:
            result = await self.provider.generate(prompt)
            payload = json.loads(_strip_json(result.text))
            decision = ConflictDecision.model_validate(payload)
        except (AIProviderError, json.JSONDecodeError, ValidationError, TypeError) as e:
            logger.warning(
                "Conflict decision failed (%s); defaulting to no-replace", type(e).__name__
            )
            return ConflictDecision(replace=False, confidence=0.0, reason="decision unavailable")

        logger.info(
            "Conflict decision: replace=%s confidence=%.2f", decision.replace, decision.confidence
        )
        return decision


def get_memory_extraction_service(
    provider: AIProvider = Depends(get_ai_provider),
) -> MemoryExtractionService:
    return MemoryExtractionService(provider)
