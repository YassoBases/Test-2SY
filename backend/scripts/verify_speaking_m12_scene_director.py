"""M12.1 — Claude Scene Director verifier.

Proves that Claude (and only Claude) reasons about Scene Practice turns:
- scene_director.py contract, validation, provider labels
- template fallback when Claude is unconfigured or fails
- continue_rehearsal_turn no longer performs GPT reasoning
- RehearsalState round-trips new evaluations/scene_beat fields

Usage:
  python -u scripts/verify_speaking_m12_scene_director.py
"""

from __future__ import annotations

import asyncio
import inspect
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
        package_id="pkg_m12_demo",
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


def _good_director_payload() -> dict:
    return {
        "evaluation": {
            "grammar_issues": ["past tense of 'go'"],
            "vocabulary_issues": [],
            "missing_targets": ["delay"],
            "pronunciation_note": None,
        },
        "decision": "probe",
        "micro_correction": None,
        "coaching_note": "Try using 'delay' in your next line.",
        "next_line": {"speaker": "Anna", "text": "So what happened after you landed?"},
        "scene_beat": {"index": 2, "is_final": False},
    }


def main() -> int:
    print("\n=== M12.1 Claude Scene Director ===\n", flush=True)

    import app.services.language_speaking_live_bridge.rehearsal as rehearsal_mod
    import app.services.language_speaking_live_bridge.scene_director as director_mod
    from app.services.language_speaking_live_bridge import build_speaking_scenario
    from app.services.language_speaking_live_bridge.rehearsal import (
        REHEARSAL_PROVIDER_CLAUDE,
        REHEARSAL_PROVIDER_TEMPLATE,
        continue_rehearsal_turn,
        start_rehearsal,
    )
    from app.services.language_speaking_live_bridge.scene_director import (
        DIRECTOR_DECISIONS,
        DIRECTOR_PROVIDER_CLAUDE,
        DIRECTOR_PROVIDER_TEMPLATE,
        SCENE_DIRECTOR_SYSTEM,
        SCENE_OPENING_SYSTEM,
        direct_scene_opening,
        direct_scene_turn,
        validate_director_payload,
    )
    from app.services.language_speaking_live_bridge.types import RehearsalState

    # --- 1. Ownership: Claude only, no GPT reasoning in the director ---
    director_src = inspect.getsource(director_mod)
    check("director provider label", DIRECTOR_PROVIDER_CLAUDE == "claude-scene-director")
    check("template provider label", DIRECTOR_PROVIDER_TEMPLATE == "template_fallback")
    check("director imports claude_service", "claude_service" in director_src)
    check("director has no openai url", "openai.com" not in director_src.lower())
    check("director has no httpx", "httpx" not in director_src)
    check("director has no realtime", "realtime" not in director_src.lower())
    check(
        "decisions are A-D",
        DIRECTOR_DECISIONS == ("correct", "accept", "probe", "advance"),
    )

    # --- 2. System prompt contract ---
    sys_lower = SCENE_DIRECTOR_SYSTEM.lower()
    check("prompt: silent evaluation first", "silently evaluate" in sys_lower)
    check("prompt: all four decisions", all(d in sys_lower for d in DIRECTOR_DECISIONS))
    check("prompt: never invent world", "never invent a new world" in sys_lower)
    check("prompt: no scores/cefr", "no scores" in sys_lower and "cefr" in sys_lower)
    check("prompt: forbids hello opening", "hello" in sys_lower)
    check("prompt: json contract keys", all(k in SCENE_DIRECTOR_SYSTEM for k in (
        "evaluation", "decision", "micro_correction", "coaching_note", "next_line", "scene_beat",
    )))
    check(
        "prompt: pronunciation honesty",
        "never invent pronunciation feedback" in sys_lower,
    )
    check("opening prompt: in character", "in character" in SCENE_OPENING_SYSTEM.lower())

    # --- 3. Contract validation ---
    good = validate_director_payload(_good_director_payload())
    check("valid payload accepted", good is not None)
    check("valid payload decision kept", good and good["decision"] == "probe")
    check("valid payload line kept", good and good["next_line"]["text"].startswith("So what"))
    check("valid payload beat kept", good and good["scene_beat"] == {"index": 2, "is_final": False})

    missing_line = _good_director_payload()
    missing_line.pop("next_line")
    check("missing next_line rejected", validate_director_payload(missing_line) is None)

    empty_line = _good_director_payload()
    empty_line["next_line"] = {"speaker": "Anna", "text": "   "}
    check("empty line rejected", validate_director_payload(empty_line) is None)

    bad_decision = _good_director_payload()
    bad_decision["decision"] = "lecture"
    check("unknown decision rejected", validate_director_payload(bad_decision) is None)

    check("non-dict rejected", validate_director_payload("nope") is None)

    hollow_correct = _good_director_payload()
    hollow_correct["decision"] = "correct"
    hollow_correct["micro_correction"] = None
    coerced = validate_director_payload(hollow_correct)
    check("correct without correction coerced to accept", coerced and coerced["decision"] == "accept")

    long_line = _good_director_payload()
    long_line["next_line"]["text"] = "x" * 5000
    trimmed = validate_director_payload(long_line)
    check("long line truncated", trimmed and len(trimmed["next_line"]["text"]) <= 600)

    with_correction = _good_director_payload()
    with_correction["decision"] = "correct"
    with_correction["micro_correction"] = {"brief": "past tense", "corrected_form": "I went"}
    wc = validate_director_payload(with_correction)
    check("correction preserved", wc and wc["micro_correction"]["corrected_form"] == "I went")

    # --- 4. Claude unconfigured => director declines (caller falls back) ---
    orig_configured = director_mod.is_claude_configured
    director_mod.is_claude_configured = lambda: False
    try:
        declined = asyncio.run(
            direct_scene_turn(
                context={}, recent_turns=[], student_transcript="hi", scene_beat=None
            )
        )
        check("unconfigured claude declines turn", declined is None)
        declined_open = asyncio.run(direct_scene_opening(context={}))
        check("unconfigured claude declines opening", declined_open is None)
    finally:
        director_mod.is_claude_configured = orig_configured

    # --- 5. Runtime wiring: continue_rehearsal_turn uses the director ---
    continue_src = inspect.getsource(rehearsal_mod.continue_rehearsal_turn)
    check("turn no longer calls gpt", "_call_gpt_rehearsal" not in continue_src)
    check("turn calls scene director", "direct_scene_turn" in continue_src)

    pkg = _sample_package()
    scenario = build_speaking_scenario(pkg)
    state, _voice = start_rehearsal(
        package=pkg, scenario=scenario, discussion_summary="Discussed honesty."
    )

    async def _fake_directed(**_kwargs):
        return validate_director_payload(_good_director_payload())

    orig_direct = rehearsal_mod.direct_scene_turn
    rehearsal_mod.direct_scene_turn = _fake_directed
    try:
        state = asyncio.run(
            continue_rehearsal_turn(
                state,
                package=pkg,
                student_text="Anna, I am sorry the flight was delayed.",
                discussion_summary="Discussed honesty.",
            )
        )
    finally:
        rehearsal_mod.direct_scene_turn = orig_direct

    check("provider is claude scene director", state.provider == REHEARSAL_PROVIDER_CLAUDE)
    check("student turn recorded", state.turns[-2]["role"] == "student")
    check("assistant turn is claude's line", state.turns[-1]["text"].startswith("So what"))
    check("coaching note persisted", any("delay" in n for n in state.coaching_notes))
    check("evaluation persisted", len(state.evaluations) == 1)
    check("evaluation has decision", state.evaluations[0].get("decision") == "probe")
    check("scene beat persisted", state.scene_beat == {"index": 2, "is_final": False})

    # --- 6. Director failure => template fallback (never another LLM) ---
    async def _fail_directed(**_kwargs):
        return None

    rehearsal_mod.direct_scene_turn = _fail_directed
    try:
        state = asyncio.run(
            continue_rehearsal_turn(
                state,
                package=pkg,
                student_text="And then we took the taxi together.",
                discussion_summary="Discussed honesty.",
            )
        )
    finally:
        rehearsal_mod.direct_scene_turn = orig_direct

    check("fallback provider is template", state.provider == REHEARSAL_PROVIDER_TEMPLATE)
    check("fallback still answers", state.turns[-1]["role"] == "assistant" and bool(state.turns[-1]["text"]))

    # --- 7. RehearsalState round-trip with new fields ---
    rt = RehearsalState.from_dict(state.to_dict())
    check("round-trip evaluations", rt is not None and rt.evaluations == state.evaluations)
    check("round-trip scene beat", rt is not None and rt.scene_beat == state.scene_beat)

    legacy = state.to_dict()
    legacy.pop("evaluations")
    legacy.pop("scene_beat")
    legacy_state = RehearsalState.from_dict(legacy)
    check("legacy payload loads", legacy_state is not None)
    check("legacy defaults empty", legacy_state.evaluations == [] and legacy_state.scene_beat == {})

    print(f"\nResult: {PASS} passed, {FAIL} failed\n", flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
