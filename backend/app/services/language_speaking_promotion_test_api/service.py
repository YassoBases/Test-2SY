"""API orchestration for Speaking Promotion Assessment — S18 create + S19 execution."""

from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.schemas.language_speaking_promotion_test import (
    SpeakingPromotionAssessmentBridgeOut,
    SpeakingPromotionAssessmentCompleteOut,
    SpeakingPromotionAssessmentCreateOut,
    SpeakingPromotionAssessmentGetOut,
    SpeakingPromotionAssessmentResultOut,
    SpeakingPromotionAssessmentStartOut,
    SpeakingPromotionAssessmentStatusOut,
    SpeakingPromotionAssessmentSubmitIn,
    SpeakingPromotionAssessmentSubmitOut,
    SpeakingPromotionAssessmentTaskOut,
)
from app.services.language_progression_service import ensure_progression_row
from app.services.language_speaking.enums import SpeakingLearningStage
from app.services.language_speaking_knowledge_model.locking import lock_speaking_progression_row
from app.services.language_speaking_progression.runtime import run_speaking_progression_engines
from app.services.language_speaking_promotion_readiness.storage import (
    speaking_promotion_bucket_from_payload,
)
from app.services.language_speaking_promotion_test import (
    SpaCreateFailureCode,
    SpaExecutionFailureCode,
    SpaUnlockAuthority,
    SpeakingPromotionAssessment,
    abandon_speaking_promotion_assessment,
    complete_speaking_promotion_assessment,
    create_speaking_promotion_assessment,
    current_task_id,
    find_assessment_in_payload,
    get_active_assessment,
    persist_active_assessment,
    record_task_score,
    start_speaking_promotion_assessment,
    timeout_speaking_promotion_assessment,
)
from app.services.language_speaking_promotion_test.policy import estimated_duration_seconds
from app.services.language_speaking_promotion_test_api.s7_adapter import evaluate_spa_task_with_s7


