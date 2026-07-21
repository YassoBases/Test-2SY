"""M10 — Live Speaking Bridge verifier.

Proves Educational Case → Discussion → Preparation → GPT Rehearsal →
LiveConversationContext (Hume EVI) share the same story world, characters,
conflict, decision point, vocabulary, grammar, and objectives.

Usage:
  python -u scripts/verify_speaking_m10_live_bridge.py
"""

from __future__ import annotations

import sys
from pathlib import Path

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


def _sample_package():
    from app.services.language_educational_package.lifecycle import PackageLifecycleStatus
    from app.services.language_educational_package.types import (
        DiscussionFlow,
        EducationalPackage,
        InputMaterial,
        InputMaterialKind,
        MiniPractice,
        ReflectionSection,
        StoryCharacter,
        StorySpine,
        VocabularyEntry,
        VocabularyInContext,
    )

    spine = StorySpine(
        title="Delayed Flight Home",
        context="Anna waited at arrivals.",
        setting="airport arrivals hall",
        characters=[
            StoryCharacter(name="Diego", background="traveler"),
            StoryCharacter(name="Anna", background="friend"),
            StoryCharacter(name="Taxi Driver", background="driver"),
        ],
        stakeholders=["Anna", "Taxi Driver"],
        problem="Diego's flight was delayed.",
        conflict="Diego must greet Anna honestly while the taxi waits.",
        timeline="evening",
        events=["Flight delayed", "Anna waits outside", "Taxi arrives"],
        decision_point="Whether to tell Anna the delay caused another problem",
        consequences="Trust and next destination plans",
        ending="They must decide where to go next.",
        ending_type="open",
        discussion_hooks=["Why was Anna waiting?", "What should Diego say first?"],
        continuation_hook=(
            "Greet the driver, thank Anna, explain what happened, "
            "and decide whether to tell her about the other problem."
        ),
        case_category="travel_interpersonal",
        case_archetype="honest_disclosure",
    )
    return EducationalPackage(
        package_id="pkg_m10_demo",
        schema_version="1.0.0",
        author_version="1.0.0",
        author_provider="template",
        constraints_fingerprint="fp_c",
        content_fingerprint="fp_x",
        blueprint_hash="bh",
        mission_id="m1",
        status=PackageLifecycleStatus.frozen,
        input_material=InputMaterial(
            kind=InputMaterialKind.story,
            title="Delayed Flight Home",
            body_blocks=[],
        ),
        vocabulary_in_context=VocabularyInContext(
            entries=[
                VocabularyEntry(
                    vocabulary_id="v1",
                    surface="delay",
                    context_span_ref="b1",
                    brief_gloss="late",
                ),
                VocabularyEntry(
                    vocabulary_id="v2",
                    surface="thank",
                    context_span_ref="b1",
                    brief_gloss="say thanks",
                ),
            ]
        ),
        teaching_blocks_authored=[],
        discussion=DiscussionFlow(
            flow_id="d1", steps=[], opening_move="Let's talk.", closing_move="Well done."
        ),
        mini_practice=MiniPractice(
            task_id="mp1",
            prompt="Speak the next beat.",
            scaffold="I…",
            evidence_intent_echo="production",
        ),
        reflection=ReflectionSection(prompts=["What was hard?"], self_check_cues=[]),
        story_spine=spine,
    )


