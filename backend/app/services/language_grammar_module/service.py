"""Student Grammar Module service — dashboard, generate-only start, Wave D attested complete."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.language_grammar.enums import GrammarEvidenceSourceSkill
from app.services.language_grammar_activity_authoring.llm.lesson_schema import METHODOLOGY_VERSION
from app.services.language_grammar_canonical_authoring.preview import (
    GrammarCanonicalPreviewError,
    build_canonical_lesson_start_package,
)
from app.services.language_grammar_integrity import (
    AttestedCompletionRequest,
    GrammarIntegrityError,
    complete_attested_activity,
    issue_and_stamp_for_context,
)
from app.services.language_grammar_integration import build_learning_snapshot_async
from app.services.language_grammar_integration.types import GrammarLearningSnapshot
from app.services.language_grammar_lesson_planner import plan_lesson
from app.services.language_grammar_module.flags import grammar_module_enabled
from app.services.language_grammar_pipeline.generate import (
    generate_grammar_lesson,
    lesson_dict_from_generation,
)
from app.services.language_grammar_pipeline.types import PipelineRequest, PipelineStatus
from app.services.language_grammar_skill_context import build_skill_grammar_context


class GrammarModuleError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


logger = logging.getLogger(__name__)


def _as_of() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cefr_value(value: object) -> str:
    return str(value.value if hasattr(value, "value") else value or "")


def _topic_cefr_for_target(snapshot: GrammarLearningSnapshot, grammar_id: str, fallback: str) -> str:
    for topic in (snapshot.current_topic, snapshot.next_topic):
        if topic is not None and topic.grammar_id == grammar_id:
            return _cefr_value(topic.cefr_band) or fallback
    return fallback


async def build_grammar_dashboard(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
) -> dict:
    """Preview metadata only — planner snapshot, no authoring/execution."""
    if not grammar_module_enabled():
        return {"enabled": False}

    snapshot = await build_learning_snapshot_async(
        db, student_id=student_id, language_id=language_id, as_of=_as_of()
    )
    return _dashboard_from_snapshot(snapshot)


def _dashboard_from_snapshot(snapshot: GrammarLearningSnapshot) -> dict:
    blueprint = plan_lesson(snapshot) if snapshot.enabled else None
    topic = None
    if snapshot.current_topic is not None:
        topic = {
            "grammar_id": snapshot.current_topic.grammar_id,
            "display_name": snapshot.current_topic.display_name,
            "cefr_band": snapshot.current_topic.cefr_band.value
            if hasattr(snapshot.current_topic.cefr_band, "value")
            else str(snapshot.current_topic.cefr_band),
        }
    cefr = (
        snapshot.overall_cefr.value
        if hasattr(snapshot.overall_cefr, "value")
        else str(snapshot.overall_cefr)
    )
    has_target = bool(snapshot.current_grammar_id)
    return {
        "enabled": True,
        "current_cefr": cefr,
        "current_grammar_topic": topic,
        "grammar_target": snapshot.current_grammar_id,
        "difficulty": "guided",
        "estimated_minutes": int(blueprint.estimated_duration_minutes) if blueprint else 10,
        "lesson_goal": (blueprint.lesson_goal if blueprint else "")
        or (topic["display_name"] if topic else ""),
        "has_lesson_preview": has_target,
        "empty_state_message": "Generate your first Grammar lesson."
        if not has_target
        else "",
    }


async def start_grammar_lesson(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
    use_llm_authoring: bool = True,
    learning_snapshot: GrammarLearningSnapshot | None = None,
) -> dict:
    """Generate personalized lesson package — no execution/evaluation/mastery/review."""
    if not grammar_module_enabled():
        raise GrammarModuleError("module_disabled", "Grammar module is not available.")

    snapshot = learning_snapshot or await build_learning_snapshot_async(
        db, student_id=student_id, language_id=language_id, as_of=_as_of()
    )
    if not snapshot.current_grammar_id and not snapshot.next_grammar_id:
        raise GrammarModuleError(
            "no_grammar_target",
            "No grammar topic is ready yet. Complete language placement first.",
        )

    cefr = _cefr_value(snapshot.overall_cefr)
    target_grammar_id = snapshot.current_grammar_id or snapshot.next_grammar_id or ""
    target_cefr = _topic_cefr_for_target(snapshot, target_grammar_id, cefr)
    settings = get_settings()
    lesson = await _canonical_lesson_for_start(
        db,
        grammar_id=target_grammar_id,
        cefr_level=target_cefr,
        allow_reviewable=bool(settings.DEBUG),
    )
    if lesson is None:
        outcome = generate_grammar_lesson(
            PipelineRequest(
                student_id=student_id,
                language_id=language_id,
                student_response="",  # unused on generate-only path
                learning_snapshot=snapshot,
                use_llm_authoring=use_llm_authoring,
                activity_type="voice_recording",
                as_of=_as_of(),
                overall_cefr=str(cefr),
                apply_learner_writes=False,
            )
        )
        if outcome.status is not PipelineStatus.completed:
            detail = outcome.failures[0].message if outcome.failures else "Lesson generation failed"
            raise GrammarModuleError("generation_failed", detail)

        # Architecture guard: generate path must never open write gate or execute.
        if outcome.execution_invoked or outcome.write_gate.mastery_applied:
            raise GrammarModuleError(
                "architecture_violation",
                "Generate-only path must not execute or update mastery",
            )

        lesson = lesson_dict_from_generation(outcome)

    grammar_ctx = await build_skill_grammar_context(
        db,
        student_id=student_id,
        language_id=language_id,
        source_skill=GrammarEvidenceSourceSkill.grammar_lesson,
    )
    if grammar_ctx is None:
        raise GrammarModuleError(
            "resolver_empty",
            "Grammar resolver returned no target — cannot start lesson",
        )
    # Server stamp is authoritative; align lesson label to resolver.
    lesson["grammar_target"] = grammar_ctx.grammar_id

    try:
        session = await issue_and_stamp_for_context(
            db,
            student_id=student_id,
            language_id=language_id,
            grammar_ctx=grammar_ctx,
            skill=GrammarEvidenceSourceSkill.grammar_lesson,
            activity_type="grammar_lesson",
            lesson_id=str(lesson.get("lesson_id") or ""),
            server_payload={
                "expected_patterns": list(lesson.get("expected_patterns") or []),
                "lesson_id": str(lesson.get("lesson_id") or ""),
            },
        )
    except GrammarIntegrityError as exc:
        raise GrammarModuleError(exc.code, exc.message) from exc

    lesson["activity_session_id"] = str(session.id)
    lesson["activity_id"] = str(session.id)
    return lesson


async def _canonical_lesson_for_start(
    db: AsyncSession,
    *,
    grammar_id: str,
    cefr_level: str,
    allow_reviewable: bool,
) -> dict | None:
    if not grammar_id or not cefr_level:
        return None
    try:
        return await build_canonical_lesson_start_package(
            db,
            grammar_id=grammar_id,
            cefr_level=cefr_level,
            locale="ar-SY",
            allow_reviewable=allow_reviewable,
            allow_cefr_fallback=allow_reviewable,
        )
    except GrammarCanonicalPreviewError as exc:
        logger.warning(
            "canonical_grammar_start_package_invalid grammar_id=%s cefr=%s methodology=%s code=%s",
            grammar_id,
            cefr_level,
            METHODOLOGY_VERSION,
            exc.code,
        )
        return None


async def complete_grammar_activity(
    db: AsyncSession,
    *,
    student_id: int,
    activity_session_id: str,
    language_id: int = 1,
    answers: dict | list | None = None,
    response_text: str = "",
) -> dict:
    """Wave D: attested completion — client supplies session id + answers only."""
    if not grammar_module_enabled():
        raise GrammarModuleError("module_disabled", "Grammar module is not available.")

    try:
        result = await complete_attested_activity(
            db,
            AttestedCompletionRequest(
                student_id=student_id,
                language_id=language_id,
                activity_session_id=activity_session_id,
                answers=answers,
                response_text=response_text,
            ),
        )
    except GrammarIntegrityError as exc:
        raise GrammarModuleError(exc.code, exc.message) from exc
    except Exception as exc:  # noqa: BLE001
        raise GrammarModuleError("completion_failed", str(exc)) from exc

    return {
        "grammar_id": result.grammar_id,
        "mastery_state": result.mastery_state,
        "overall_mastery": result.overall_mastery,
        "evidence_was_new": result.evidence_was_new,
        "synced_completed_ids": list(result.completed_sync.synced_ids),
        "current_grammar_id": result.current_grammar_id,
        "next_grammar_id": result.next_grammar_id,
        "unlocked_ids": list(result.unlocked_ids),
        "observation_id": result.evidence_batch.observations[0].observation_id
        if result.evidence_batch.observations
        else "",
        "activity_session_id": activity_session_id,
    }
