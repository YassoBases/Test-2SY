"""Verify Speaking S19 — SPA assessment execution, pass gates, evidence quarantine.

S19 owns distinct blueprint/assessment/attempt identities, dedicated SPA session,
task submit scoring via S7 summaries, aggregate + mandatory competency PASS gates,
FAIL bridge projection, and ready-for-S20 flag — never official_speaking_cefr.

Usage (from backend/):
    python scripts/verify_speaking_s19_promotion_assessment_execution.py
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.language_speaking.ownership import ALLOWED_PACKAGE_DEPENDENCIES
from app.services.language_speaking_evaluation_runtime.knowledge_bridge import (
    build_speaking_skill_observations,
)
from app.services.language_speaking_evaluation_runtime.knowledge_bridge_types import (
    SpeakingKnowledgeMutationStatus,
)
from app.services.language_speaking_evaluator.evaluation_result import (
    CompletionEligibilityFacts,
    DimensionEvidenceStatus,
    DimensionFacts,
    EvidenceSummaryFacts,
    ExplanationFacts,
    RevisionReadinessFacts,
    SpeakingEvaluationEngineResult,
)
from app.services.language_speaking_evaluator.input_types import (
    SpeakingGoalContext,
    SpeakingOfficialCefrContext,
    SpeakingTaskContext,
)
from app.services.language_speaking_knowledge_model.types import ObservationSourceType
from app.services.language_speaking_promotion_test import (
    SpaAssessmentOutcome,
    SpaTaskScoreSummary,
    SpaUnlockAuthority,
    abandon_speaking_promotion_assessment,
    assert_bucket_bounded,
    assessments_bucket_from_payload,
    complete_speaking_promotion_assessment,
    create_speaking_promotion_assessment,
    current_task_id,
    decide_spa_pass_gate,
    get_active_assessment,
    merge_assessments_into_payload,
    persist_active_assessment,
    record_task_score,
    spa_evidence_may_apply_to_mastery,
    start_speaking_promotion_assessment,
    timeout_speaking_promotion_assessment,
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


def _score(
    task,
    *,
    eligible: bool = True,
    semantic: bool = True,
    readiness: float = 0.8,
    evaluation_id: str | None = None,
) -> SpaTaskScoreSummary:
    return SpaTaskScoreSummary(
        task_id=task.task_id,
        task_order=task.task_order,
        task_family=task.task_family.value,
        evaluation_id=evaluation_id or f"eval_{task.task_id}",
        overall_readiness=readiness,
        completion_eligible=eligible,
        semantic_task_met=semantic,
        target_skill_ids=task.target_skill_ids,
        strong_skills=task.target_skill_ids[:1],
        weak_skills=(),
        student_safe_summary="ok",
    )


def _dim(name: str = "task_response") -> DimensionFacts:
    return DimensionFacts(
        dimension=name,
        status=DimensionEvidenceStatus.met,
        normalized_value=0.8,
        confidence=0.8,
        reason="ok",
        supporting_evidence_ids=(),
        limitations=(),
        score=0.8,
        weight=1.0,
        passed=True,
    )


def _fake_evaluation() -> SpeakingEvaluationEngineResult:
    task = SpeakingTaskContext(
        task_id="t1",
        task_type="monologue",
        task_prompt="p",
        task_instructions="i",
    )
    return SpeakingEvaluationEngineResult(
        evaluation_id="e1",
        student_id=1,
        language_id=1,
        session_id="s1",
        task_id="t1",
        attempt_id="a1",
        revision_number=1,
        evaluated_at="2026-01-01T00:00:00Z",
        task_context=task,
        goal_context=SpeakingGoalContext(speaking_goal="g", goal_label="G"),
        official_cefr_context=SpeakingOfficialCefrContext(official_cefr="A2"),
        evidence_summary=EvidenceSummaryFacts(
            availability={"transcript": True},
            reliability=0.7,
            provider_provenance=(),
            evidence_reference_ids=(),
        ),
        task_response=_dim("task_response"),
        topic_understanding=_dim("topic_understanding"),
        pronunciation=_dim("pronunciation"),
        fluency_delivery=_dim("fluency_delivery"),
        grammar=_dim("grammar"),
        vocabulary=_dim("vocabulary"),
        coherence=_dim("coherence"),
        interaction=_dim("interaction"),
        goal_alignment=_dim("goal_alignment"),
        cefr_validation=_dim("cefr_validation"),
        strengths=(),
        weaknesses=(),
        priority_issue="",
        revision_readiness=RevisionReadinessFacts(ready=True, blockers=()),
        completion_eligibility=CompletionEligibilityFacts(
            eligible=True, reason="ok", semantic_task_met=True
        ),
        comparison_with_previous_attempt="",
        educational_analysis=None,
        candidate_skill_evidence=(),
        explanation=ExplanationFacts(
            summary="s",
            priority_issue="",
            improvements=(),
            strengths=(),
            focus_label="",
        ),
        provider_provenance=(),
        weak_skills=(),
        strong_skills=(),
        overall_readiness=0.8,
    )


def test_identity_separation() -> None:
    print("\n--- identity separation ---")
    created = create_speaking_promotion_assessment(_authority())
    check("1. create ok", created.ok and created.assessment is not None and created.blueprint is not None)
    assert created.assessment is not None and created.blueprint is not None
    a = created.assessment
    check("2. assessment_id present", bool(a.assessment_id))
    check("3. blueprint_id present", bool(a.blueprint_id))
    check("4. assessment_id != blueprint_id", a.assessment_id != a.blueprint_id)
    check("5. attempt_id absent before start", a.current_attempt is None)
    check("6. blueprint identity matches", a.blueprint_id == created.blueprint.blueprint_id)

    started = start_speaking_promotion_assessment(a)
    check("7. start ok", started.ok and started.assessment is not None)
    assert started.assessment is not None and started.assessment.current_attempt is not None
    attempt_id = started.assessment.current_attempt.attempt_id
    check("8. attempt_id minted on start", bool(attempt_id) and attempt_id != a.assessment_id)
    check(
        "9. session owns all three ids",
        started.assessment.session is not None
        and started.assessment.session.assessment_id == a.assessment_id
        and started.assessment.session.blueprint_id == a.blueprint_id
        and started.assessment.session.attempt_id == attempt_id,
    )


def test_pass_and_fail_paths() -> None:
    print("\n--- pass / fail / bridge ---")
    created = create_speaking_promotion_assessment(_authority())
    assert created.assessment is not None
    started = start_speaking_promotion_assessment(created.assessment)
    assert started.assessment is not None
    a = started.assessment

    # PASS: all eligible + semantic met
    for task in sorted(a.blueprint.tasks, key=lambda t: t.task_order):
        scored = record_task_score(a, task_id=task.task_id, score=_score(task))
        check(f"10. submit {task.task_order}", scored.ok)
        assert scored.assessment is not None
        a = scored.assessment
    completed = complete_speaking_promotion_assessment(a)
    check("11. complete ok", completed.ok and completed.assessment is not None)
    assert completed.assessment is not None and completed.assessment.result is not None
    check("12. PASS outcome", completed.assessment.result.outcome == SpaAssessmentOutcome.PASS)
    check("13. ready_for_official_promotion", completed.assessment.result.ready_for_official_promotion is True)
    check("14. no bridge on PASS", completed.assessment.result.bridge_recommendation is None)

    # FAIL path with mandatory competency block: restart-like synthetic gate
    created2 = create_speaking_promotion_assessment(
        _authority(unlock_fingerprint="unlock_fail_" + "d" * 16)
    )
    assert created2.assessment is not None
    started2 = start_speaking_promotion_assessment(created2.assessment)
    assert started2.assessment is not None
    a2 = started2.assessment
    for task in sorted(a2.blueprint.tasks, key=lambda t: t.task_order):
        # Aggregate eligible, but production semantic fails on spontaneous tasks
        semantic = not task.spontaneous_production_required
        scored = record_task_score(
            a2,
            task_id=task.task_id,
            score=_score(task, eligible=True, semantic=semantic, readiness=0.9),
        )
        assert scored.assessment is not None
        a2 = scored.assessment
    scores = tuple(t.score for t in a2.current_attempt.task_attempts if t.score)  # type: ignore[union-attr]
    gate = decide_spa_pass_gate(
        scores=scores,
        tasks_total=len(a2.blueprint.tasks),
        requirements=a2.mandatory_requirements,
    )
    check("15. aggregate would pass", gate.would_pass_on_aggregate_alone is True)
    check("16. mandatory blocks PASS", gate.blocked_by_mandatory_competency is True)
    check("17. overall FAIL", gate.outcome == SpaAssessmentOutcome.FAIL)

    completed2 = complete_speaking_promotion_assessment(a2)
    assert completed2.assessment is not None and completed2.assessment.result is not None
    check("18. FAIL outcome persisted", completed2.assessment.result.outcome == SpaAssessmentOutcome.FAIL)
    check("19. bridge projection present", completed2.assessment.result.bridge_recommendation is not None)
    check("20. not ready for official CEFR", completed2.assessment.result.ready_for_official_promotion is False)


def test_abandon_timeout_resume_retry() -> None:
    print("\n--- abandon / timeout / resume / retry ---")
    created = create_speaking_promotion_assessment(_authority(unlock_fingerprint="unlock_ab_" + "e" * 16))
    assert created.assessment is not None
    started = start_speaking_promotion_assessment(created.assessment)
    assert started.assessment is not None
    a = started.assessment
    attempt1 = a.current_attempt.attempt_id if a.current_attempt else ""

    # Resume idempotent
    resumed = start_speaking_promotion_assessment(a)
    check("21. resume idempotent", resumed.ok and resumed.idempotent is True)
    assert resumed.assessment is not None and resumed.assessment.current_attempt is not None
    check("22. attempt_id unchanged on resume", resumed.assessment.current_attempt.attempt_id == attempt1)

    # Submit one task then reconnect cursor
    first = sorted(a.blueprint.tasks, key=lambda t: t.task_order)[0]
    scored = record_task_score(a, task_id=first.task_id, score=_score(first))
    assert scored.assessment is not None
    a = scored.assessment
    check("23. cursor advanced", a.session is not None and a.session.current_task_index == 1)
    check("24. current task is #2", current_task_id(a) == sorted(a.blueprint.tasks, key=lambda t: t.task_order)[1].task_id)

    # Idempotent re-submit
    again = record_task_score(a, task_id=first.task_id, score=_score(first, evaluation_id=f"eval_{first.task_id}"))
    check("25. idempotent resubmit", again.ok and again.idempotent is True)

    abandoned = abandon_speaking_promotion_assessment(a)
    check("26. abandon ok", abandoned.ok and abandoned.assessment is not None)
    assert abandoned.assessment is not None and abandoned.assessment.result is not None
    check("27. ABANDONED outcome", abandoned.assessment.result.outcome == SpaAssessmentOutcome.ABANDONED)

    retried = start_speaking_promotion_assessment(abandoned.assessment, force_new_attempt=True)
    check("28. retry after abandon ok", retried.ok and retried.assessment is not None)
    assert retried.assessment is not None and retried.assessment.current_attempt is not None
    check(
        "29. new attempt_id never reused",
        retried.assessment.current_attempt.attempt_id != attempt1,
    )
    check("30. blueprint freeze intact", retried.assessment.blueprint_id == created.assessment.blueprint_id)

    timed = timeout_speaking_promotion_assessment(retried.assessment)
    check("31. timeout ok", timed.ok and timed.assessment is not None)
    assert timed.assessment is not None and timed.assessment.result is not None
    check("32. TIMEOUT outcome", timed.assessment.result.outcome == SpaAssessmentOutcome.TIMEOUT)


def test_persistence_and_quarantine() -> None:
    print("\n--- persistence + quarantine ---")
    created = create_speaking_promotion_assessment(_authority(unlock_fingerprint="unlock_p_" + "f" * 17))
    assert created.assessment is not None
    payload = persist_active_assessment({}, created.assessment)
    bucket = assessments_bucket_from_payload(payload)
    try:
        assert_bucket_bounded(bucket)
        bounded = True
    except ValueError:
        bounded = False
    check("33. bucket bounded", bounded)
    check(
        "34. active_assessment key",
        set(bucket.keys()) == {"active_assessment", "most_recent_terminal_assessment"},
    )
    active = get_active_assessment(payload)
    check("35. load assessment distinct ids", active is not None and active.assessment_id != active.blueprint_id)

    check("36. mastery apply denied for SPA source", spa_evidence_may_apply_to_mastery(evidence_source="promotion_assessment") is False)
    check("37. mastery apply allowed for lesson source", spa_evidence_may_apply_to_mastery(evidence_source="evaluation_turn") is True)

    built = build_speaking_skill_observations(
        _fake_evaluation(),
        turn_reference="spa:x:t",
        session_id="s",
        source_type=ObservationSourceType.promotion_assessment,
    )
    check(
        "38. knowledge bridge quarantines SPA",
        built.mutation_status == SpeakingKnowledgeMutationStatus.quarantined_promotion_assessment,
    )
    check("39. no observations applied from SPA", len(built.observations) == 0)

    # merge strips forbidden archives
    dirty = dict(bucket)
    dirty["blueprints_by_id"] = {"x": {}}
    merged = merge_assessments_into_payload({}, dirty)
    check(
        "40. merge strips archives",
        "blueprints_by_id" not in merged["speaking_promotion_assessments"],
    )


def test_authority_boundaries() -> None:
    print("\n--- authority boundaries ---")
    pkg = BACKEND / "app/services/language_speaking_promotion_test"
    assign = False
    for p in pkg.rglob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Attribute) and t.attr == "official_speaking_cefr":
                        assign = True
    check("41. no official_speaking_cefr write in promotion_test", not assign)

    # promotion_test must not import evaluator (ownership)
    imports_eval = False
    for p in pkg.rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        if "language_speaking_evaluator" in text and "TYPE_CHECKING" not in text:
            # allow comments only
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("#"):
                    continue
                if "language_speaking_evaluator" in s:
                    imports_eval = True
    check("42. promotion_test does not import evaluator", not imports_eval)

    deps = ALLOWED_PACKAGE_DEPENDENCIES["language_speaking_promotion_test"]
    check("43. ownership unchanged for curriculum/generation", "language_speaking_curriculum" in deps and "language_speaking_generation" in deps)
    check("44. evaluator not an ownership dep of promotion_test", "language_speaking_evaluator" not in deps)

    api = BACKEND / "app/api/language_speaking_promotion_test.py"
    api_text = api.read_text(encoding="utf-8")
    check("45. start route", "/start" in api_text)
    check("46. submit route", "/submit" in api_text)
    check("47. complete route", "/complete" in api_text)
    check("48. result route", "/result" in api_text)
    check("49. abandon route", "/abandon" in api_text)

    # S7 lesson eval engine file untouched meaning: exists and still exports evaluate
    eng = (BACKEND / "app/services/language_speaking_evaluator/engine.py").read_text(encoding="utf-8")
    check("50. S7 evaluate_speaking_turn still present", "async def evaluate_speaking_turn" in eng)

    # No EVI execution mode introduced in SPA execution
    exec_text = (pkg / "execution.py").read_text(encoding="utf-8")
    check("51. SPA execution rejects non recorded/controlled", "invalid_execution_mode" in exec_text)


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
)


def run_s19_unit_suite() -> int:
    global PASS, FAIL
    print("=== Speaking S19 promotion assessment execution verifier ===\n", flush=True)
    test_identity_separation()
    test_pass_and_fail_paths()
    test_abandon_timeout_resume_retry()
    test_persistence_and_quarantine()
    test_authority_boundaries()
    print(f"\n=== S19 units: {PASS} passed, {FAIL} failed ===", flush=True)
    return FAIL


def main() -> int:
    if os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1":
        failed = run_s19_unit_suite()
        return 1 if failed else 0

    print("=== Speaking S19 FLAT regression runner ===\n", flush=True)
    for label, script in FLAT_REGRESSION_CHAIN:
        if not run_flat_verifier(label, script):
            print(f"\n=== STOPPED: flat regression failed at {label} ({script}) ===", flush=True)
            return 1

    print("\n=== FLAT S19 (this process) ===", flush=True)
    if run_s19_unit_suite() != 0:
        print("\n=== STOPPED: S19 unit suite failed ===", flush=True)
        return 1

    print("\n=== RESULT: all flat regressions + S19 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
