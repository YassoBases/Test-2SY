"""M8 — Adaptive Educational Case Personalization verifier.

Same curriculum (CEFR / vocab / grammar / objectives / difficulty) for three
students with different age, profession, interests, goals, and history.
Verifies experience changes while ownership stays with Curriculum Engine.

Usage:
  python -u scripts/verify_speaking_m8_case_personalization.py
"""

from __future__ import annotations

import copy
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


def _curriculum_slice(cons) -> dict:
    return {
        "cefr": cons.official_cefr.upper(),
        "learning_focus": cons.learning_focus,
        "objectives": list(cons.objectives),
        "vocab_ids": list(cons.vocabulary_ids),
        "vocab_surfaces": list(cons.vocabulary_surface_forms),
        "grammar_ids": list(cons.grammar_topic_ids),
        "difficulty": cons.difficulty,
        "case_category": cons.case_category,
        "case_archetype": cons.case_archetype,
        "decision_complexity": (cons.story_complexity_policy or {}).get("decision_complexity"),
        "min_words": (cons.story_complexity_policy or {}).get("min_words"),
    }


def _base_enriched_payload(cefr: str = "B2"):
    from app.services.language_speaking_curriculum_engine import enrich_speaking_constraints_payload
    from app.services.language_speaking_diagnostic.selector import select_speaking_target
    from app.services.language_speaking_knowledge_model.storage import empty_knowledge_model
    from app.services.language_speaking_lesson_planner.planner import assemble_speaking_lesson_blueprint
    from app.services.language_speaking_runtime_api.journey_constraints import (
        build_constraints_payload_from_journey,
    )

    km = empty_knowledge_model(student_id=8800, language_id=1)
    rec = select_speaking_target(km, official_cefr=cefr, speaking_goal="general_english")
    bp = assemble_speaking_lesson_blueprint(rec)
    try:
        bp.official_cefr_hint = cefr
    except Exception:
        pass
    row = SimpleNamespace(
        official_speaking_cefr=SimpleNamespace(value=cefr),
        learning_stage_speaking=2,
        promotion_readiness_json={},
    )
    payload = build_constraints_payload_from_journey(row=row, blueprint=bp, session=None)
    payload["official_cefr"] = cefr
    if not payload.get("vocabulary_targets"):
        payload = enrich_speaking_constraints_payload(payload)
    return payload


