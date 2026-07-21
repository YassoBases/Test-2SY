"""Developer-only shortcut: skip language placement and start learning from a CEFR.

Mirrors the post-placement init from legacy ``submit_attempt`` (levels + progression
+ learning path) without scoring, fake mastery, or seeding the learner model.

Gated by ``settings.DEBUG`` at the API layer — never call from production routes.

Default path is DB-only and fast. Claude package authoring is NOT done here;
the Speaking page starts today's Educational Case after redirect.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.analytics import LanguageAnalytics
from app.models.language.enums import LanguageLevel, LanguageOnboardingStep, LanguageSkill
from app.models.language.progression import LanguageProgression
from app.services.language_learning_path_service import generate_learning_path
from app.services.language_placement_service import _ensure_profile
from app.services.language_progression_service import (
    ensure_progression_row,
    sync_progression_from_skill_levels,
    upsert_official_levels,
)
from app.services.language_speaking_case_personalization.memory import SPEAKING_CASE_MEMORY_KEY
from app.services.language_speaking_curriculum_engine.progression_memory import (
    merge_progression_ledger_into_payload,
)
from app.services.language_speaking_curriculum_engine.progression_types import (
    ProgressionMasteryLedger,
)
from app.services.language_speaking_curriculum_engine.progression_selector import (
    resolve_progression_decision,
)
from app.services.language_speaking_diagnostic.selector import select_speaking_target
from app.services.language_speaking_educational_package.storage_index import (
    SPEAKING_ELP_INDEX_KEY,
    empty_elp_index,
)
from app.services.language_speaking_knowledge_model.storage import (
    SPEAKING_BUCKET_KEY,
    empty_knowledge_model,
    merge_knowledge_model_into_speaking_bucket,
)
from app.services.language_subscription_service import get_default_language


def _parse_cefr(raw: str) -> LanguageLevel:
    value = (raw or "A1").strip().upper()
    try:
        level = LanguageLevel(value)
    except ValueError as exc:
        raise ValueError(f"Unsupported starting CEFR: {raw!r}") from exc
    if level == LanguageLevel.C2:
        # UI offers A1–C1; clamp C2 to C1 for a safe curriculum entry.
        return LanguageLevel.C1
    return level


async def _reset_speaking_runtime_scratch(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    starting: LanguageLevel,
) -> tuple[str, str | None]:
    """Empty KM + empty curriculum ledger + clear ELP/case memory; stages → 1."""
    row = await ensure_progression_row(db, student_id=student_id, language_id=language_id)
    if row is None:
        row = LanguageProgression(student_id=student_id, language_id=language_id)
        db.add(row)
        await db.flush()

    row.learning_stage_reading = 1
    row.learning_stage_listening = 1
    row.learning_stage_writing = 1
    row.learning_stage_speaking = 1

    empty_km = empty_knowledge_model(student_id=student_id, language_id=language_id)
    speaking_bucket = merge_knowledge_model_into_speaking_bucket({}, empty_km)

    payload: dict = dict(row.promotion_readiness_json or {})
    payload[SPEAKING_BUCKET_KEY] = speaking_bucket
    payload[SPEAKING_ELP_INDEX_KEY] = empty_elp_index()
    payload.pop(SPEAKING_CASE_MEMORY_KEY, None)
    payload = merge_progression_ledger_into_payload(payload, ProgressionMasteryLedger())
    row.promotion_readiness_json = payload
    flag_modified(row, "promotion_readiness_json")
    await db.flush()

    decision = resolve_progression_decision(cefr=starting.value, ledger=ProgressionMasteryLedger())
    # Deterministic primary target (no LLM) — same sparse-evidence path as journey bootstrap.
    rec = select_speaking_target(empty_km, official_cefr=starting.value, speaking_goal="general_english")
    return decision.node.node_id, rec.primary_target_skill_id


async def skip_placement_from_scratch(
    db: AsyncSession,
    *,
    student_id: int,
    starting_cefr: str = "A1",
    bootstrap_learning: bool = False,
) -> dict:
    """Mark placement complete and initialize empty learner runtime at ``starting_cefr``.

    Fast path (default): DB writes only — no Claude, no package generation.
    Optional ``bootstrap_learning`` still exists for rare local scripts; the
    Developer UI never enables it.
    """
    starting = _parse_cefr(starting_cefr)
    language = await get_default_language(db)
    profile = await _ensure_profile(db, student_id=student_id, language_id=language.id)

    now = datetime.now(timezone.utc)
    profile.placement_completed_at = now
    profile.last_assessment_date = now
    profile.next_allowed_retake_date = now + timedelta(days=90)
    profile.onboarding_step = LanguageOnboardingStep.dashboard

    skill_levels = {skill: starting for skill in LanguageSkill}

    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": language.id})
    if not analytics:
        analytics = LanguageAnalytics(student_id=student_id, language_id=language.id)
        db.add(analytics)
        await db.flush()
    analytics.reading_level = starting
    analytics.listening_level = starting
    analytics.writing_level = starting
    analytics.speaking_level = starting
    analytics.overall_level_internal = starting

    await sync_progression_from_skill_levels(
        db,
        student_id=student_id,
        language_id=language.id,
        skill_levels=skill_levels,
        overall=starting,
        source="dev_skip_placement",
    )
    # Speaking journey reads Official CEFR from the progression row. Force the
    # dual-write so a selected level (e.g. B1) works even when
    # LANG_PROGRESSION_ENABLED is false in local .env.
    await upsert_official_levels(
        db,
        student_id=student_id,
        language_id=language.id,
        reading=starting,
        listening=starting,
        writing=starting,
        speaking=starting,
        overall=starting,
        source="dev_skip_placement",
        force=True,
    )

    entry_node_id, primary_skill = await _reset_speaking_runtime_scratch(
        db,
        student_id=student_id,
        language_id=language.id,
        starting=starting,
    )

    path = await generate_learning_path(
        db,
        student_id=student_id,
        language_id=language.id,
        assessment_id=None,
        overall_level=starting,
        skill_levels=skill_levels,
    )

    learning_bootstrapped = False
    package_id: str | None = None
    lesson_opened = False
    bootstrap_warning: str | None = None

    if bootstrap_learning:
        # Optional slow path — not used by the Developer UI.
        try:
            from app.services.language_speaking_runtime_api.ensure_learning import (
                RuntimeIntegrationError,
                start_learning_runtime,
            )

            started = await start_learning_runtime(
                db,
                student_id=student_id,
                language_id=language.id,
                author_mode="auto",
                use_cache=True,
                force_restart_lesson=True,
            )
            learning_bootstrapped = bool(started.get("success"))
            pkg = started.get("package") or {}
            package_id = pkg.get("package_id")
            lesson_opened = bool(started.get("lesson"))
        except Exception as exc:  # noqa: BLE001 — DX path must still unlock placement
            bootstrap_warning = str(getattr(exc, "detail", None) or exc)

    await db.flush()

    return {
        "ok": True,
        "placement_completed": True,
        "starting_cefr": starting.value,
        "official_levels": {
            "reading": starting.value,
            "listening": starting.value,
            "writing": starting.value,
            "speaking": starting.value,
            "overall": starting.value,
        },
        "learning_path_id": path.id if path else None,
        "curriculum_entry_node_id": entry_node_id,
        "primary_target_skill_id": primary_skill,
        "knowledge_model_initialized": True,
        # Planner is computed lazily on next hub/daily-plan fetch after placement unlock.
        "daily_plan_ready": True,
        "learning_bootstrapped": learning_bootstrapped,
        "package_id": package_id,
        "lesson_opened": lesson_opened,
        "bootstrap_warning": bootstrap_warning,
        "redirect": "/student/languages/speaking",
    }
