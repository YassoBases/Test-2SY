"""Verify Speaking S20 — official CEFR promotion engine.

S20 is the sole runtime writer of official_speaking_cefr after SPA PASS.
Consumes S19 ready_for_official_promotion; never re-scores SPA.

Usage (from backend/):
    python scripts/verify_speaking_s20_official_promotion.py
"""

from __future__ import annotations

import ast
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.language.enums import LanguageLevel
from app.services.language_speaking.ownership import ALLOWED_PACKAGE_DEPENDENCIES
from app.services.language_speaking_official_promotion import (
    SPEAKING_OFFICIAL_PROMOTION_VERSION,
    apply_speaking_official_promotion,
)
from app.services.language_speaking_official_promotion.ownership_guard import (
    AUTHORIZED_SPEAKING_CEFR_WRITERS,
    verify_speaking_cefr_ownership,
)
from app.services.language_speaking_official_promotion.storage import (
    append_speaking_promotion_record,
    assessment_is_consumed,
    find_promotion_pass_assessment,
    is_attempt_already_promoted,
    mark_assessment_consumed_in_payload,
    promotions_bucket_from_payload,
    reset_speaking_promotion_readiness_projection,
)
from app.services.language_speaking_promotion_test import (
    SpaAssessmentOutcome,
    SpaTaskScoreSummary,
    SpaUnlockAuthority,
    complete_speaking_promotion_assessment,
    create_speaking_promotion_assessment,
    persist_active_assessment,
    record_task_score,
    start_speaking_promotion_assessment,
)

PASS = 0
FAIL = 0
BACKEND = Path(__file__).resolve().parents[1]


def check(label: str, cond: bool) -> None:
    global PASS, FAIL
    safe = label.replace("→", "->").replace("–", "-")
    if cond:
        PASS += 1
        print(f"  OK  {safe}")
    else:
        FAIL += 1
        print(f" FAIL {safe}")


def _authority(**overrides) -> SpaUnlockAuthority:
    data = dict(
        spa_unlocked=True,
        official_cefr="A2",
        target_cefr="B1",
        readiness_snapshot_fingerprint="ready_fp_aaaaaaaaaaaaaaaaaaaa",
        source_stage_signal_fingerprint="stage_fp_bbbbbbbbbbbbbbbbbbbb",
        unlock_fingerprint="unlock_fp_cccccccccccccccccccc",
        hard_blockers_empty=True,
        stability_requirements_passed=True,
        current_stage_advanced=True,
    )
    data.update(overrides)
    return SpaUnlockAuthority(**data)


def _score(task, *, eligible=True, semantic=True, readiness=0.85):
    return SpaTaskScoreSummary(
        task_id=task.task_id,
        task_order=task.task_order,
        task_family=task.task_family.value,
        evaluation_id=f"eval_{task.task_id}",
        overall_readiness=readiness,
        completion_eligible=eligible,
        semantic_task_met=semantic,
        target_skill_ids=task.target_skill_ids,
        strong_skills=task.target_skill_ids[:1],
    )


def _build_pass_assessment_payload(*, unlock_fp: str = "unlock_s20_" + "a" * 16):
    created = create_speaking_promotion_assessment(_authority(unlock_fingerprint=unlock_fp))
    assert created.ok and created.assessment is not None
    started = start_speaking_promotion_assessment(created.assessment)
    assert started.ok and started.assessment is not None
    a = started.assessment
    for task in sorted(a.blueprint.tasks, key=lambda t: t.task_order):
        scored = record_task_score(a, task_id=task.task_id, score=_score(task))
        assert scored.ok and scored.assessment is not None
        a = scored.assessment
    completed = complete_speaking_promotion_assessment(a)
    assert completed.ok and completed.assessment is not None
    assert completed.assessment.result is not None
    assert completed.assessment.result.outcome == SpaAssessmentOutcome.PASS
    assert completed.assessment.result.ready_for_official_promotion is True
    payload = persist_active_assessment({}, completed.assessment)
    return payload, completed.assessment


