"""M11 (retired) — GPT Realtime anti-regression after M12.5.

Proves OpenAI Realtime / WebRTC Scene Practice infrastructure is gone and that
M12 Claude Scene Director + TTS/STT ownership remains intact for Alex handoff.

Usage:
  python -u scripts/verify_speaking_m11_realtime_scene_practice.py
"""

from __future__ import annotations

import ast
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


def _read(rel: str) -> str:
    return (BACKEND / rel).read_text(encoding="utf-8")


def main() -> int:
    print("\n=== M11 retired — Realtime removed (M12.5) ===\n", flush=True)

    api_src = _read("app/api/language_speaking_live_bridge.py")
    schema_src = _read("app/schemas/language_speaking_live_bridge.py")
    rehearsal_src = _read("app/services/language_speaking_live_bridge/rehearsal.py")
    engine_src = _read("app/services/language_speaking_live_bridge/engine.py")
    api_twin_src = _read("app/services/language_speaking_live_bridge_api/service.py")
    config_src = _read("app/core/config.py")
    fe_api = (BACKEND.parent / "src/api/speakingLiveBridge.js").read_text(encoding="utf-8")
    fe_bridge = (BACKEND.parent / "src/composables/useSpeakingLiveBridge.js").read_text(
        encoding="utf-8"
    )
    fe_voice = BACKEND.parent / "src/composables/useScenePracticeVoice.js"
    fe_realtime = BACKEND.parent / "src/composables/useScenePracticeRealtime.js"

    check("no /rehearsal/realtime-session route", "realtime-session" not in api_src)
    check("no /rehearsal/sync route", "/rehearsal/sync" not in api_src and "sync_rehearsal" not in api_src)
    check("respond route remains", "/rehearsal/respond" in api_src)
    check("no LiveBridgeRealtimeSessionOut schema", "LiveBridgeRealtimeSessionOut" not in schema_src)
    check("no LiveBridgeRehearsalSyncIn schema", "LiveBridgeRehearsalSyncIn" not in schema_src)

    check("no mint_realtime_session", "mint_realtime_session" not in rehearsal_src)
    check("no sync_rehearsal_snapshot", "sync_rehearsal_snapshot" not in rehearsal_src)
    check("no realtime client_secrets url", "realtime/client_secrets" not in rehearsal_src)
    check("no _call_gpt_rehearsal", "_call_gpt_rehearsal" not in rehearsal_src)
    check("no httpx in rehearsal", "httpx" not in rehearsal_src)
    check("claude director wired", "direct_scene_turn" in rehearsal_src)

    check("engine has no mint_rehearsal_realtime", "mint_rehearsal_realtime" not in engine_src)
    check("engine has no sync_rehearsal_transcript", "sync_rehearsal_transcript" not in engine_src)
    check("api twin has no mint/sync", "mint_realtime" not in api_twin_src and "sync_rehearsal" not in api_twin_src)

    check("no SPEAKING_REALTIME_MODEL config", "SPEAKING_REALTIME_MODEL" not in config_src)
    check("SPEAKING_TTS_MODEL remains", "SPEAKING_TTS_MODEL" in config_src)

    check("frontend no mintSpeakingRealtime", "mintSpeakingRealtime" not in fe_api)
    check("frontend no syncSpeakingRehearsal", "syncSpeakingRehearsal" not in fe_api)
    check("frontend has respondSpeakingRehearsal", "respondSpeakingRehearsal" in fe_api)
    check("frontend no syncRehearsal composable", "syncRehearsal" not in fe_bridge)
    check("useScenePracticeVoice exists", fe_voice.is_file())
    check("useScenePracticeRealtime deleted", not fe_realtime.is_file())

    # Continuity: LCC handoff still works without client sync
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
    from app.services.language_speaking_live_bridge import (
        build_live_conversation_context,
        build_speaking_scenario,
        merge_live_context_into_alex_dict,
    )
    from app.services.language_speaking_live_bridge.rehearsal import start_rehearsal

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
        events=["Flight delayed"],
        decision_point="Whether to tell Anna the delay caused another problem",
        consequences="Trust",
        ending="They must decide where to go next.",
        ending_type="open",
        discussion_hooks=["Why was Anna waiting?"],
        continuation_hook="Greet the driver and thank Anna.",
        case_category="travel_interpersonal",
        case_archetype="honest_disclosure",
    )
    pkg = EducationalPackage(
        package_id="pkg_m11_retire",
        schema_version="1.0.0",
        author_version="1.0.0",
        author_provider="template",
        constraints_fingerprint="fp_c",
        content_fingerprint="fp_x",
        blueprint_hash="bh",
        mission_id="m1",
        status=PackageLifecycleStatus.frozen,
        input_material=InputMaterial(
            kind=InputMaterialKind.story, title="Delayed Flight Home", body_blocks=[]
        ),
        vocabulary_in_context=VocabularyInContext(
            entries=[
                VocabularyEntry(
                    vocabulary_id="v1",
                    surface="delay",
                    context_span_ref="b1",
                    brief_gloss="late",
                )
            ]
        ),
        teaching_blocks_authored=[],
        discussion=DiscussionFlow(
            flow_id="d1", steps=[], opening_move="Let's talk.", closing_move="Well done."
        ),
        mini_practice=MiniPractice(
            task_id="mp1", prompt="Speak.", scaffold="I…", evidence_intent_echo="production"
        ),
        reflection=ReflectionSection(prompts=["What was hard?"], self_check_cues=[]),
        story_spine=spine,
    )
    scenario = build_speaking_scenario(pkg)
    state, voice = start_rehearsal(package=pkg, scenario=scenario, discussion_summary="Discussed honesty.")
    state.turns = [
        {"role": "assistant", "text": "[Anna] Thank you for finally arriving."},
        {"role": "student", "text": "Anna, I am sorry the flight was delayed."},
        {"role": "assistant", "text": "[Taxi Driver] Where do you want to go?"},
    ]
    state.coaching_notes = ["Nice apology."]
    live = build_live_conversation_context(
        scenario, rehearsal=state, discussion_summary="Discussed honesty."
    )
    check("voice session not hume", voice.get("not_hume") is True)
    check("opening continues scene", "continue exactly where scene practice left off" in live.opening_line.lower() or "where do you want to go" in live.opening_line.lower())
    check("opening not fresh hello", "how are you today" not in live.opening_line.lower())
    alex = merge_live_context_into_alex_dict(
        {"case_title": "", "live_conversation_opening": ""},
        live,
    )
    check("alex overlay ready", alex.get("live_bridge_ready") is True)

    # AST: rehearsal module must not import httpx / openai realtime
    tree = ast.parse(rehearsal_src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    check("rehearsal does not import httpx", "httpx" not in imported)

    print(f"\nResult: {PASS} passed, {FAIL} failed\n", flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