def _generate_for_student(base_payload: dict, signals, label: str):
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_case_personalization import (
        apply_case_personalization,
        snapshot_curriculum_fields,
    )
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_lesson_planner.planner import continue_alex_from_story_spine
    from app.services.language_speaking_lesson_planner.types import AlexTutoringContext

    before = snapshot_curriculum_fields(base_payload)
    personalized = apply_case_personalization(copy.deepcopy(base_payload), signals)
    after = snapshot_curriculum_fields(personalized)
    check(f"{label}. curriculum snapshot unchanged", before == after)

    constraints = build_speaking_package_constraints(personalized)
    raw = author_package_json_template(constraints)
    result = process_package_generation(
        constraints,
        raw,
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    check(f"{label}. generation success", result.success and result.package is not None)
    assert result.package is not None
    pkg = result.package

    alex_seed = AlexTutoringContext(
        session_goal="Continue today's Educational Case",
        target_skill_label=constraints.learning_focus,
        communicative_scenario="placeholder",
        encourage_behaviors=("warm",),
        elicit_behaviors=("elicit",),
        retry_focus="same case",
        conversation_constraints=("same world",),
    )
    alex = continue_alex_from_story_spine(
        alex_seed,
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
    perso = constraints.personalization or {}
    if perso.get("alex_notes"):
        alex_notes = " ".join(perso.get("alex_notes") or [])
        from dataclasses import replace

        alex = replace(
            alex,
            communicative_scenario=f"{alex.communicative_scenario} {alex_notes}".strip(),
        )

    return {
        "label": label,
        "constraints": constraints,
        "package": pkg,
        "alex": alex,
        "personalized_payload": personalized,
    }


def main() -> int:
    print("\n=== M8 Educational Case personalization (3 students) ===\n", flush=True)

    from app.services.language_speaking import ownership as owning
    from app.services.language_speaking_case_personalization import (
        PERSONALIZATION_ENGINE_VERSION,
        build_signals_from_parts,
        signals_are_substantive,
    )

    check(
        "engine version 1.x",
        PERSONALIZATION_ENGINE_VERSION.startswith("1."),
    )
    check(
        "ownership registers personalization",
        "language_speaking_case_personalization" in owning.PACKAGE_OWNERSHIP,
    )
    check(
        "empty signals skip personalization",
        not signals_are_substantive(build_signals_from_parts(student_id=1)),
    )

    base = _base_enriched_payload("B2")
    # Force a negotiation-like identity when present; otherwise keep curriculum category.
    # Curriculum remains owner — we do not rewrite case_category here.

    students = {
        "A_football": build_signals_from_parts(
            student_id=101,
            age=22,
            occupation="student",
            future_goal="sports journalism",
            learning_style="practical",
            explanation_style="simple",
            interests=["football", "sports"],
            hobbies=["football"],
            favorite_topics=["football clubs"],
            culture_hint="arabic_levant",
        ),
        "B_medical": build_signals_from_parts(
            student_id=102,
            age=24,
            occupation="medical_student",
            future_goal="doctor",
            learning_style="theoretical",
            explanation_style="detailed",
            interests=["medicine", "healthcare"],
            hobbies=["reading medical news"],
            favorite_topics=["hospital work"],
            culture_hint="international",
            used_settings=["airport", "airport arrivals"],
            completed_case_titles=["Late at Arrivals"],
        ),
        "C_business": build_signals_from_parts(
            student_id=103,
            age=35,
            occupation="business_owner",
            future_goal="business",
            learning_style="practical",
            explanation_style="normal",
            interests=["business", "negotiation"],
            hobbies=["entrepreneurship"],
            favorite_topics=["supplier contracts"],
            culture_hint="international",
            weak_skill_labels=["speaking rate"],
            recent_mistake_tags=["hesitation"],
        ),
    }

    # Sanity: all substantive
    for label, sig in students.items():
        check(f"{label}. signals substantive", signals_are_substantive(sig))

    results = {}
    for label, sig in students.items():
        print(f"\n--- Student {label} ---", flush=True)
        results[label] = _generate_for_student(base, sig, label)

    a = results["A_football"]
    b = results["B_medical"]
    c = results["C_business"]

    print("\n--- Curriculum identity identical ---", flush=True)
    sa, sb, sc = _curriculum_slice(a["constraints"]), _curriculum_slice(b["constraints"]), _curriculum_slice(c["constraints"])
    check("objectives identical", sa["objectives"] == sb["objectives"] == sc["objectives"])
    check("vocabulary ids identical", sa["vocab_ids"] == sb["vocab_ids"] == sc["vocab_ids"])
    check("vocabulary surfaces identical", sa["vocab_surfaces"] == sb["vocab_surfaces"] == sc["vocab_surfaces"])
    check("grammar ids identical", sa["grammar_ids"] == sb["grammar_ids"] == sc["grammar_ids"])
    check("CEFR identical", sa["cefr"] == sb["cefr"] == sc["cefr"])
    check("difficulty identical", sa["difficulty"] == sb["difficulty"] == sc["difficulty"])
    check(
        "case_category identical",
        sa["case_category"] == sb["case_category"] == sc["case_category"],
    )
    check(
        "case_archetype identical",
        sa["case_archetype"] == sb["case_archetype"] == sc["case_archetype"],
    )
    check(
        "decision complexity identical",
        sa["decision_complexity"] == sb["decision_complexity"] == sc["decision_complexity"],
    )
    check("learning_focus identical", sa["learning_focus"] == sb["learning_focus"] == sc["learning_focus"])

    print("\n--- Experience differs ---", flush=True)
    worlds = {
        k: results[k]["package"].story_spine.context.lower()
        + " "
        + results[k]["constraints"].story_world.lower()
        for k in results
    }
    settings = {k: results[k]["package"].story_spine.setting.lower() for k in results}
    check(
        "story worlds differ across students",
        len({worlds["A_football"], worlds["B_medical"], worlds["C_business"]}) >= 2,
        str({k: worlds[k][:80] for k in worlds}),
    )
    # With M9 progression shell, personalization may flavor rather than replace worlds —
    # interests must still surface in personalization directives and/or discussion.
    perso_a = a["constraints"].personalization or {}
    perso_b = b["constraints"].personalization or {}
    perso_c = c["constraints"].personalization or {}
    check(
        "football framing present for A",
        "football" in worlds["A_football"]
        or "club" in worlds["A_football"]
        or "football" in " ".join(perso_a.get("interest_labels") or []).lower(),
        worlds["A_football"][:120],
    )
    check(
        "medical/hospital framing present for B",
        any(
            x in worlds["B_medical"]
            for x in ("hospital", "clinic", "medical", "doctor", "patient")
        )
        or any(
            x in " ".join(perso_b.get("interest_labels") or []).lower()
            for x in ("medicine", "medical", "healthcare")
        ),
        worlds["B_medical"][:120],
    )
    check(
        "business/supplier framing present for C",
        any(x in worlds["C_business"] for x in ("business", "supplier", "contract", "owner"))
        or any(
            x in " ".join(perso_c.get("interest_labels") or []).lower()
            for x in ("business", "supplier")
        ),
        worlds["C_business"][:120],
    )
    # M9 progression may lock setting/title to the Curriculum Graph case shell.
    # Personalization must still differentiate experience via flavor + discussion + Alex.
    perso_blobs = {
        k: " ".join(
            [
                " ".join((results[k]["constraints"].personalization or {}).get("interest_labels") or []),
                " ".join(
                    (results[k]["constraints"].personalization or {}).get(
                        "discussion_interest_hooks"
                    )
                    or []
                ),
                str((results[k]["constraints"].personalization or {}).get("theme_key") or ""),
                results[k]["constraints"].story_world.lower(),
            ]
        ).lower()
        for k in results
    }
    check(
        "personalization experience blobs differ",
        len(set(perso_blobs.values())) >= 2,
        str({k: perso_blobs[k][:80] for k in perso_blobs}),
    )
    check(
        "settings either differ or progression-locked shell is shared",
        len(set(settings.values())) >= 2
        or all(
            bool((results[k]["constraints"].curriculum_progression or {}))
            for k in results
        ),
        str(settings),
    )

    # Memory: B avoided airport reuse
    check(
        "B avoided airport setting after memory",
        "airport" not in settings["B_medical"],
        settings["B_medical"],
    )

    print("\n--- Discussion / Alex personalization ---", flush=True)
    disc = {
        k: (
            results[k]["package"].discussion.opening_move
            + " "
            + " ".join(s.prompt for s in results[k]["package"].discussion.steps)
        ).lower()
        for k in results
    }
    check(
        "A discussion references football interest",
        "football" in disc["A_football"],
        disc["A_football"][:160],
    )
    check(
        "B discussion references medical interest",
        any(x in disc["B_medical"] for x in ("medical", "hospital", "patient", "healthcare")),
        disc["B_medical"][:160],
    )
    check(
        "discussion text not identical across students",
        len({disc["A_football"], disc["B_medical"], disc["C_business"]}) >= 2,
    )

    alex_scenarios = {k: results[k]["alex"].communicative_scenario.lower() for k in results}
    check(
        "Alex continues A's football case",
        results["A_football"]["alex"].case_continuation_hook
        == results["A_football"]["package"].story_spine.continuation_hook
        and results["A_football"]["alex"].case_category
        == results["A_football"]["package"].story_spine.case_category,
    )
    check(
        "Alex notes differ with student history",
        alex_scenarios["A_football"] != alex_scenarios["C_business"]
        or "speaking rate" in alex_scenarios["C_business"]
        or "hesitation" in alex_scenarios["C_business"],
        str({k: alex_scenarios[k][:100] for k in alex_scenarios}),
    )
    check(
        "Alex case_category unchanged from package/curriculum",
        results["A_football"]["alex"].case_category
        == results["A_football"]["constraints"].case_category,
    )

    print(f"\n=== M8 result: {PASS} passed, {FAIL} failed ===\n", flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