def _fake_row(payload: dict, *, speaking: LanguageLevel = LanguageLevel.A2):
    return SimpleNamespace(
        official_speaking_cefr=speaking,
        official_reading_cefr=LanguageLevel.A2,
        official_listening_cefr=LanguageLevel.A2,
        official_writing_cefr=LanguageLevel.A2,
        official_overall_cefr=LanguageLevel.A2,
        learning_stage_speaking=3,
        promotion_readiness_score=80,
        promotion_readiness_json=payload,
        last_promotion_at=None,
        version=1,
    )


async def _promote(row, **kwargs):
    fake_db = SimpleNamespace(flush=AsyncMock())
    with (
        patch(
            "app.services.language_speaking_official_promotion.engine.record_official_speaking_promotion_event",
            new_callable=AsyncMock,
            return_value=1,
        ),
        patch(
            "app.services.language_speaking_official_promotion.engine.flag_modified",
            lambda *_a, **_k: None,
        ),
    ):
        return await apply_speaking_official_promotion(
            fake_db,
            student_id=1,
            language_id=1,
            locked_row=row,
            **kwargs,
        )


def test_storage_and_pass_discovery() -> None:
    print("\n--- storage + PASS discovery ---")
    payload, assessment = _build_pass_assessment_payload()
    found = find_promotion_pass_assessment(payload)
    check("1. finds PASS ready assessment", found is not None and found.assessment_id == assessment.assessment_id)
    check("2. ready_for_official_promotion", found is not None and found.result is not None and found.result.ready_for_official_promotion)

    attempt_id = assessment.result.attempt_id
    check("3. not yet promoted attempt", not is_attempt_already_promoted(payload, attempt_id))

    consumed_payload = mark_assessment_consumed_in_payload(
        payload, assessment_id=assessment.assessment_id, attempt_id=attempt_id
    )
    check("4. consumed flag set", assessment_is_consumed(consumed_payload, assessment.assessment_id))
    found_after = find_promotion_pass_assessment(consumed_payload)
    check("5. consumed excluded from eligible find", found_after is None)

    with_promo = append_speaking_promotion_record(
        consumed_payload,
        assessment_id=assessment.assessment_id,
        attempt_id=attempt_id,
        old_cefr="A2",
        new_cefr="B1",
    )
    check("6. attempt recorded as promoted", is_attempt_already_promoted(with_promo, attempt_id))
    bucket = promotions_bucket_from_payload(with_promo)
    check("7. last_promotion persisted", isinstance(bucket.get("last_promotion"), dict))

    reset = reset_speaking_promotion_readiness_projection(with_promo, new_official_cefr="B1")
    proj = (reset.get("speaking_promotion") or {}).get("student_projection") or {}
    check("8. readiness unlock cleared", proj.get("spa_unlocked") is False)
    check("9. projection official cefr B1", str(proj.get("official_cefr")).upper() == "B1")


def test_engine_pass_and_idempotency() -> None:
    print("\n--- engine PASS / idempotency ---")
    payload, assessment = _build_pass_assessment_payload(unlock_fp="unlock_eng_" + "b" * 16)
    row = _fake_row(payload)
    result = asyncio.run(_promote(row))
    check("10. promote success", result.success)
    check("11. CEFR A2->B1", result.old_cefr == "A2" and result.new_cefr == "B1")
    check("12. row official_speaking_cefr B1", row.official_speaking_cefr == LanguageLevel.B1)
    check("13. stage reset to foundation", int(row.learning_stage_speaking) == 1)
    check("14. readiness score cleared", int(row.promotion_readiness_score or 0) == 0)
    check("15. last_promotion_at set", row.last_promotion_at is not None)
    check("16. version bumped", int(row.version) == 2)
    check("17. ready_for_new_journey", result.ready_for_new_journey is True)
    check(
        "18. assessment consumed in JSON",
        assessment_is_consumed(row.promotion_readiness_json, assessment.assessment_id),
    )

    # Replay
    replay = asyncio.run(_promote(row, assessment_id=assessment.assessment_id))
    check("19. replay success idempotent", replay.success and replay.already_promoted)
    check("20. CEFR not double-write (still B1)", row.official_speaking_cefr == LanguageLevel.B1)
    check("21. version not bumped again beyond first", int(row.version) == 2)


