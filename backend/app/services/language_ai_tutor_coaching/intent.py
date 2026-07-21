"""Lightweight student-intent detection for coaching routing (deterministic)."""

from __future__ import annotations

from app.services.language_ai_tutor_coaching.enums import StudentIntent
from app.services.language_ai_tutor_coaching.types import CoachingTurnRequest


_FULL_ANSWER_MARKERS = (
    "just tell me",
    "give me the answer",
    "what is the answer",
    "tell me the answer",
    "full explanation",
    "worked example",
    "i give up",
    "show me the solution",
)

_HINT_MARKERS = ("hint", "clue", "help me start", "stuck", "not sure where")

_WHY_MARKERS = ("why", "how come", "explain why", "what went wrong")

_WRAP_MARKERS = ("wrap up", "summarize the lesson", "lesson summary", "end of lesson", "finish lesson")


def detect_intent(request: CoachingTurnRequest) -> StudentIntent:
    if request.request_wrap_up:
        return StudentIntent.request_wrap_up
    if request.request_full_answer:
        return StudentIntent.request_full_answer

    text = (request.message or "").strip().lower()
    if request.is_correct is False or (
        request.student_attempt and request.is_correct is False
    ):
        return StudentIntent.submit_attempt
    if request.student_attempt and request.is_correct is True:
        return StudentIntent.submit_attempt

    if any(m in text for m in _WRAP_MARKERS):
        return StudentIntent.request_wrap_up
    if any(m in text for m in _FULL_ANSWER_MARKERS):
        return StudentIntent.request_full_answer
    if any(m in text for m in _HINT_MARKERS):
        return StudentIntent.ask_hint
    if any(m in text for m in _WHY_MARKERS):
        return StudentIntent.ask_why
    if "answer" in text and ("?" in text or text.startswith("what")):
        return StudentIntent.ask_answer
    return StudentIntent.general
