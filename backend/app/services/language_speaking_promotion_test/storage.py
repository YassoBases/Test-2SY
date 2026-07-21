"""Bounded SPA assessment persistence under promotion_readiness_json (S18/S19).

CORRECTION 1 (S18): never unbounded blueprints_by_id.
S19: persist active_assessment + most_recent_terminal_assessment
(with embedded frozen blueprint). Legacy active_blueprint keys are lifted
on read for compatibility.
"""

from __future__ import annotations

from typing import Any

from app.services.language_speaking_promotion_test.assessment import (
    build_speaking_promotion_assessment,
)
from app.services.language_speaking_promotion_test.execution_types import (
    MAX_ATTEMPT_HISTORY,
    SpeakingPromotionAssessment,
)
from app.services.language_speaking_promotion_test.policy import MAX_PERSISTED_BLUEPRINTS
from app.services.language_speaking_promotion_test.types import (
    SpaBlueprintStatus,
    SpeakingPromotionAssessmentBlueprint,
)

SPEAKING_PROMOTION_ASSESSMENTS_KEY = "speaking_promotion_assessments"

_ALLOWED_BUCKET_KEYS = frozenset(
    {
        "active_assessment",
        "most_recent_terminal_assessment",
        # Legacy S18 keys — accepted on read, stripped on write.
        "active_blueprint",
        "most_recent_terminal_blueprint",
    }
)

_TERMINAL_STATUSES = frozenset(
    {
        SpaBlueprintStatus.completed.value,
        SpaBlueprintStatus.abandoned.value,
        SpaBlueprintStatus.unavailable.value,
    }
)


def empty_assessments_bucket() -> dict[str, Any]:
    return {
        "active_assessment": None,
        "most_recent_terminal_assessment": None,
    }


def _lift_legacy_blueprint(raw: dict[str, Any] | None) -> SpeakingPromotionAssessment | None:
    if not isinstance(raw, dict):
        return None
    # Already an assessment envelope.
    if "blueprint" in raw and "assessment_id" in raw:
        return SpeakingPromotionAssessment.from_dict(raw)
    # Legacy: raw is a blueprint dict (possibly with deprecated assessment_id == blueprint_id).
    try:
        bp = SpeakingPromotionAssessmentBlueprint.from_dict(raw)
    except (KeyError, TypeError, ValueError):
        return None
    # Prefer distinct assessment_id when legacy field equals blueprint_id.
    legacy_aid = str(raw.get("assessment_id") or "")
    aid = None if (not legacy_aid or legacy_aid == bp.blueprint_id) else legacy_aid
    assessment = build_speaking_promotion_assessment(bp, assessment_id=aid, created_at=bp.created_at)
    # Preserve terminal/status from legacy blueprint status field.
    status = SpaBlueprintStatus(str(raw.get("status") or bp.status.value))
    return SpeakingPromotionAssessment(
        assessment_id=assessment.assessment_id,
        blueprint_id=assessment.blueprint_id,
        blueprint=assessment.blueprint,
        status=status,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
        mandatory_requirements=assessment.mandatory_requirements,
        evidence_source=assessment.evidence_source,
        schema_version=assessment.schema_version,
    )


def assessments_bucket_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return empty_assessments_bucket()
    raw = payload.get(SPEAKING_PROMOTION_ASSESSMENTS_KEY)
    if not isinstance(raw, dict):
        return empty_assessments_bucket()

    active = raw.get("active_assessment")
    if not isinstance(active, dict):
        active_lifted = _lift_legacy_blueprint(
            raw.get("active_blueprint") if isinstance(raw.get("active_blueprint"), dict) else None
        )
        active = active_lifted.to_dict() if active_lifted else None
    terminal = raw.get("most_recent_terminal_assessment")
    if not isinstance(terminal, dict):
        term_lifted = _lift_legacy_blueprint(
            raw.get("most_recent_terminal_blueprint")
            if isinstance(raw.get("most_recent_terminal_blueprint"), dict)
            else None
        )
        terminal = term_lifted.to_dict() if term_lifted else None
    return {
        "active_assessment": active if isinstance(active, dict) else None,
        "most_recent_terminal_assessment": terminal if isinstance(terminal, dict) else None,
    }


