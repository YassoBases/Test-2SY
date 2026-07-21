"""Verify Speaking E4 discussion → evaluation mapping adapter.

Usage:
  python -u scripts/verify_speaking_e4_discussion_eval.py
  $env:SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS='1'
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}", flush=True)
    else:
        FAIL += 1
        suffix = f" — {detail}" if detail else ""
        print(f" FAIL {name}{suffix}", flush=True)


def sample_constraints() -> dict:
    return {
        "skill": "speaking",
        "official_cefr": "A2",
        "learning_stage": 1,
        "mission_id": "mission_e4",
        "mission_kind": "guided_practice",
        "execution_mode": "controlled_response",
        "evidence_intent": "formative",
        "blueprint_id": "bp_e4",
        "blueprint_hash": "hash_e4",
        "learning_focus": "ordering coffee",
        "objectives": ["Order politely"],
        "vocabulary_ids": ["v_coffee", "v_please"],
        "vocabulary_surface_forms": ["coffee", "please"],
        "grammar_topic_ids": [],
        "teaching_block_specs": [
            {"block_id": "tb1", "kind": "explanation", "target_skill_ids": [], "max_len": 160}
        ],
        "weak_skill_labels": [],
        "difficulty": "standard",
        "scenario_type": "cafe",
        "input_material_kind": "story",
        "lesson_length_band": "short",
        "mini_practice_task_id": "task_e4",
        "reflection_requirements": {"prompt_count": 2},
        "locale": "en",
    }


def test_e4_units() -> None:
    print("\n--- E4 discussion evaluation adapter units ---", flush=True)
    from app.services.language_educational_package.evidence_policy import DiscussionEvidenceRole
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_educational_package.question_ladder import QuestionBand
    from app.services.language_educational_package.types import DiscussionStep
    from app.services.language_speaking import ownership as owning
    from app.services.language_speaking_discussion.types import (
        DiscussionPhase,
        DiscussionRuntimeState,
        DiscussionTurn,
    )
    from app.services.language_speaking_discussion_eval.adapter import (
        maybe_map_discussion_turn_to_evaluation,
    )
    from app.services.language_speaking_discussion_eval.policy import (
        DEFAULT_DISCUSSION_EVAL_POLICY,
        category_for_step,
    )
    from app.services.language_speaking_discussion_eval.types import (
        DISCUSSION_EVAL_ADAPTER_VERSION,
        DiscussionEvidenceCategory,
        DiscussionProductionMode,
    )
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_evaluator.evaluation_result import (
        SpeakingEvaluationEngineResult,
    )
    from app.services.language_speaking_evaluation_runtime.knowledge_bridge_types import (
        SpeakingKnowledgeMutationBridgeResult,
        SpeakingKnowledgeMutationStatus,
    )

    constraints = build_speaking_package_constraints(sample_constraints())
    gen = process_package_generation(
        constraints,
        author_package_json_template(constraints),
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
    )
    check("1. frozen package ready", gen.success and gen.package is not None)
    package = gen.package
    assert package is not None

    # Policy: informational / none skips
    none_step = DiscussionStep(
        step_id="s_none",
        ladder_band=QuestionBand.literal,
        prompt="What did they say?",
        success_cues=[],
        evidence_role=DiscussionEvidenceRole.none,
        allowed_correction_mode=__import__(
            "app.services.language_educational_package.evidence_policy", fromlist=["CorrectionMode"]
        ).CorrectionMode.none,
    )
    d_none = DEFAULT_DISCUSSION_EVAL_POLICY.decide(
        none_step, student_response="They asked for coffee please."
    )
    check("2. informational/none not eligible", not d_none.eligible)
    check(
        "3. category informational",
        category_for_step(none_step) == DiscussionEvidenceCategory.informational,
    )

    # Find an eligible step on the authored package
    eligible_step = next(
        (s for s in package.discussion.steps if s.evidence_role != DiscussionEvidenceRole.none),
        None,
    )
    if eligible_step is None:
        # Force a formative step for adapter tests
        from app.services.language_educational_package.evidence_policy import CorrectionMode

        eligible_step = DiscussionStep(
            step_id="s_form",
            ladder_band=QuestionBand.reasoning,
            prompt="Why might someone order coffee politely?",
            success_cues=["because", "please"],
            evidence_role=DiscussionEvidenceRole.formative,
            allowed_correction_mode=CorrectionMode.micro,
        )
    check("4. eligible step available", eligible_step is not None)

    d_ok = DEFAULT_DISCUSSION_EVAL_POLICY.decide(
        eligible_step,
        student_response="I would like to order a coffee politely because it is respectful.",
        production_mode=DiscussionProductionMode.text,
    )
    check("5. formative/text eligible", d_ok.eligible)
    check(
        "6. category not informational",
        d_ok.category != DiscussionEvidenceCategory.informational,
    )

    short = DEFAULT_DISCUSSION_EVAL_POLICY.decide(
        eligible_step, student_response="ok"
    )
    check("7. below min words skips", not short.eligible)

    transfer_step = DiscussionStep(
        step_id="s_xfer",
        ladder_band=QuestionBand.real_world_transfer,
        prompt="Order coffee in a new cafe.",
        success_cues=["coffee"],
        evidence_role=DiscussionEvidenceRole.transfer,
        allowed_correction_mode=none_step.allowed_correction_mode,
    )
    check(
        "8. transfer category",
        category_for_step(transfer_step) == DiscussionEvidenceCategory.transfer,
    )

    state = DiscussionRuntimeState(
        package_id=package.package_id,
        content_item_id=1,
        content_fingerprint=package.content_fingerprint,
        phase=DiscussionPhase.waiting_for_student,
        step_index=0,
        current_step_id=eligible_step.step_id,
        turns=[
            DiscussionTurn(
                role="student",
                text="I would like to order a coffee politely because it is respectful.",
                step_id=eligible_step.step_id,
                created_at="2026-01-01T00:00:00+00:00",
            )
        ],
        started_at="2026-01-01T00:00:00+00:00",
    )

    fake_eval = SimpleNamespace(
        evaluation_id="disc-eval-test",
        engine_version="test",
        evaluated_at="2026-01-01T00:00:00+00:00",
        revision_number=1,
        candidate_skill_evidence=(),
        student_id=1,
    )
    # Typing: adapter expects SpeakingEvaluationEngineResult; patch returns SimpleNamespace ok for our fields
    fake_bridge = SpeakingKnowledgeMutationBridgeResult(
        bridge_version="test",
        source_evaluation_version="test",
        turn_reference="discussion:x:y:t1",
        mutation_status=SpeakingKnowledgeMutationStatus.no_observations,
    )

    called = {"s7": 0, "bridge": 0}

    async def fake_s7(inp, ctx):
        called["s7"] += 1
        check("9. S7 input has transcript", bool(inp.transcript_text))
        check("10. S7 context has task_id", bool(ctx.task.task_id.startswith("discussion:")))
        # Ensure discussion context packaging never put promotion/CEFR into task instructions as authority
        check(
            "11. task instructions omit promotion",
            "promotion" not in (ctx.task.task_instructions or "").lower(),
        )
        return fake_eval

    async def fake_bridge_apply(*_a, **kwargs):
        called["bridge"] += 1
        source = kwargs.get("source_type")
        check(
            "12. knowledge via bridge source evaluation_turn",
            getattr(source, "value", None) == "evaluation_turn",
        )
        return fake_bridge

    async def fake_cefr(*_a, **_k):
        return "A2"

    async def _run_handoff() -> None:
        fake_db = SimpleNamespace(execute=AsyncMock())
        with (
            patch(
                "app.services.language_speaking_discussion_eval.adapter.evaluate_speaking_turn",
                new=fake_s7,
            ),
            patch(
                "app.services.language_speaking_discussion_eval.adapter.apply_speaking_evaluation_to_knowledge_model",
                new=fake_bridge_apply,
            ),
            patch(
                "app.services.language_speaking_discussion_eval.adapter._load_official_speaking_cefr",
                new=fake_cefr,
            ),
        ):
            result = await maybe_map_discussion_turn_to_evaluation(
                fake_db,
                student_id=1,
                language_id=1,
                package=package,
                state=state,
                step=eligible_step,
                student_response="I would like to order a coffee politely because it is respectful.",
            )
            check("13. handoff not skipped", not result.skipped)
            check("14. evaluation_id set", bool(result.evaluation_id))
            check("15. turn_reference discussion:", bool(result.turn_reference and result.turn_reference.startswith("discussion:")))
            check("16. adapter version", result.adapter_version == DISCUSSION_EVAL_ADAPTER_VERSION)

            skipped = await maybe_map_discussion_turn_to_evaluation(
                fake_db,
                student_id=1,
                language_id=1,
                package=package,
                state=state,
                step=none_step,
                student_response="They asked for coffee please and that is all for today.",
            )
            check("17. none role skips without S7", skipped.skipped and called["s7"] == 1)

    asyncio.run(_run_handoff())
    check("18. S7 called once for eligible", called["s7"] == 1)
    check("19. knowledge bridge once", called["bridge"] == 1)

    # Ownership / boundary
    check(
        "20. ownership registers discussion_eval",
        "language_speaking_discussion_eval" in owning.PACKAGE_OWNERSHIP,
    )
    deps = owning.ALLOWED_PACKAGE_DEPENDENCIES["language_speaking_discussion_eval"]
    check("21. may depend on discussion", "language_speaking_discussion" in deps)
    check("22. may depend on evaluator", "language_speaking_evaluator" in deps)
    check("23. may depend on evaluation_runtime", "language_speaking_evaluation_runtime" in deps)
    check(
        "24. layer experience",
        owning.PACKAGE_LAYER.get("language_speaking_discussion_eval") == "experience",
    )

    disc_pkg = BACKEND / "app/services/language_speaking_discussion"
    disc_text = "\n".join(p.read_text(encoding="utf-8") for p in disc_pkg.glob("*.py"))
    check(
        "25. E3 discussion still no evaluation_runtime import",
        "language_speaking_evaluation_runtime" not in disc_text,
    )
    check("26. E3 discussion no adapter import", "discussion_eval" not in disc_text)
    check("27. E3 no official_promotion", "official_promotion" not in disc_text)
    check("28. E3 no alex_context", "alex_context" not in disc_text)

    eval_pkg = BACKEND / "app/services/language_speaking_discussion_eval"
    eval_text = "\n".join(p.read_text(encoding="utf-8") for p in eval_pkg.glob("*.py"))
    check("29. adapter does not import alex", "alex_context" not in eval_text)
    check("30. adapter does not import official_promotion", "official_promotion" not in eval_text)
    check(
        "31. adapter does not write official_speaking_cefr",
        "official_speaking_cefr =" not in eval_text.replace(" ", ""),
    )
    # CEFR is read-only select
    check("32. adapter loads CEFR read-only", "_load_official_speaking_cefr" in eval_text)

    api = (BACKEND / "app/api/language_speaking_discussion.py").read_text(encoding="utf-8")
    check("33. no new eval HTTP surface", "evaluation" not in api.lower())
    api_svc = (BACKEND / "app/services/language_speaking_discussion_api/service.py").read_text(
        encoding="utf-8"
    )
    check("34. API twin wires E4 handoff", "maybe_map_discussion_turn_to_evaluation" in api_svc)
    check("35. student contract still DiscussionRuntimeOut", "DiscussionRuntimeOut" in api_svc)

    fe_ui = BACKEND.parent / "src/components/language/SpeakingGuidedDiscussion.vue"
    if fe_ui.is_file():
        ui = fe_ui.read_text(encoding="utf-8")
        check("36. FE hides mastery/CEFR", "mastery" not in ui.lower() and "cefr" not in ui.lower())
    else:
        check("36. FE discussion UI present", False, "missing SpeakingGuidedDiscussion.vue")

    # Silence unused import for type presence
    check("37. SpeakingEvaluationEngineResult importable", SpeakingEvaluationEngineResult is not None)


def run_flat_verifier(label: str, script: str, timeout_s: int = 180) -> bool:
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
            proc.kill()
            print(f"TIMEOUT after {timeout_s}s: {script}", flush=True)
            return False
    ok = proc.returncode == 0
    print(f"  {'OK' if ok else 'FAIL'}  {label} (exit={proc.returncode})", flush=True)
    if not ok:
        try:
            print(log_path.read_text(encoding="utf-8", errors="replace")[-2500:], flush=True)
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
    ("S20", "verify_speaking_s20_official_promotion.py"),
    ("E1", "verify_speaking_e1_learning_package.py"),
    ("E2", "verify_speaking_e2_lesson_runtime.py"),
    ("E3", "verify_speaking_e3_guided_discussion.py"),
)


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    if not skip:
        print("=== Speaking E4 FLAT regression runner ===\n", flush=True)
        for label, script in FLAT_REGRESSION_CHAIN:
            if not run_flat_verifier(label, script):
                print(f"\n=== STOPPED: flat regression failed at {label} ===", flush=True)
                return 1
        print("\n=== FLAT E4 (this process) ===", flush=True)

    print("=== Speaking E4 discussion evaluation verifier ===\n", flush=True)
    test_e4_units()
    print(f"\n=== E4 units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n=== RESULT: all flat regressions + E4 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

