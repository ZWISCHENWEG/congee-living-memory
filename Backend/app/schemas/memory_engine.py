"""Schemas for the Phase 3 autonomous memory engine.

These value objects describe the structured output of the Gemini-backed memory
classifier and the result of an automatic memory operation. They are kept
separate from the existing `memories`/`chat` schemas so Phase 1/2 contracts stay
untouched.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

#: The twelve memory categories a fact may fall into (Feature 2).
MemoryCategory = Literal[
    "identity",
    "location",
    "education",
    "career",
    "preference",
    "goal",
    "project",
    "relationship",
    "health",
    "skill",
    "work",
    "other",
]

#: Terminal outcomes of a single automatic-memory operation.
MemoryStatus = Literal[
    "created",
    "updated",
    "duplicate",
    "conflict",
    "deleted",
    "ignored",
]


class MemoryExtraction(BaseModel):
    """Structured classification of a single user message (Feature 1 & 7).

    Produced by the Gemini classifier. `action` decides the branch taken by the
    orchestrator: ``save`` a new fact, ``forget`` an existing one, or ``none``.
    """

    action: Literal["save", "forget", "none"] = "none"
    memory: Optional[str] = None
    type: MemoryCategory = "other"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class ConflictDecision(BaseModel):
    """Gemini's verdict on whether a new memory should replace an existing one
    (Feature 6)."""

    replace: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class MemoryAction(BaseModel):
    """Result of the automatic memory pipeline, surfaced on `ChatResponse`.

    Immutable value object. `status` is the single source of truth for the
    frontend; the remaining fields provide context (which memory, what category,
    why). Backwards-compatible: the whole object is optional on the response.
    """

    model_config = ConfigDict(frozen=True)

    status: MemoryStatus
    memory: Optional[str] = None
    memory_id: Optional[str] = None
    type: Optional[str] = None
    importance: Optional[float] = None
    detail: Optional[str] = None


class ConflictResolution(BaseModel):
    """Request body for `POST /memory/resolve-conflict` (Feature 6 tail).

    Sent by the frontend after a chat turn returns ``status="conflict"`` to
    confirm or reject the pending replacement.
    """

    existing_id: str
    new_content: str
    decision: Literal["replace", "keep"]
    type: MemoryCategory = "other"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