def merge_assessments_into_payload(
    payload: dict[str, Any] | None,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    out = dict(payload) if isinstance(payload, dict) else {}
    clean = {
        "active_assessment": bucket.get("active_assessment"),
        "most_recent_terminal_assessment": bucket.get("most_recent_terminal_assessment"),
    }
    out[SPEAKING_PROMOTION_ASSESSMENTS_KEY] = clean
    return out


def count_persisted_blueprints(bucket: dict[str, Any]) -> int:
    """Count distinct assessment/blueprint slots (≤2)."""
    n = 0
    if isinstance(bucket.get("active_assessment"), dict) or isinstance(bucket.get("active_blueprint"), dict):
        n += 1
    if isinstance(bucket.get("most_recent_terminal_assessment"), dict) or isinstance(
        bucket.get("most_recent_terminal_blueprint"), dict
    ):
        n += 1
    return n


def assert_bucket_bounded(bucket: dict[str, Any]) -> None:
    """Raise if the JSONB SPA collection is unbounded or exceeds retention policy."""
    if "blueprints_by_id" in bucket and bucket["blueprints_by_id"]:
        raise ValueError("unbounded blueprints_by_id is forbidden in S18 SPA persistence")
    if count_persisted_blueprints(bucket) > MAX_PERSISTED_BLUEPRINTS:
        raise ValueError(
            f"SPA blueprint retention exceeded bound of {MAX_PERSISTED_BLUEPRINTS}"
        )
    for key, val in bucket.items():
        if key in _ALLOWED_BUCKET_KEYS:
            continue
        if isinstance(val, (list, dict)) and val:
            raise ValueError(f"unexpected SPA archive key '{key}' — retention must stay bounded")


def get_active_assessment(payload: dict[str, Any] | None) -> SpeakingPromotionAssessment | None:
    bucket = assessments_bucket_from_payload(payload)
    raw = bucket.get("active_assessment")
    if not isinstance(raw, dict):
        return None
    return SpeakingPromotionAssessment.from_dict(raw)


def get_active_blueprint(payload: dict[str, Any] | None) -> SpeakingPromotionAssessmentBlueprint | None:
    """Backward-compatible: return the frozen blueprint from the active assessment."""
    assessment = get_active_assessment(payload)
    return assessment.blueprint if assessment is not None else None


def persist_active_assessment(
    payload: dict[str, Any] | None,
    assessment: SpeakingPromotionAssessment,
    *,
    retire_previous_active_as_terminal: bool = True,
) -> dict[str, Any]:
    """Store assessment as active; optionally retire previous active → terminal."""
    bucket = assessments_bucket_from_payload(payload)
    previous = bucket.get("active_assessment")
    if retire_previous_active_as_terminal and isinstance(previous, dict):
        prev_status = str(previous.get("status") or "")
        if prev_status in _TERMINAL_STATUSES or prev_status in (
            SpaBlueprintStatus.not_started.value,
            SpaBlueprintStatus.available.value,
            SpaBlueprintStatus.in_progress.value,
        ):
            # Cap attempt history on the retired record.
            retired = dict(previous)
            hist = retired.get("attempt_history")
            if isinstance(hist, list) and len(hist) > MAX_ATTEMPT_HISTORY:
                retired["attempt_history"] = hist[-MAX_ATTEMPT_HISTORY:]
            bucket["most_recent_terminal_assessment"] = retired
    data = assessment.to_dict()
    hist = data.get("attempt_history")
    if isinstance(hist, list) and len(hist) > MAX_ATTEMPT_HISTORY:
        data["attempt_history"] = hist[-MAX_ATTEMPT_HISTORY:]
    bucket["active_assessment"] = data
    assert_bucket_bounded(bucket)
    return merge_assessments_into_payload(payload, bucket)


def persist_active_blueprint(
    payload: dict[str, Any] | None,
    blueprint: SpeakingPromotionAssessmentBlueprint,
    *,
    retire_previous_active_as_terminal: bool = True,
) -> dict[str, Any]:
    """S18-compatible entry: wrap blueprint in a fresh assessment envelope."""
    assessment = build_speaking_promotion_assessment(blueprint)
    return persist_active_assessment(
        payload,
        assessment,
        retire_previous_active_as_terminal=retire_previous_active_as_terminal,
    )


def mark_active_terminal(
    payload: dict[str, Any] | None,
    *,
    status: SpaBlueprintStatus,
) -> dict[str, Any]:
    """Move active assessment → most_recent_terminal with terminal status."""
    bucket = assessments_bucket_from_payload(payload)
    active = bucket.get("active_assessment")
    if not isinstance(active, dict):
        return merge_assessments_into_payload(payload, bucket)
    terminal = dict(active)
    terminal["status"] = status.value
    bucket["most_recent_terminal_assessment"] = terminal
    bucket["active_assessment"] = None
    assert_bucket_bounded(bucket)
    return merge_assessments_into_payload(payload, bucket)


def find_assessment_in_payload(
    payload: dict[str, Any] | None,
    assessment_id: str,
) -> SpeakingPromotionAssessment | None:
    """Lookup by assessment_id (preferred) or blueprint_id (compat)."""
    bucket = assessments_bucket_from_payload(payload)
    for key in ("active_assessment", "most_recent_terminal_assessment"):
        raw = bucket.get(key)
        if not isinstance(raw, dict):
            continue
        try:
            assessment = SpeakingPromotionAssessment.from_dict(raw)
        except (KeyError, TypeError, ValueError):
            continue
        if assessment.assessment_id == assessment_id or assessment.blueprint_id == assessment_id:
            return assessment
    return None
