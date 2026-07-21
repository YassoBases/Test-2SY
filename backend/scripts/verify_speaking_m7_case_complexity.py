"""M7 — CEFR-adaptive Educational Case sophistication verifier.

Generates Educational Cases for A1 / A2 / B1 / B2 / C1 and proves complexity
rises beyond word count alone (decision, ethics, stakeholders, discussion,
reflection). Also proves Alex binds to the SAME Educational Case.

Usage:
  python -u scripts/verify_speaking_m7_case_complexity.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

PASS = 0
FAIL = 0

LEVELS = ("A1", "A2", "B1", "B2", "C1")

DECISION_RANK = {
    "one_obvious_solution": 1,
    "simple_choice_two_options": 2,
    "several_solutions_tradeoffs": 3,
    "competing_valid_options": 4,
    "no_single_correct_answer": 5,
}

ETHICAL_RANK = {
    "none": 0,
    "light_fairness": 1,
    "personal_responsibility": 2,
    "ethical_dilemma": 3,
    "advanced_public_ethics": 4,
}

READING_RANK = {
    "very_easy": 1,
    "easy": 2,
    "intermediate": 3,
    "upper_intermediate": 4,
    "advanced": 5,
}

GRAMMAR_RANK = {
    "present_simple_short": 1,
    "present_and_past_with_connectors": 2,
    "past_present_future_cause_effect": 3,
    "mixed_grammar_complex_connectors": 4,
    "advanced_embedded_clauses": 5,
}

DISCUSSION_RANK = {
    "literal_understanding_simple_opinion": 1,
    "literal_vocab_simple_reasoning": 2,
    "reasoning_comparison_alternatives": 3,
    "ethical_judgment_tradeoffs_evidence": 4,
    "critical_policy_counterarguments": 5,
}


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


def _discussion_blob(pkg) -> str:
    return " ".join(
        [pkg.discussion.opening_move, pkg.discussion.closing_move]
        + [s.prompt for s in pkg.discussion.steps]
    ).lower()


def _generate_for_cefr(cefr: str):
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
    from app.services.language_speaking_lesson_planner.planner import (
        assemble_speaking_lesson_blueprint,
        continue_alex_from_story_spine,
    )
    from app.services.language_speaking_runtime_api.journey_constraints import (
        build_constraints_payload_from_journey,
    )

    km = empty_knowledge_model(student_id=9700, language_id=1)
    rec = select_speaking_target(km, official_cefr=cefr, speaking_goal="general_english")
    bp = assemble_speaking_lesson_blueprint(rec)
    try:
        bp.official_cefr_hint = cefr
    except Exception:
        pass
    # Rebuild alex with the verifier CEFR so taxonomy matches the package
    from app.services.language_speaking_diagnostic.types import TargetSelectionReason
    from app.services.language_speaking_lesson_planner.planner import _alex_context
    import dataclasses

    node_label = bp.alex_context.target_skill_label
    reason = TargetSelectionReason(bp.selection_reason)
    alex = _alex_context(
        node_label,
        reason,
        bp.speaking_goal,
        skill_ids=list(bp.target_skill_ids) + [bp.primary_target_skill_id],
        official_cefr=cefr,
    )
    bp = dataclasses.replace(bp, official_cefr_hint=cefr, alex_context=alex)

    stage = {"A1": 1, "A2": 1, "B1": 2, "B2": 2, "C1": 3}.get(cefr, 1)
    row = SimpleNamespace(
        official_speaking_cefr=SimpleNamespace(value=cefr),
        learning_stage_speaking=stage,
        promotion_readiness_json={},
    )
    payload = build_constraints_payload_from_journey(row=row, blueprint=bp, session=None)
    payload["official_cefr"] = cefr
    if not payload.get("vocabulary_targets"):
        payload = enrich_speaking_constraints_payload(payload)
    constraints = build_speaking_package_constraints(payload)
    raw = author_package_json_template(constraints)
    result = process_package_generation(
        constraints,
        raw,
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    assert result.success and result.package is not None, f"{cefr} package failed"
    pkg = result.package
    alex_bound = continue_alex_from_story_spine(
        bp.alex_context,
        title=pkg.story_spine.title,
        setting=pkg.story_spine.setting,
        characters=[c.name for c in pkg.story_spine.characters],
        conflict=pkg.story_spine.conflict,
        continuation_hook=pkg.story_spine.continuation_hook,
        case_category=pkg.story_spine.case_category,
        case_archetype=pkg.story_spine.case_archetype,
        stakeholders=list(pkg.story_spine.stakeholders),
        decision_point=pkg.story_spine.decision_point,
    )
    return {
        "cefr": cefr,
        "constraints": constraints,
        "package": pkg,
        "alex": alex_bound,
        "blueprint": bp,
    }


def main() -> int:
    print("\n=== M7 Educational Case sophistication (A1→C1) ===\n", flush=True)
    from app.services.language_speaking_curriculum_engine import (
        CURRICULUM_ENGINE_VERSION,
        EducationalCaseCategory,
        story_complexity_policy_for_cefr,
    )
    from app.services.language_speaking_curriculum_engine.case_taxonomy import (
        _CEFR_CATEGORY_POOL,
        case_archetype_for_cefr,
    )

    check("engine version ≥ 2.3", CURRICULUM_ENGINE_VERSION.startswith("2."))
    check(
        "taxonomy has curriculum categories",
        EducationalCaseCategory.daily_life in EducationalCaseCategory
        and EducationalCaseCategory.law in EducationalCaseCategory,
    )
    check("A1 pool is everyday-facing", "daily_life" in {c.value for c in _CEFR_CATEGORY_POOL["A1"]})
    check("C1 pool includes law/leadership", "law" in {c.value for c in _CEFR_CATEGORY_POOL["C1"]})

    samples = {}
    for cefr in LEVELS:
        print(f"\n--- Generating {cefr} ---", flush=True)
        samples[cefr] = _generate_for_cefr(cefr)
        pkg = samples[cefr]["package"]
        cons = samples[cefr]["constraints"]
        complexity = cons.story_complexity_policy or {}
        policy = story_complexity_policy_for_cefr(cefr)

        check(f"{cefr}. generation ok", True)
        check(
            f"{cefr}. case_category curriculum-owned",
            bool(complexity.get("case_category"))
            and pkg.story_spine.case_category == complexity.get("case_category"),
            f"spine={pkg.story_spine.case_category} policy={complexity.get('case_category')}",
        )
        check(
            f"{cefr}. case_archetype matches CEFR",
            pkg.story_spine.case_archetype == case_archetype_for_cefr(cefr),
            pkg.story_spine.case_archetype,
        )
        check(
            f"{cefr}. stakeholders ≥ policy",
            len(pkg.story_spine.stakeholders) >= int(complexity.get("stakeholder_count") or 0),
            f"have={len(pkg.story_spine.stakeholders)} need={complexity.get('stakeholder_count')}",
        )
        check(f"{cefr}. decision_point present", bool(pkg.story_spine.decision_point.strip()))
        check(
            f"{cefr}. ending_type present",
            bool(pkg.story_spine.ending_type.strip()),
        )
        check(
            f"{cefr}. word count meets min",
            _word_count(pkg) >= int(complexity.get("min_words") or 0),
            f"words={_word_count(pkg)} min={complexity.get('min_words')}",
        )
        check(
            f"{cefr}. grammar topics ≥ policy",
            len(list(cons.grammar_targets)) >= policy.required_grammar_topic_count,
        )
        check(
            f"{cefr}. reflection depth",
            len(pkg.reflection.prompts) >= int(complexity.get("reflection_depth") or 0),
            f"prompts={len(pkg.reflection.prompts)} need={complexity.get('reflection_depth')}",
        )
        check(
            f"{cefr}. discussion has steps",
            len(pkg.discussion.steps) >= cons.question_ladder_policy.min_steps,
        )
        alex = samples[cefr]["alex"]
        check(
            f"{cefr}. Alex same case_category",
            alex.case_category == pkg.story_spine.case_category,
        )
        check(
            f"{cefr}. Alex same case_archetype",
            alex.case_archetype == pkg.story_spine.case_archetype,
        )
        check(
            f"{cefr}. Alex has stakeholders",
            len(alex.case_stakeholders) >= 1
            and set(alex.case_stakeholders) == set(pkg.story_spine.stakeholders),
        )
        check(
            f"{cefr}. Alex same decision_point",
            alex.case_decision_point == pkg.story_spine.decision_point,
        )
        check(
            f"{cefr}. Alex same continuation_hook",
            alex.case_continuation_hook == pkg.story_spine.continuation_hook,
        )

    # Comparative progression A1 → C1
    print("\n--- Comparative progression ---", flush=True)
    words = [_word_count(samples[c]["package"]) for c in LEVELS]
    check("1. reading complexity increases (words)", words[0] < words[2] < words[4], str(words))

    reading = [
        READING_RANK.get(
            (samples[c]["constraints"].story_complexity_policy or {}).get("reading_complexity"),
            0,
        )
        for c in LEVELS
    ]
    check("1b. reading_complexity policy increases", reading == sorted(reading) and reading[0] < reading[-1], str(reading))

    vocab_n = [len(samples[c]["constraints"].vocabulary_targets) for c in LEVELS]
    check(
        "2. vocabulary complexity increases (count)",
        vocab_n[0] <= vocab_n[2] and vocab_n[2] <= vocab_n[4],
        str(vocab_n),
    )

    grammar = [
        GRAMMAR_RANK.get(
            (samples[c]["constraints"].story_complexity_policy or {}).get("sentence_complexity"),
            0,
        )
        for c in LEVELS
    ]
    check("3. grammar complexity increases", grammar == sorted(grammar) and grammar[0] < grammar[-1], str(grammar))

    decision = [
        DECISION_RANK.get(
            (samples[c]["constraints"].story_complexity_policy or {}).get("decision_complexity"),
            0,
        )
        for c in LEVELS
    ]
    check(
        "4. decision complexity increases",
        decision == sorted(decision) and decision[0] < decision[-1],
        str(decision),
    )

    ethical = [
        ETHICAL_RANK.get(
            (samples[c]["constraints"].story_complexity_policy or {}).get("ethical_complexity"),
            0,
        )
        for c in LEVELS
    ]
    check(
        "5. ethical complexity increases",
        ethical == sorted(ethical) and ethical[0] < ethical[-1],
        str(ethical),
    )

    stakes = [
        len(samples[c]["package"].story_spine.stakeholders) for c in LEVELS
    ]
    check(
        "6. stakeholder count increases",
        stakes[0] <= stakes[2] <= stakes[4] and stakes[0] < stakes[4],
        str(stakes),
    )

    discussion = [
        DISCUSSION_RANK.get(
            (samples[c]["constraints"].story_complexity_policy or {}).get("discussion_depth"),
            0,
        )
        for c in LEVELS
    ]
    check(
        "7. discussion depth increases",
        discussion == sorted(discussion) and discussion[0] < discussion[-1],
        str(discussion),
    )
    # Harder bands should ask for trade-offs / critique in prompts
    b2_blob = _discussion_blob(samples["B2"]["package"])
    c1_blob = _discussion_blob(samples["C1"]["package"])
    check(
        "7b. B2 discussion asks ethical/trade-off",
        any(k in b2_blob for k in ("ethic", "trade", "perspective", "evidence")),
    )
    check(
        "7c. C1 discussion asks critical/counter",
        any(k in c1_blob for k in ("counter", "societ", "policy", "defend", "long-term")),
    )

    reflection = [len(samples[c]["package"].reflection.prompts) for c in LEVELS]
    check(
        "8. reflection depth increases",
        reflection[0] <= reflection[2] <= reflection[4] and reflection[0] < reflection[4],
        str(reflection),
    )

    # Alex same-world across bind
    a1_pkg = samples["A1"]["package"]
    a1_alex = samples["A1"]["alex"]
    check(
        "9. Alex continues SAME Educational Case (A1)",
        a1_alex.case_category == a1_pkg.story_spine.case_category
        and a1_alex.case_decision_point == a1_pkg.story_spine.decision_point
        and a1_alex.case_continuation_hook == a1_pkg.story_spine.continuation_hook
        and set(a1_alex.case_stakeholders) == set(a1_pkg.story_spine.stakeholders),
    )
    # Different CEFR → different archetype (not the same shallow world class)
    check(
        "9b. archetypes differ A1 vs C1",
        samples["A1"]["package"].story_spine.case_archetype
        != samples["C1"]["package"].story_spine.case_archetype,
    )

    print(f"\n=== M7 result: {PASS} passed, {FAIL} failed ===\n", flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