class SpeakingPromotionAssessmentApiError(Exception):
    def __init__(self, status_code: int, detail: dict | str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


def _unlock_fingerprint(readiness_fp: str, stage_fp: str, official: str, target: str | None) -> str:
    raw = f"{readiness_fp}|{stage_fp}|{official}|{target or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _authority_from_engines(result) -> SpaUnlockAuthority:
    readiness = result.readiness
    stability = result.stability
    return SpaUnlockAuthority(
        spa_unlocked=bool(readiness.spa_unlocked),
        official_cefr=str(readiness.official_cefr),
        target_cefr=readiness.target_cefr,
        readiness_snapshot_fingerprint=str(readiness.snapshot_fingerprint),
        source_stage_signal_fingerprint=str(readiness.source_stage_signal_fingerprint),
        unlock_fingerprint=_unlock_fingerprint(
            str(readiness.snapshot_fingerprint),
            str(readiness.source_stage_signal_fingerprint),
            str(readiness.official_cefr),
            readiness.target_cefr,
        ),
        hard_blockers_empty=bool(readiness.hard_blockers_empty),
        stability_requirements_passed=bool(stability.requirements_passed),
        current_stage_advanced=readiness.current_stage == SpeakingLearningStage.advanced,
    )


def _task_out(raw: dict[str, Any]) -> SpeakingPromotionAssessmentTaskOut:
    return SpeakingPromotionAssessmentTaskOut(
        task_id=str(raw.get("task_id", "")),
        task_order=int(raw.get("task_order") or 0),
        task_family=str(raw.get("task_family", "")),
        execution_mode=str(raw.get("execution_mode", "")),
        scenario=str(raw.get("scenario", "")),
        student_prompt=str(raw.get("student_prompt", "")),
        follow_up_prompts=[str(x) for x in (raw.get("follow_up_prompts") or [])],
        context_descriptor=str(raw.get("context_descriptor", "")),
        max_duration_seconds=int(raw.get("max_duration_seconds") or 0),
        preparation_seconds=int(raw.get("preparation_seconds") or 0),
        spontaneous_production_required=bool(raw.get("spontaneous_production_required", False)),
        spontaneous_interaction_required=False,
    )


def _task_out_from_model(task) -> SpeakingPromotionAssessmentTaskOut:
    return _task_out(task.to_student_safe_dict())


def _assessment_create_out(assessment: SpeakingPromotionAssessment) -> SpeakingPromotionAssessmentCreateOut:
    safe = assessment.to_student_safe_dict(include_tasks=True)
    return SpeakingPromotionAssessmentCreateOut(
        assessment_id=str(safe["assessment_id"]),
        blueprint_id=str(safe["blueprint_id"]),
        status=str(safe["status"]),
        source_cefr=str(safe["source_cefr"]),
        target_cefr=str(safe["target_cefr"]),
        task_count=int(safe["task_count"]),
        frozen=bool(safe["frozen"]),
        has_interaction_coverage_gaps=bool(safe.get("has_interaction_coverage_gaps")),
        tasks=[_task_out(t) for t in (safe.get("tasks") or [])],
        attempt_id=safe.get("attempt_id"),
    )


def _assessment_get_out(assessment: SpeakingPromotionAssessment) -> SpeakingPromotionAssessmentGetOut:
    safe = assessment.to_student_safe_dict(include_tasks=True)
    return SpeakingPromotionAssessmentGetOut(
        assessment_id=str(safe["assessment_id"]),
        blueprint_id=str(safe["blueprint_id"]),
        status=str(safe["status"]),
        source_cefr=str(safe["source_cefr"]),
        target_cefr=str(safe["target_cefr"]),
        task_count=int(safe["task_count"]),
        frozen=bool(safe["frozen"]),
        has_interaction_coverage_gaps=bool(safe.get("has_interaction_coverage_gaps")),
        tasks=[_task_out(t) for t in (safe.get("tasks") or [])],
        created_at=assessment.created_at,
        attempt_id=safe.get("attempt_id"),
        current_task_index=safe.get("current_task_index"),
        ready_for_official_promotion=bool(safe.get("ready_for_official_promotion")),
    )


def _result_out(assessment: SpeakingPromotionAssessment) -> SpeakingPromotionAssessmentResultOut:
    if assessment.result is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Result not available."})
    safe = assessment.result.to_student_safe_dict()
    bridge = None
    if isinstance(safe.get("bridge_recommendation"), dict):
        br = safe["bridge_recommendation"]
        bridge = SpeakingPromotionAssessmentBridgeOut(
            focus_skill_ids=list(br.get("focus_skill_ids") or []),
            focus_labels=list(br.get("focus_labels") or []),
            summary=str(br.get("summary") or ""),
            suggested_practice=list(br.get("suggested_practice") or []),
        )
    return SpeakingPromotionAssessmentResultOut(
        assessment_id=str(safe["assessment_id"]),
        blueprint_id=str(safe["blueprint_id"]),
        attempt_id=str(safe["attempt_id"]),
        outcome=str(safe["outcome"]),
        status=assessment.status.value,
        ready_for_official_promotion=bool(safe.get("ready_for_official_promotion")),
        message=str(safe.get("message") or ""),
        blocked_by_required_competency=bool(safe.get("blocked_by_required_competency")),
        bridge_recommendation=bridge,
        completed_at=str(safe.get("completed_at") or ""),
    )


def _failure_http(code: SpaCreateFailureCode | None) -> tuple[int, str]:
    if code in (
        SpaCreateFailureCode.unlock_not_granted,
        SpaCreateFailureCode.stale_fingerprint,
        SpaCreateFailureCode.cefr_mismatch,
    ):
        return 403, "Speaking promotion assessment is not available."
    if code == SpaCreateFailureCode.unsupported_target:
        return 409, "Speaking promotion assessment target is unsupported."
    return 503, "Speaking promotion assessment is temporarily unavailable."


def _exec_http(code: SpaExecutionFailureCode | None) -> tuple[int, str]:
    if code in (
        SpaExecutionFailureCode.assessment_not_found,
    ):
        return 404, "Assessment not found."
    if code in (
        SpaExecutionFailureCode.assessment_not_startable,
        SpaExecutionFailureCode.retry_not_eligible,
        SpaExecutionFailureCode.assessment_not_in_progress,
        SpaExecutionFailureCode.attempt_mismatch,
        SpaExecutionFailureCode.task_not_current,
        SpaExecutionFailureCode.task_already_terminal,
        SpaExecutionFailureCode.invalid_execution_mode,
        SpaExecutionFailureCode.validation_failed,
    ):
        return 409, "Assessment action not allowed."
    if code == SpaExecutionFailureCode.evaluation_failed:
        return 503, "Assessment evaluation temporarily unavailable."
    return 503, "Speaking promotion assessment is temporarily unavailable."


async def _load_locked_payload(
    db: AsyncSession, *, student_id: int, language_id: int
) -> tuple[Any, dict]:
    row = await lock_speaking_progression_row(db, student_id=student_id, language_id=language_id)
    if row is None:
        raise SpeakingPromotionAssessmentApiError(503, {"message": "Progression unavailable."})
    return row, dict(row.promotion_readiness_json or {})


async def _persist_assessment(
    db: AsyncSession,
    row: Any,
    payload: dict,
    assessment: SpeakingPromotionAssessment,
) -> SpeakingPromotionAssessment:
    payload = persist_active_assessment(payload, assessment, retire_previous_active_as_terminal=False)
    row.promotion_readiness_json = payload
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return assessment


async def get_speaking_promotion_assessment_status(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
) -> SpeakingPromotionAssessmentStatusOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    engines = await run_speaking_progression_engines(
        db, student_id=student_id, language_id=language_id
    )
    authority = _authority_from_engines(engines)
    row = await lock_speaking_progression_row(db, student_id=student_id, language_id=language_id)
    payload = dict(row.promotion_readiness_json or {}) if row is not None else {}
    active = get_active_assessment(payload)

    if active is not None:
        safe = active.to_student_safe_dict(include_tasks=False)
        return SpeakingPromotionAssessmentStatusOut(
            available=True,
            spa_unlocked=authority.spa_unlocked,
            source_cefr=active.blueprint.source_cefr,
            target_cefr=active.blueprint.target_cefr,
            estimated_duration_seconds=estimated_duration_seconds(),
            status=str(safe["status"]),
            assessment_id=str(safe["assessment_id"]),
            blueprint_id=str(safe["blueprint_id"]),
            attempt_id=safe.get("attempt_id"),
            task_count=int(safe["task_count"]),
            has_interaction_coverage_gaps=bool(safe.get("has_interaction_coverage_gaps")),
            message="Your next-level speaking assessment is ready.",
        )

    if not authority.spa_unlocked:
        proj = engines.readiness.to_student_safe_dict()
        return SpeakingPromotionAssessmentStatusOut(
            available=False,
            spa_unlocked=False,
            source_cefr=authority.official_cefr,
            target_cefr=authority.target_cefr,
            estimated_duration_seconds=estimated_duration_seconds(),
            status="locked",
            message=str(proj.get("message") or "Keep building speaking skills."),
        )

    return SpeakingPromotionAssessmentStatusOut(
        available=True,
        spa_unlocked=True,
        source_cefr=authority.official_cefr,
        target_cefr=authority.target_cefr,
        estimated_duration_seconds=estimated_duration_seconds(),
        status="available",
        message="You can start the next-level speaking assessment.",
    )


async def create_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
) -> SpeakingPromotionAssessmentCreateOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    engines = await run_speaking_progression_engines(
        db, student_id=student_id, language_id=language_id
    )
    authority = _authority_from_engines(engines)

    result = create_speaking_promotion_assessment(
        authority,
        expected_official_cefr=authority.official_cefr,
        fresh_readiness_snapshot_fingerprint=authority.readiness_snapshot_fingerprint,
        fresh_source_stage_signal_fingerprint=authority.source_stage_signal_fingerprint,
    )
    if not result.ok or result.assessment is None:
        status, msg = _failure_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": (result.failure_code.value if result.failure_code else "unavailable"),
            },
        )

    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    _ = speaking_promotion_bucket_from_payload(payload)
    payload = persist_active_assessment(
        payload, result.assessment, retire_previous_active_as_terminal=True
    )
    row.promotion_readiness_json = payload
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return _assessment_create_out(result.assessment)