def test_engine_denials() -> None:
    print("\n--- engine denials ---")
    payload, assessment = _build_pass_assessment_payload(unlock_fp="unlock_den_" + "c" * 16)

    # Stale source CEFR
    stale_row = _fake_row(payload, speaking=LanguageLevel.B1)
    stale = asyncio.run(_promote(stale_row))
    check("22. stale source denied", not stale.success and "stale" in stale.reason.lower())

    # Non-PASS FAIL assessment
    created = create_speaking_promotion_assessment(_authority(unlock_fingerprint="unlock_fail_" + "d" * 16))
    assert created.assessment is not None
    started = start_speaking_promotion_assessment(created.assessment)
    assert started.assessment is not None
    a = started.assessment
    for task in sorted(a.blueprint.tasks, key=lambda t: t.task_order):
        semantic = not task.spontaneous_production_required
        scored = record_task_score(
            a, task_id=task.task_id, score=_score(task, eligible=True, semantic=semantic)
        )
        assert scored.assessment is not None
        a = scored.assessment
    fail_done = complete_speaking_promotion_assessment(a)
    assert fail_done.assessment is not None
    check("23. FAIL not ready", fail_done.assessment.result.outcome == SpaAssessmentOutcome.FAIL)
    fail_payload = persist_active_assessment({}, fail_done.assessment)
    fail_row = _fake_row(fail_payload)
    fail_res = asyncio.run(
        _promote(fail_row, assessment_id=fail_done.assessment.assessment_id)
    )
    check("24. FAIL promote denied", not fail_res.success and "pass" in fail_res.reason.lower())

    # Missing assessment
    empty_row = _fake_row({})
    missing = asyncio.run(_promote(empty_row))
    check("25. missing assessment denied", not missing.success)

    # Consumed assessment deny
    good_payload, good = _build_pass_assessment_payload(unlock_fp="unlock_cons_" + "e" * 16)
    consumed = mark_assessment_consumed_in_payload(
        good_payload,
        assessment_id=good.assessment_id,
        attempt_id=good.result.attempt_id,
    )
    # Also clear ready flag in object path is already done by mark
    cons_row = _fake_row(consumed)
    cons = asyncio.run(_promote(cons_row, assessment_id=good.assessment_id))
    check("26. consumed assessment denied", not cons.success)

    # Invalid target / skip: mutate blueprint target in payload
    skip_payload, skip_a = _build_pass_assessment_payload(unlock_fp="unlock_skip_" + "f" * 16)
    bucket = skip_payload["speaking_promotion_assessments"]
    active = dict(bucket["active_assessment"])
    bp = dict(active["blueprint"])
    bp["target_cefr"] = "C1"  # skip B1
    active["blueprint"] = bp
    if isinstance(active.get("result"), dict):
        # keep PASS flags but integrity gate + target path fail
        pass
    bucket["active_assessment"] = active
    skip_payload["speaking_promotion_assessments"] = bucket
    skip_row = _fake_row(skip_payload)
    skip = asyncio.run(_promote(skip_row))
    check("27. skip-level target denied", not skip.success)


def test_authority_and_contracts() -> None:
    print("\n--- authority + contracts ---")
    check("28. S20 version", SPEAKING_OFFICIAL_PROMOTION_VERSION.startswith("20."))
    deps = ALLOWED_PACKAGE_DEPENDENCIES["language_speaking_official_promotion"]
    check("29. ownership depends on promotion_test", "language_speaking_promotion_test" in deps)
    check("30. ownership depends on progression", "language_speaking_progression" in deps)

    app_root = BACKEND / "app"
    ok, unauthorized, missing = verify_speaking_cefr_ownership(app_root)
    check("31. no unauthorized CEFR writers", ok and not unauthorized)
    check(
        "32. engine authorized writer present",
        "app.services.language_speaking_official_promotion.engine" in AUTHORIZED_SPEAKING_CEFR_WRITERS,
    )
    check(
        "33. engine module not missing",
        "app.services.language_speaking_official_promotion.engine" not in missing,
    )

    # AST: promotion_test still never assigns official_speaking_cefr
    pkg = BACKEND / "app/services/language_speaking_promotion_test"
    assign = False
    for p in pkg.rglob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Attribute) and t.attr == "official_speaking_cefr":
                        assign = True
    check("34. S19 package no CEFR write", not assign)

    api = BACKEND / "app/api/language_speaking_official_promotion.py"
    check("35. promote API module exists", api.exists())
    api_text = api.read_text(encoding="utf-8")
    check("36. /promote route", "/promote" in api_text)

    router = (BACKEND / "app/api/router.py").read_text(encoding="utf-8")
    check("37. router registers S20", "language_speaking_official_promotion" in router)

    fe = (BACKEND.parent / "src/api/speakingPromotion.js").read_text(encoding="utf-8")
    check("38. FE promote client", "promoteSpeakingOfficialCefr" in fe and "/speaking/promote" in fe)

    eng = (BACKEND / "app/services/language_speaking_official_promotion/engine.py").read_text(encoding="utf-8")
    check("39. engine assigns official_speaking_cefr", "official_speaking_cefr" in eng)
    check("40. engine uses bottleneck overall", "bottleneck_level" in eng)