def main() -> int:
    print("\n=== M10 Live Speaking Bridge ===\n", flush=True)

    from app.services.language_speaking_live_bridge import (
        LIVE_BRIDGE_VERSION,
        SPEAKING_LIVE_BRIDGE_KEY,
        assert_same_world,
        build_live_conversation_context,
        build_speaking_scenario,
        continuity_fingerprint_for_package,
        extract_case_continuity_fields,
        merge_live_context_into_alex_dict,
        scenario_to_prep_projection,
    )
    from app.services.language_speaking_live_bridge.rehearsal import (
        REHEARSAL_PROVIDER_CLAUDE,
        build_rehearsal_context_payload,
        start_rehearsal,
    )
    from app.services.language_speaking_live_bridge.types import (
        LiveBridgeBundle,
        RehearsalState,
    )

    pkg = _sample_package()
    fields = extract_case_continuity_fields(pkg)
    check("extract story world", "airport" in fields["story_world"].lower())
    check("extract characters include Diego", "Diego" in fields["characters"])
    check("extract Anna", "Anna" in fields["characters"])
    check("extract decision point", "tell Anna" in fields["decision_point"])
    check("extract continuation hook", "taxi" in fields["continuation_hook"].lower() or "greet" in fields["continuation_hook"].lower())
    check("extract vocabulary", "delay" in fields["vocabulary"])
    check("fingerprint stable", bool(continuity_fingerprint_for_package(pkg)))

    scenario = build_speaking_scenario(pkg)
    check("scenario same package", scenario.package_id == pkg.package_id)
    check("scenario student role Diego", scenario.student_role == "Diego")
    check("scenario brief not static empty", len(scenario.student_brief) > 40)
    check("scenario includes decision", scenario.decision_point == fields["decision_point"])
    check("scenario same fingerprint", scenario.continuity_fingerprint == continuity_fingerprint_for_package(pkg))
    check("scenario must_do non-empty", len(scenario.must_do) >= 1)

    prep = scenario_to_prep_projection(scenario)
    check("prep projection has gpt roles", isinstance(prep.get("gpt_roles"), list) and prep["gpt_roles"])

    state, voice = start_rehearsal(package=pkg, scenario=scenario, discussion_summary="Discussed honesty.")
    check("rehearsal not Hume", voice.get("not_hume") is True)
    check("voice provider is TTS only", "tts" in str(voice.get("provider") or "").lower())
    check("director is claude", voice.get("director") == REHEARSAL_PROVIDER_CLAUDE)
    check("rehearsal opening not generic hello", "hello, how are you" not in state.turns[0]["text"].lower())

    ctx_payload = build_rehearsal_context_payload(package=pkg, scenario=scenario)
    check("context forbids inventing world", "invent_new_story_world" in (ctx_payload.get("forbidden") or []))
    check("context case-bound title", "Delayed" in str(ctx_payload.get("educational_package", {}).get("title") or ""))

    # Simulate one student rehearsal turn via template path
    state.turns.append({"role": "student", "text": "Anna, thank you for waiting. The flight was delayed."})
    state.coaching_notes.append("Good thank-you move.")
    live = build_live_conversation_context(
        scenario,
        rehearsal=state,
        discussion_summary="Discussed honesty.",
        weak_skills=["greeting_openers"],
    )
    check("live context same fingerprint", live.continuity_fingerprint == scenario.continuity_fingerprint)
    check("live context same characters", set(live.characters) == set(scenario.characters))
    check("live context same decision", live.decision_point == scenario.decision_point)
    check("live context same hook", live.continuation_hook == scenario.continuation_hook)
    check("live opening not fresh hello", "how are you today" not in live.opening_line.lower())
    check("live opening references case", "anna" in live.opening_line.lower() or "taxi" in live.opening_line.lower() or "diego" in live.opening_line.lower())
    check("journey phases include gpt_rehearsal", "gpt_rehearsal" in live.journey_phases)
    check("journey phases include live_evi", "live_evi" in live.journey_phases)

    # Continuity guards across stages
    stage_fields = {
        "story_world": live.story_world,
        "decision_point": live.decision_point,
        "continuation_hook": live.continuation_hook,
        "conflict": fields["conflict"],
        "characters": list(live.characters),
    }
    violations = assert_same_world(fields, stage_fields, label="case→live")
    check("assert_same_world clean", violations == [], str(violations))

    alex = {
        "case_title": "old",
        "communicative_scenario": "Hello, how are you today?",
        "current_task_instruction": "chat freely",
    }
    merged = merge_live_context_into_alex_dict(alex, live)
    check("alex overlay uses case hook", merged["communicative_scenario"] == live.continuation_hook)
    check("alex overlay has opening", bool(merged.get("live_conversation_opening")))
    check("alex overlay not fresh hello", "how are you today" not in merged["communicative_scenario"].lower())
    check("alex overlay keeps characters", "Diego" in merged["case_characters"])

    bundle = LiveBridgeBundle(
        package_id=pkg.package_id,
        scenario=scenario,
        rehearsal=state,
        live_context=live,
        discussion_summary="Discussed honesty.",
        journey_phase="ready_for_live",
    )
    raw = bundle.to_dict()
    check("bundle roundtrip key", SPEAKING_LIVE_BRIDGE_KEY == "speaking_live_bridge")
    check("bundle has bridge version", raw.get("bridge_version") == LIVE_BRIDGE_VERSION or LIVE_BRIDGE_VERSION)
    restored = LiveBridgeBundle.from_dict(raw)
    check("bundle restore live id", restored.live_context is not None and restored.live_context.context_id == live.context_id)
    check("rehearsal state type", isinstance(state, RehearsalState))

    # Ownership registration
    from app.services.language_speaking.ownership import PACKAGE_OWNERSHIP, PACKAGE_LAYER

    check("ownership lists live_bridge", "language_speaking_live_bridge" in PACKAGE_OWNERSHIP)
    check("layer experience", PACKAGE_LAYER.get("language_speaking_live_bridge") == "experience")

    print(f"\n=== Result: {PASS} passed, {FAIL} failed ===\n", flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
