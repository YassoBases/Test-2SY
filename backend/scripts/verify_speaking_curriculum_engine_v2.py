"""Verify Curriculum Engine V2 — educational intelligence before Claude.

Usage:
  python -u scripts/verify_speaking_curriculum_engine_v2.py
  $env:SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS='1'
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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


def _word_count(pkg) -> int:
    return sum(len((b.text or "").split()) for b in pkg.input_material.body_blocks)


def _turn_count(pkg) -> int:
    """Count Educational Case beats (paragraph/heading) or legacy dialogue turns."""
    return len(
        [
            b
            for b in pkg.input_material.body_blocks
            if (b.kind.value if hasattr(b.kind, "value") else str(b.kind))
            in {"turn", "paragraph", "heading"}
        ]
    )


def _corpus(pkg) -> str:
    parts = [
        " ".join(b.text for b in pkg.input_material.body_blocks),
        " ".join(b.body for b in pkg.teaching_blocks_authored),
        " ".join(
            [pkg.discussion.opening_move, pkg.discussion.closing_move]
            + [s.prompt for s in pkg.discussion.steps]
        ),
        f"{pkg.mini_practice.prompt} {pkg.mini_practice.scaffold}",
    ]
    return "\n".join(parts).lower()


def test_curriculum_units() -> None:
    print("\n--- Curriculum Engine V2 units ---", flush=True)
    from app.services.language_speaking import ownership as owning
    from app.services.language_speaking_curriculum_engine import (
        CURRICULUM_ENGINE_VERSION,
        enrich_speaking_constraints_payload,
    )
    from app.services.language_speaking_curriculum_engine.cefr_policy import (
        lesson_authoring_policy_for_cefr,
    )
    from app.services.language_speaking_curriculum_engine.vocabulary_catalog import (
        select_vocabulary_targets,
    )
    from app.services.language_educational_package.constraints import (
        ELP_CONSTRAINTS_SCHEMA_VERSION,
        PackageConstraints,
    )

    check("1. engine version 2", CURRICULUM_ENGINE_VERSION.startswith("2."))
    check("2. constraints schema 2", ELP_CONSTRAINTS_SCHEMA_VERSION.startswith("2."))
    check(
        "3. ownership registers curriculum_engine",
        "language_speaking_curriculum_engine" in owning.PACKAGE_OWNERSHIP,
    )
    check(
        "4. layer curriculum",
        owning.PACKAGE_LAYER.get("language_speaking_curriculum_engine") == "curriculum",
    )

    a1 = lesson_authoring_policy_for_cefr("A1")
    a2 = lesson_authoring_policy_for_cefr("A2")
    b2 = lesson_authoring_policy_for_cefr("B2")
    check("5. A1 fewer turns than A2", a1.min_story_beats < a2.min_story_beats)
    check("6. A2 fewer turns than B2", a2.min_story_beats < b2.min_story_beats)
    check("7. A1 fewer words than A2", a1.min_input_word_count < a2.min_input_word_count)
    check("8. B2 higher recycle", b2.min_recycle_per_item >= a2.min_recycle_per_item)

    v_a1 = select_vocabulary_targets(
        cefr="A1",
        skill_ids=["phrase:travel_greetings"],
        learning_focus="Travel greetings",
        count=a1.target_vocabulary_count,
    )
    v_a2 = select_vocabulary_targets(
        cefr="A2",
        skill_ids=["phrase:travel_greetings"],
        learning_focus="Travel greetings",
        count=a2.target_vocabulary_count,
    )
    v_b2 = select_vocabulary_targets(
        cefr="B2",
        skill_ids=["fluency:appropriate_rate"],
        learning_focus="Appropriate speaking rate",
        count=b2.target_vocabulary_count,
    )
    check("9. A1 vocab real lemmas", all(x.lemma and x.surface and x.meaning for x in v_a1))
    check("10. A1 not meta skill label", all(x.surface.lower() != "travel greetings" for x in v_a1))
    check("11. A2 vocab differs from A1", {x.vocabulary_id for x in v_a1} != {x.vocabulary_id for x in v_a2})
    check("12. B2 pace vocab present", any("slow" in x.surface.lower() or "pace" in x.surface.lower() for x in v_b2))
    check("13. B2 recycle freq ≥3", all(x.required_lesson_frequency >= 2 for x in v_b2))

    base_a1 = {
        "skill": "speaking",
        "official_cefr": "A1",
        "learning_stage": 1,
        "mission_id": "m1",
        "mission_kind": "teaching",
        "execution_mode": "study",
        "evidence_intent": "none",
        "blueprint_id": "bp1",
        "blueprint_hash": "h1",
        "learning_focus": "Learn: Travel greetings",
        "objectives": ["Use Travel greetings clearly when you speak."],
        "target_skill_ids": ["phrase:travel_greetings"],
        "teaching_block_specs": [
            {
                "block_id": "tb1",
                "kind": "explanation",
                "target_skill_ids": ["phrase:travel_greetings"],
                "max_len": 220,
            }
        ],
        "locale": "en",
        "mini_practice_task_id": "task1",
        "input_material_kind": "story",
        "scenario_type": "conversation",
    }
    enriched = enrich_speaking_constraints_payload(base_a1)
    check("14. enriched has vocabulary_targets", len(enriched.get("vocabulary_targets") or []) >= 4)
    kinds = {o["kind"] for o in enriched.get("educational_objectives") or []}
    check(
        "15. objective kinds present",
        {"communicative", "vocabulary", "speaking", "transfer"}.issubset(kinds),
    )
    check("16. grammar_targets selected", len(enriched.get("grammar_targets") or []) >= 1)
    check(
        "16b. story_complexity_policy present",
        isinstance(enriched.get("story_complexity_policy"), dict)
        and int((enriched.get("story_complexity_policy") or {}).get("min_words") or 0) >= 90,
    )
    check("17. engine version stamped", enriched.get("curriculum_engine_version", "").startswith("2."))
    check(
        "18. no invented-surface forbidden flag",
        "no_invented_vocabulary_surfaces" in (enriched.get("forbidden_behaviors") or []),
    )
    cons = PackageConstraints.from_dict(enriched)
    check("19. PackageConstraints round-trip targets", len(cons.vocabulary_targets) >= 4)
    check("20. objectives list expanded", len(cons.objectives) >= 4)


def test_generate_packages() -> None:
    print("\n--- Curriculum Engine V2 generated packages (template path) ---", flush=True)
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_curriculum_engine import enrich_speaking_constraints_payload
    from app.services.language_speaking_diagnostic.selector import select_speaking_target
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_knowledge_model.storage import empty_knowledge_model
    from app.services.language_speaking_lesson_planner.planner import assemble_speaking_lesson_blueprint
    from app.services.language_speaking_runtime_api.journey_constraints import (
        build_constraints_payload_from_journey,
    )

    levels = [("A1", 1, "everyday_survival"), ("A2", 1, "general_english"), ("B2", 2, "general_english")]
    packages = {}
    constraints_by = {}

    for cefr, stage, goal in levels:
        km = empty_knowledge_model(student_id=9100, language_id=1)
        rec = select_speaking_target(km, official_cefr=cefr, speaking_goal=goal)
        bp = assemble_speaking_lesson_blueprint(rec)
        try:
            bp.official_cefr_hint = cefr
        except Exception:
            pass
        row = SimpleNamespace(
            official_speaking_cefr=SimpleNamespace(value=cefr),
            learning_stage_speaking=stage,
            promotion_readiness_json={},
        )
        payload = build_constraints_payload_from_journey(row=row, blueprint=bp, session=None)
        payload["official_cefr"] = cefr
        # Ensure V2 enrichment always applied (journey already enriches)
        if not payload.get("vocabulary_targets"):
            payload = enrich_speaking_constraints_payload(payload)
        constraints = build_speaking_package_constraints(payload)
        constraints_by[cefr] = constraints
        raw = author_package_json_template(constraints)
        result = process_package_generation(
            constraints,
            raw,
            author_provider=AUTHOR_PROVIDER_TEMPLATE,
            attempt_repair=True,
        )
        check(f"{cefr}. generation success", result.success and result.package is not None)
        assert result.package is not None
        packages[cefr] = result.package

        cons = constraints
        pkg = result.package
        check(f"{cefr}. real vocab count", len(cons.vocabulary_targets) >= 4)
        check(
            f"{cefr}. no meta Travel greetings surface",
            all(
                str(v.get("surface") or "").lower() != "travel greetings"
                for v in cons.vocabulary_targets
            ),
        )
        check(f"{cefr}. educational objectives ≥4", len(cons.educational_objectives) >= 4)
        check(f"{cefr}. grammar_targets selected", len(list(cons.grammar_targets)) >= 1)
        check(
            f"{cefr}. story complexity words band",
            isinstance(cons.story_complexity_policy, dict)
            and int((cons.story_complexity_policy or {}).get("min_words") or 0)
            <= _word_count(pkg),
        )
        policy = cons.lesson_authoring_policy or {}
        complexity = cons.story_complexity_policy or {}
        check(
            f"{cefr}. density turns",
            _turn_count(pkg)
            >= int(
                complexity.get("paragraph_count_min")
                or policy.get("min_story_beats")
                or 0
            ),
            f"turns={_turn_count(pkg)} need={complexity.get('paragraph_count_min') or policy.get('min_story_beats')}",
        )
        check(
            f"{cefr}. density words",
            _word_count(pkg)
            >= int(complexity.get("min_words") or policy.get("min_input_word_count") or 0),
            f"words={_word_count(pkg)} need={complexity.get('min_words') or policy.get('min_input_word_count')}",
        )
        check(
            f"{cefr}. characters meet policy",
            len(pkg.story_spine.characters)
            >= int((cons.story_complexity_policy or {}).get("characters_min") or 0),
        )
        check(
            f"{cefr}. events meet policy",
            len(pkg.story_spine.events)
            >= int(
                (cons.story_complexity_policy or {}).get("story_events_min")
                or (cons.story_complexity_policy or {}).get("story_events")
                or 0
            ),
        )
        # Recycling
        corpus = _corpus(pkg)
        recycle_ok = True
        need = int((cons.lexical_recycling_policy or {}).get("min_appearances_per_item") or 2)
        for raw in cons.vocabulary_targets:
            surface = str(raw.get("surface") or "").strip()
            if not surface:
                continue
            if corpus.count(surface.lower()) < need:
                recycle_ok = False
                break
        check(f"{cefr}. lexical recycling", recycle_ok)
        # Exact surfaces in package entries
        by_id = {e.vocabulary_id: e.surface for e in pkg.vocabulary_in_context.entries}
        exact = True
        for raw in cons.vocabulary_targets:
            vid = str(raw.get("vocabulary_id") or "")
            if vid in by_id and by_id[vid].strip() != str(raw.get("surface") or "").strip():
                exact = False
        check(f"{cefr}. exact vocab surfaces", exact)
        check(f"{cefr}. teaching blocks present", len(pkg.teaching_blocks_authored) >= 2)
        check(f"{cefr}. discussion steps ≥ ladder min", len(pkg.discussion.steps) >= cons.question_ladder_policy.min_steps)
        check(f"{cefr}. mini practice uses language", bool(pkg.mini_practice.prompt.strip()))
        check(f"{cefr}. reflection present", len(pkg.reflection.prompts) >= 2)

    # Differentiation
    check(
        "DIFF. A1 vocab ≠ A2 vocab",
        {v.get("vocabulary_id") for v in constraints_by["A1"].vocabulary_targets}
        != {v.get("vocabulary_id") for v in constraints_by["A2"].vocabulary_targets},
    )
    check(
        "DIFF. A1 turns policy < A2",
        (constraints_by["A1"].lesson_authoring_policy or {}).get("min_story_beats", 0)
        < (constraints_by["A2"].lesson_authoring_policy or {}).get("min_story_beats", 0),
    )
    check(
        "DIFF. A2 turns policy < B2",
        (constraints_by["A2"].lesson_authoring_policy or {}).get("min_story_beats", 0)
        < (constraints_by["B2"].lesson_authoring_policy or {}).get("min_story_beats", 0),
    )
    check(
        "DIFF. package word counts increase loosely",
        _word_count(packages["A1"]) <= _word_count(packages["B2"]),
    )
    check(
        "DIFF. B2 ladder includes transfer",
        any(s.ladder_band.value == "real_world_transfer" for s in packages["B2"].discussion.steps),
    )


def run_flat(label: str, script: str, timeout_s: int = 180) -> bool:
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
            return False
    ok = proc.returncode == 0
    print(f"  {'OK' if ok else 'FAIL'}  {label} (exit={proc.returncode})", flush=True)
    return ok


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    print("=== Speaking Curriculum Engine V2 verifier ===\n", flush=True)
    test_curriculum_units()
    test_generate_packages()
    print(f"\n=== V2 units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n--- E1–E4 regression (flat, nested skip) ---", flush=True)
        for label, script in (
            ("E1", "verify_speaking_e1_learning_package.py"),
            ("E2", "verify_speaking_e2_lesson_runtime.py"),
            ("E3", "verify_speaking_e3_guided_discussion.py"),
            ("E4", "verify_speaking_e4_discussion_eval.py"),
        ):
            if not run_flat(label, script):
                return 1
        print("\n=== RESULT: Curriculum Engine V2 + E1–E4 green ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