async def get_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
) -> SpeakingPromotionAssessmentGetOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row = await lock_speaking_progression_row(db, student_id=student_id, language_id=language_id)
    payload = dict(row.promotion_readiness_json or {}) if row is not None else {}
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    return _assessment_get_out(assessment)


async def start_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
    force_new_attempt: bool = False,
) -> SpeakingPromotionAssessmentStartOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})

    result = start_speaking_promotion_assessment(
        assessment, force_new_attempt=force_new_attempt
    )
    if not result.ok or result.assessment is None:
        status, msg = _exec_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": result.failure_code.value if result.failure_code else "unavailable",
            },
        )
    await _persist_assessment(db, row, payload, result.assessment)
    a = result.assessment
    assert a.session is not None and a.current_attempt is not None
    cur_id = current_task_id(a)
    cur_task = next((t for t in a.blueprint.tasks if t.task_id == cur_id), None)
    return SpeakingPromotionAssessmentStartOut(
        assessment_id=a.assessment_id,
        blueprint_id=a.blueprint_id,
        attempt_id=a.current_attempt.attempt_id,
        session_id=a.session.session_id,
        status=a.status.value,
        current_task_index=a.session.current_task_index,
        current_task=_task_out_from_model(cur_task) if cur_task else None,
        task_count=len(a.blueprint.tasks),
        resumed=bool(result.idempotent),
    )


