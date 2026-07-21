"""M12.3 — POST /rehearsal/respond verifier.

Proves the voice Scene Practice turn pipeline:
  student audio → STT → Claude Scene Director → persist RehearsalState → TTS → response

Server owns the entire conversation. TTS failure never fails the turn.
Persistence happens BEFORE TTS.

Usage:
  python -u scripts/verify_speaking_m12_respond.py
"""

from __future__ import annotations

import asyncio
import base64
import inspect
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
        discussion_hooks=["Why was Anna waiting?"],
        continuation_hook="Greet the driver and thank Anna.",
        case_category="travel_interpersonal",
        case_archetype="honest_disclosure",
    )
    return EducationalPackage(
        package_id="pkg_m123_demo",
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


def main() -> int:
    print("\n=== M12.3 POST /rehearsal/respond ===\n", flush=True)

    import app.services.language_speaking_live_bridge.engine as engine_mod
    from app.schemas.language_speaking_live_bridge import LiveBridgeRespondOut
    from app.services.language_speaking_live_bridge import (
        build_speaking_scenario,
        respond_rehearsal_turn,
    )
    api_src = (BACKEND / "app/api/language_speaking_live_bridge.py").read_text(encoding="utf-8")
    from app.services.language_speaking_live_bridge.rehearsal import (
        REHEARSAL_PROVIDER_CLAUDE,
        start_rehearsal,
    )
    from app.services.language_speaking_live_bridge.scene_director import (
        validate_director_payload,
    )
    from app.services.language_speaking_live_bridge.storage import (
        merge_live_bridge_into_payload,
    )
    from app.services.language_speaking_live_bridge.types import LiveBridgeBundle
    from app.services.language_speaking_live_bridge_api import respond_rehearsal_api

    # --- 1. Surface / ownership ---
    engine_src = inspect.getsource(engine_mod.respond_rehearsal_turn)
    check("engine exports respond_rehearsal_turn", callable(respond_rehearsal_turn))
    check("api twin exports respond_rehearsal_api", callable(respond_rehearsal_api))
    check("route path /rehearsal/respond", "/rehearsal/respond" in api_src)
    check("route uses UploadFile", "UploadFile" in api_src and "File(...)" in api_src)
    check("response schema LiveBridgeRespondOut", "LiveBridgeRespondOut" in api_src)
    check("route calls respond_rehearsal_api", "respond_rehearsal_api" in api_src)
    check(
        "pipeline order STT before director",
        engine_src.index("_transcribe_student_audio")
        < engine_src.index("continue_rehearsal_turn"),
    )
    # Happy-path body: persist the mutation, then synthesize. The empty-transcript
    # branch may call TTS for a reprompt without mutating state — that is fine.
    persist_marker = "row.promotion_readiness_json = payload"
    check(
        "persist before TTS",
        persist_marker in engine_src
        and engine_src.index(persist_marker)
        < engine_src.rindex("**(await _tts_block(next_text))"),
    )
    check("uses claude via continue_rehearsal_turn", "continue_rehearsal_turn" in engine_src)
    check("passes stt_confidence", "stt_confidence=confidence" in engine_src)
    check("passes student_cefr", "student_cefr=" in engine_src)
    check("passes student_memory", "student_memory=" in engine_src)
    check("empty audio rejected", "empty_audio" in engine_src)
    check("empty transcript does not mutate", "heard" in engine_src and "False" in engine_src)

    # Schema contract
    fields = set(LiveBridgeRespondOut.model_fields)
    for required in (
        "heard",
        "student_transcript",
        "stt_confidence",
        "provider",
        "decision",
        "micro_correction",
        "coaching_note",
        "next_line",
        "audio_b64",
        "audio_mime",
        "bridge",
    ):
        check(f"schema has {required}", required in fields)

    # --- 2. Happy path (mocked STT + Claude + TTS) ---
    pkg = _sample_package()
    scenario = build_speaking_scenario(pkg)
    state, _voice = start_rehearsal(
        package=pkg, scenario=scenario, discussion_summary="Discussed honesty."
    )
    bundle = LiveBridgeBundle(
        package_id=pkg.package_id,
        scenario=scenario,
        rehearsal=state,
        discussion_summary="Discussed honesty.",
        journey_phase="gpt_rehearsal",
    )
    payload = merge_live_bridge_into_payload(
        {"speaking_case_memory": {"recent_themes": ["travel"]}},
        bundle,
    )
    row = SimpleNamespace(
        promotion_readiness_json=payload,
        official_speaking_cefr=SimpleNamespace(value="A2"),
    )

    directed = validate_director_payload(
        {
            "evaluation": {
                "grammar_issues": [],
                "vocabulary_issues": [],
                "missing_targets": ["delay"],
                "pronunciation_note": None,
            },
            "decision": "probe",
            "micro_correction": None,
            "coaching_note": "Try using 'delay'.",
            "next_line": {"speaker": "Anna", "text": "So what happened after you landed?"},
            "scene_beat": {"index": 2, "is_final": False},
        }
    )
    assert directed is not None

    async def fake_transcribe(*_a, **_k):
        return "Anna, I am sorry the flight was delayed.", 0.91

    async def fake_continue(state, **kwargs):
        check("cefr forwarded to director path", kwargs.get("student_cefr") == "A2")
        check(
            "memory forwarded to director path",
            isinstance(kwargs.get("student_memory"), dict)
            and "recent_themes" in (kwargs.get("student_memory") or {}),
        )
        check("stt confidence forwarded", kwargs.get("stt_confidence") == 0.91)
        state.turns.append({"role": "student", "text": kwargs["student_text"]})
        state.turns.append(
            {
                "role": "assistant",
                "text": directed["next_line"]["text"],
                "speaker": directed["next_line"]["speaker"],
            }
        )
        state.provider = REHEARSAL_PROVIDER_CLAUDE
        state.coaching_notes.append(directed["coaching_note"])
        state.evaluations.append(
            {
                "turn_index": 1,
                "decision": directed["decision"],
                **directed["evaluation"],
            }
        )
        state.scene_beat = directed["scene_beat"]
        return state

    async def fake_tts(text: str):
        check("tts receives claude line", "landed" in text.lower())
        return b"ID3fakeaudio", "audio/mpeg"

    async def fake_lock(*_a, **_k):
        return row

    async def fake_resolve(*_a, **_k):
        return pkg

    with (
        patch.object(engine_mod, "_lock_row", new=fake_lock),
        patch.object(engine_mod, "_resolve_package", new=fake_resolve),
        patch.object(engine_mod, "_transcribe_student_audio", new=fake_transcribe),
        patch.object(engine_mod, "continue_rehearsal_turn", new=fake_continue),
        patch.object(engine_mod, "synthesize_scene_line", new=fake_tts),
        patch.object(engine_mod, "flag_modified", new=lambda *_a, **_k: None),
        patch.object(engine_mod, "_weak_skills_from_payload", return_value=["fluency"]),
    ):
        view, turn = asyncio.run(
            respond_rehearsal_turn(
                AsyncMock(),
                student_id=1,
                language_id=1,
                audio_bytes=b"fake-webm-bytes",
                mime_type="audio/webm",
            )
        )

    check("heard true", turn["heard"] is True)
    check("student transcript from STT", turn["student_transcript"].startswith("Anna"))
    check("stt confidence returned", turn["stt_confidence"] == 0.91)
    check("provider is claude", turn["provider"] == REHEARSAL_PROVIDER_CLAUDE)
    check("decision probe", turn["decision"] == "probe")
    check("coaching note returned", "delay" in (turn["coaching_note"] or ""))
    check("next line text", turn["next_line"]["text"].startswith("So what"))
    check("next line speaker", turn["next_line"]["speaker"] == "Anna")
    check("audio_b64 present", bool(turn["audio_b64"]))
    check("audio_mime mpeg", turn["audio_mime"] == "audio/mpeg")
    check(
        "audio_b64 decodes",
        base64.b64decode(turn["audio_b64"]) == b"ID3fakeaudio",
    )
    check("bridge phase gpt_rehearsal", view.bundle.journey_phase == "gpt_rehearsal")
    check("persisted student+assistant turns", len(view.bundle.rehearsal.turns) >= 3)
    check("persisted evaluation", len(view.bundle.rehearsal.evaluations) == 1)
    check("persisted scene beat", view.bundle.rehearsal.scene_beat.get("index") == 2)
    check(
        "persisted into row payload",
        isinstance(row.promotion_readiness_json, dict),
    )

    # --- 3. TTS failure → text-only success (never fails the turn) ---
    state2, _ = start_rehearsal(package=pkg, scenario=scenario, discussion_summary="x")
    bundle2 = LiveBridgeBundle(
        package_id=pkg.package_id,
        scenario=scenario,
        rehearsal=state2,
        discussion_summary="x",
        journey_phase="gpt_rehearsal",
    )
    row2 = SimpleNamespace(
        promotion_readiness_json=merge_live_bridge_into_payload({}, bundle2),
        official_speaking_cefr=SimpleNamespace(value="A2"),
    )

    async def fake_continue2(state, **kwargs):
        state.turns.append({"role": "student", "text": kwargs["student_text"]})
        state.turns.append({"role": "assistant", "text": "Where do you want to go?", "speaker": "Taxi Driver"})
        state.provider = REHEARSAL_PROVIDER_CLAUDE
        state.evaluations.append({"turn_index": 1, "decision": "accept", "grammar_issues": [], "vocabulary_issues": [], "missing_targets": [], "pronunciation_note": None})
        state.scene_beat = {"index": 1, "is_final": False}
        return state

    async def tts_fail(_text: str):
        return None

    with (
        patch.object(engine_mod, "_lock_row", new=AsyncMock(return_value=row2)),
        patch.object(engine_mod, "_resolve_package", new=AsyncMock(return_value=pkg)),
        patch.object(engine_mod, "_transcribe_student_audio", new=AsyncMock(return_value=("Let's go home.", 0.8))),
        patch.object(engine_mod, "continue_rehearsal_turn", new=fake_continue2),
        patch.object(engine_mod, "synthesize_scene_line", new=tts_fail),
        patch.object(engine_mod, "flag_modified", new=lambda *_a, **_k: None),
        patch.object(engine_mod, "_weak_skills_from_payload", return_value=[]),
    ):
        _view2, turn2 = asyncio.run(
            respond_rehearsal_turn(
                AsyncMock(),
                student_id=1,
                language_id=1,
                audio_bytes=b"x",
                mime_type="audio/webm",
            )
        )
    check("tts fail still heard", turn2["heard"] is True)
    check("tts fail still returns text", bool(turn2["next_line"]["text"]))
    check("tts fail audio_b64 None", turn2["audio_b64"] is None)
    check("tts fail audio_mime None", turn2["audio_mime"] is None)
    check("tts fail still persisted", len(row2.promotion_readiness_json.get("speaking_live_bridge", {}).get("rehearsal", {}).get("turns", [])) >= 2 or len(_view2.bundle.rehearsal.turns) >= 2)

    # --- 4. Empty / unintelligible transcript → no state mutation ---
    state3, _ = start_rehearsal(package=pkg, scenario=scenario, discussion_summary="x")
    turns_before = len(state3.turns)
    bundle3 = LiveBridgeBundle(
        package_id=pkg.package_id,
        scenario=scenario,
        rehearsal=state3,
        discussion_summary="x",
        journey_phase="gpt_rehearsal",
    )
    row3 = SimpleNamespace(
        promotion_readiness_json=merge_live_bridge_into_payload({}, bundle3),
        official_speaking_cefr=SimpleNamespace(value="A2"),
    )
    continue_called = {"n": 0}

    async def continue_should_not(*_a, **_k):
        continue_called["n"] += 1
        raise AssertionError("director must not run on empty transcript")

    with (
        patch.object(engine_mod, "_lock_row", new=AsyncMock(return_value=row3)),
        patch.object(engine_mod, "_resolve_package", new=AsyncMock(return_value=pkg)),
        patch.object(engine_mod, "_transcribe_student_audio", new=AsyncMock(return_value=("", None))),
        patch.object(engine_mod, "continue_rehearsal_turn", new=continue_should_not),
        patch.object(engine_mod, "synthesize_scene_line", new=AsyncMock(return_value=(b"ID3", "audio/mpeg"))),
        patch.object(engine_mod, "flag_modified", new=lambda *_a, **_k: None),
    ):
        _view3, turn3 = asyncio.run(
            respond_rehearsal_turn(
                AsyncMock(),
                student_id=1,
                language_id=1,
                audio_bytes=b"silence",
                mime_type="audio/webm",
            )
        )
    check("empty transcript heard=False", turn3["heard"] is False)
    check("empty transcript no director", continue_called["n"] == 0)
    check("empty transcript has reprompt", bool(turn3["next_line"]["text"]))
    check("empty transcript turns unchanged", len(_view3.bundle.rehearsal.turns) == turns_before)

    # --- 5. Empty audio rejected ---
    async def _empty():
        try:
            await respond_rehearsal_turn(
                AsyncMock(),
                student_id=1,
                language_id=1,
                audio_bytes=b"",
                mime_type="audio/webm",
            )
            return False
        except engine_mod.LiveBridgeError as exc:
            return exc.code == "empty_audio"

    check("empty audio raises empty_audio", asyncio.run(_empty()))

    # --- 6. No active rehearsal rejected ---
    idle_row = SimpleNamespace(
        promotion_readiness_json={},
        official_speaking_cefr=SimpleNamespace(value="A2"),
    )

    async def _no_reh():
        with patch.object(engine_mod, "_lock_row", new=AsyncMock(return_value=idle_row)):
            try:
                await respond_rehearsal_turn(
                    AsyncMock(),
                    student_id=1,
                    language_id=1,
                    audio_bytes=b"x",
                    mime_type="audio/webm",
                )
                return False
            except engine_mod.LiveBridgeError as exc:
                return exc.code == "no_rehearsal"

    check("no rehearsal raises no_rehearsal", asyncio.run(_no_reh()))

    # --- 7. API error mapping ---
    from app.services.language_speaking_live_bridge_api.service import _map

    mapped = _map(engine_mod.LiveBridgeError("stt_unavailable", "Could not hear"))
    check("stt_unavailable maps to 503", mapped.status_code == 503)
    mapped2 = _map(engine_mod.LiveBridgeError("empty_audio", "No audio"))
    check("empty_audio maps to 400", mapped2.status_code == 400)

    # --- 8. Isolation: no frontend, no Realtime in respond path ---
    check("respond does not mint realtime", "mint_realtime" not in engine_src)
    check("respond does not sync client transcript", "sync_rehearsal" not in engine_src)
    check("respond does not open webrtc", "webrtc" not in engine_src.lower())

    print(f"\nResult: {PASS} passed, {FAIL} failed\n", flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