def run_flat_verifier(label: str, script: str, *, timeout_s: int = 600) -> bool:
    print(f"\n=== FLAT {label} ===", flush=True)
    env = {
        **os.environ,
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "PYTHONUNBUFFERED": "1",
        "SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS": "1",
    }
    log_path = BACKEND / "scripts" / f"_flat_{Path(script).stem}.log"
    with open(log_path, "w", encoding="utf-8", errors="replace") as logf:
        proc = subprocess.Popen(
            [sys.executable, "-u", str(BACKEND / "scripts" / script)],
            cwd=str(BACKEND),
            stdout=logf,
            stderr=subprocess.STDOUT,
            env=env,
        )
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    check=False,
                )
            else:
                proc.kill()
            try:
                proc.wait(timeout=30)
            except Exception:
                pass
            print(f"TIMEOUT after {timeout_s}s: {script}", flush=True)
            return False
    ok = proc.returncode == 0
    status = "OK" if ok else "FAIL"
    print(f"  {status}  {label} (exit={proc.returncode})", flush=True)
    if not ok:
        try:
            print(log_path.read_text(encoding="utf-8", errors="replace")[-3000:], flush=True)
        except OSError:
            pass
    return ok


FLAT_REGRESSION_CHAIN: tuple[tuple[str, str], ...] = (
    ("S0", "verify_speaking_s0_architecture.py"),
    ("S9", "verify_speaking_s9_adaptive_journey.py"),
    ("S10", "verify_speaking_s10_educational_missions.py"),
    ("S10.1", "verify_speaking_s101_mission_stabilization.py"),
    ("S11", "verify_speaking_s11_attempt_lineage.py"),
    ("S12", "verify_speaking_s12_journey_read_model.py"),
    ("S13", "verify_speaking_s13_live_budget.py"),
    ("S14", "verify_speaking_s14_alex_context_identity.py"),
    ("S15", "verify_speaking_s15_stage_signals.py"),
    ("S16", "verify_speaking_s16_transition_gate.py"),
    ("S17", "verify_speaking_s17_promotion_readiness.py"),
    ("S18", "verify_speaking_s18_promotion_assessment_blueprint.py"),
    ("S19", "verify_speaking_s19_promotion_assessment_execution.py"),
)


def run_s20_unit_suite() -> int:
    global PASS, FAIL
    print("=== Speaking S20 official promotion verifier ===\n", flush=True)
    test_storage_and_pass_discovery()
    test_engine_pass_and_idempotency()
    test_engine_denials()
    test_authority_and_contracts()
    print(f"\n=== S20 units: {PASS} passed, {FAIL} failed ===", flush=True)
    return FAIL


def main() -> int:
    if os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1":
        failed = run_s20_unit_suite()
        return 1 if failed else 0

    print("=== Speaking S20 FLAT regression runner ===\n", flush=True)
    for label, script in FLAT_REGRESSION_CHAIN:
        if not run_flat_verifier(label, script):
            print(f"\n=== STOPPED: flat regression failed at {label} ({script}) ===", flush=True)
            return 1

    print("\n=== FLAT S20 (this process) ===", flush=True)
    if run_s20_unit_suite() != 0:
        print("\n=== STOPPED: S20 unit suite failed ===", flush=True)
        return 1

    print("\n=== RESULT: all flat regressions + S20 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