async def submit_speaking_promotion_assessment_task_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
    body: SpeakingPromotionAssessmentSubmitIn,
) -> SpeakingPromotionAssessmentSubmitOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    engines = await run_speaking_progression_engines(
        db, student_id=student_id, language_id=language_id
    )
    official = str(engines.readiness.official_cefr)
    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    if assessment.session is None or assessment.current_attempt is None:
        raise SpeakingPromotionAssessmentApiError(
            409, {"message": "Assessment is not in progress.", "code": "assessment_not_in_progress"}
        )

    task = next((t for t in assessment.blueprint.tasks if t.task_id == body.task_id), None)
    if task is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Task not found."})

    try:
        score, _evaluation = await evaluate_spa_task_with_s7(
            db=db,
            student_id=student_id,
            language_id=language_id,
            official_cefr=official,
            session_id=assessment.session.session_id,
            attempt_id=assessment.current_attempt.attempt_id,
            task=task,
            transcript_text=body.transcript_text or "",
            media_object_id=body.media_object_id,
            quarantine_apply=True,
        )
    except Exception as exc:
        raise SpeakingPromotionAssessmentApiError(
            503,
            {
                "message": "Assessment evaluation temporarily unavailable.",
                "code": SpaExecutionFailureCode.evaluation_failed.value,
                "detail": type(exc).__name__,
            },
        ) from exc

    result = record_task_score(
        assessment,
        task_id=body.task_id,
        score=score,
        attempt_id=body.attempt_id or assessment.current_attempt.attempt_id,
    )
    if not result.ok or result.assessment is None:
        status, msg = _exec_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": result.failure_code.value if result.failure_code else "unavailable",
            },
        )
    await _persist_assessment(db, row, payload, result.assessment)
    a = result.assessment
    next_id = current_task_id(a)
    all_done = next_id is None and a.session is not None and a.session.current_task_index >= len(
        a.blueprint.tasks
    )
    return SpeakingPromotionAssessmentSubmitOut(
        assessment_id=a.assessment_id,
        attempt_id=a.current_attempt.attempt_id if a.current_attempt else "",
        task_id=body.task_id,
        status=a.status.value,
        current_task_index=a.session.current_task_index if a.session else None,
        next_task_id=next_id,
        all_tasks_complete=all_done,
        student_safe_summary=score.student_safe_summary,
        idempotent=bool(result.idempotent),
    )


async def complete_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
) -> SpeakingPromotionAssessmentCompleteOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    result = complete_speaking_promotion_assessment(assessment)
    if not result.ok or result.assessment is None:
        status, msg = _exec_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": result.failure_code.value if result.failure_code else "unavailable",
            },
        )
    await _persist_assessment(db, row, payload, result.assessment)
    out = _result_out(result.assessment)
    return SpeakingPromotionAssessmentCompleteOut(**out.model_dump())


async def get_speaking_promotion_assessment_result_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
) -> SpeakingPromotionAssessmentResultOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row = await lock_speaking_progression_row(db, student_id=student_id, language_id=language_id)
    payload = dict(row.promotion_readiness_json or {}) if row is not None else {}
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    return _result_out(assessment)


async def abandon_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
) -> SpeakingPromotionAssessmentResultOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    result = abandon_speaking_promotion_assessment(assessment)
    if not result.ok or result.assessment is None:
        status, msg = _exec_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": result.failure_code.value if result.failure_code else "unavailable",
            },
        )
    await _persist_assessment(db, row, payload, result.assessment)
    return _result_out(result.assessment)


async def timeout_speaking_promotion_assessment_api(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    assessment_id: str,
) -> SpeakingPromotionAssessmentResultOut:
    await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    row, payload = await _load_locked_payload(db, student_id=student_id, language_id=language_id)
    assessment = find_assessment_in_payload(payload, assessment_id)
    if assessment is None:
        raise SpeakingPromotionAssessmentApiError(404, {"message": "Assessment not found."})
    result = timeout_speaking_promotion_assessment(assessment)
    if not result.ok or result.assessment is None:
        status, msg = _exec_http(result.failure_code)
        raise SpeakingPromotionAssessmentApiError(
            status,
            {
                "message": result.student_safe_message or msg,
                "code": result.failure_code.value if result.failure_code else "unavailable",
            },
        )
    await _persist_assessment(db, row, payload, result.assessment)
    return _result_out(result.assessment)
