"""Conversation memory helpers — completely separate from educational state."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.services.language_ai_tutor.types import (
    ConversationMemory,
    ConversationTurn,
    TutorMemorySummary,
)

MAX_STORED_TURNS = 40
MAX_RECENT_SUMMARIES = 6
MAX_RECURRING = 8


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_conversation_id() -> str:
    return f"tutor_{uuid.uuid4().hex[:16]}"


def empty_memory(
    *,
    student_id: int,
    language_id: int,
    conversation_id: str | None = None,
) -> ConversationMemory:
    return ConversationMemory(
        student_id=student_id,
        language_id=language_id,
        conversation_id=conversation_id or new_conversation_id(),
        updated_at=_now(),
    )


def memory_to_summary(memory: ConversationMemory) -> TutorMemorySummary:
    recent: list[str] = []
    for turn in memory.turns[-MAX_RECENT_SUMMARIES:]:
        prefix = "Student" if turn.role == "student" else "Tutor"
        text = turn.content.strip().replace("\n", " ")
        if len(text) > 120:
            text = text[:117] + "..."
        recent.append(f"{prefix}: {text}")
    return TutorMemorySummary(
        preferred_tone=memory.preferred_tone,
        preferred_examples=memory.preferred_examples,
        explanation_preference=memory.explanation_preference,
        recurring_questions=memory.recurring_questions[:MAX_RECURRING],
        unfinished_discussion=memory.unfinished_discussion,
        recent_turn_summaries=tuple(recent),
    )


def append_turn(
    memory: ConversationMemory,
    *,
    role: str,
    content: str,
    prompt_kind: str = "",
    mark_unfinished: str | None = None,
) -> ConversationMemory:
    turn = ConversationTurn(
        role=role,
        content=content.strip(),
        prompt_kind=prompt_kind,
        created_at=_now(),
    )
    turns = (*(memory.turns), turn)[-MAX_STORED_TURNS:]
    recurring = list(memory.recurring_questions)
    if role == "student" and content.strip().endswith("?"):
        q = content.strip()
        if q not in recurring:
            recurring = [*(recurring), q][-MAX_RECURRING:]
    unfinished = memory.unfinished_discussion
    if mark_unfinished is not None:
        unfinished = mark_unfinished
    return ConversationMemory(
        student_id=memory.student_id,
        language_id=memory.language_id,
        conversation_id=memory.conversation_id,
        preferred_tone=memory.preferred_tone,
        explanation_preference=memory.explanation_preference,
        preferred_examples=memory.preferred_examples,
        recurring_questions=tuple(recurring),
        unfinished_discussion=unfinished,
        turns=turns,
        schema_version=memory.schema_version,
        updated_at=_now(),
    )


def update_preferences(
    memory: ConversationMemory,
    *,
    preferred_tone: str | None = None,
    explanation_preference: str | None = None,
    preferred_examples: str | None = None,
) -> ConversationMemory:
    return ConversationMemory(
        student_id=memory.student_id,
        language_id=memory.language_id,
        conversation_id=memory.conversation_id,
        preferred_tone=preferred_tone or memory.preferred_tone,
        explanation_preference=explanation_preference or memory.explanation_preference,
        preferred_examples=preferred_examples or memory.preferred_examples,
        recurring_questions=memory.recurring_questions,
        unfinished_discussion=memory.unfinished_discussion,
        turns=memory.turns,
        schema_version=memory.schema_version,
        updated_at=_now(),
    )


def memory_to_dict(memory: ConversationMemory) -> dict:
    return {
        "student_id": memory.student_id,
        "language_id": memory.language_id,
        "conversation_id": memory.conversation_id,
        "preferred_tone": memory.preferred_tone,
        "explanation_preference": memory.explanation_preference,
        "preferred_examples": memory.preferred_examples,
        "recurring_questions": list(memory.recurring_questions),
        "unfinished_discussion": memory.unfinished_discussion,
        "turns": [
            {
                "role": t.role,
                "content": t.content,
                "prompt_kind": t.prompt_kind,
                "created_at": t.created_at,
            }
            for t in memory.turns
        ],
        "schema_version": memory.schema_version,
        "updated_at": memory.updated_at,
    }


def memory_from_dict(raw: dict | None, *, student_id: int, language_id: int) -> ConversationMemory | None:
    if not isinstance(raw, dict) or not raw:
        return None
    try:
        turns_raw = raw.get("turns") or []
        turns = tuple(
            ConversationTurn(
                role=str(t.get("role") or "student"),
                content=str(t.get("content") or ""),
                prompt_kind=str(t.get("prompt_kind") or ""),
                created_at=str(t.get("created_at") or ""),
            )
            for t in turns_raw
            if isinstance(t, dict)
        )
        return ConversationMemory(
            student_id=int(raw.get("student_id") or student_id),
            language_id=int(raw.get("language_id") or language_id),
            conversation_id=str(raw.get("conversation_id") or new_conversation_id()),
            preferred_tone=str(raw.get("preferred_tone") or "supportive"),
            explanation_preference=str(raw.get("explanation_preference") or "guided"),
            preferred_examples=str(raw.get("preferred_examples") or "everyday"),
            recurring_questions=tuple(str(x) for x in (raw.get("recurring_questions") or [])),
            unfinished_discussion=str(raw.get("unfinished_discussion") or ""),
            turns=turns,
            schema_version=int(raw.get("schema_version") or 1),
            updated_at=str(raw.get("updated_at") or ""),
        )
    except (TypeError, ValueError):
        return None
