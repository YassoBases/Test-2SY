"""M12.2 — Scene Practice OpenAI TTS verifier.

Proves voice.py is a stateless, never-load-bearing Text-To-Speech pass-through:
- pure function text -> (audio bytes, mime) | None
- no reasoning, no dialogue ownership, no scene logic, no Claude
- every failure path returns None (a turn can never fail because of TTS)

Usage:
  python -u scripts/verify_speaking_m12_voice_tts.py
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import sys
from pathlib import Path
from unittest.mock import patch

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


class _FakeResponse:
    def __init__(self, content: bytes, status: int = 200) -> None:
        self.content = content
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")


class _FakeClient:
    def __init__(self, response: _FakeResponse | Exception, calls: list) -> None:
        self._response = response
        self._calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False

    async def post(self, url, **kwargs):
        self._calls.append({"url": url, **kwargs})
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def main() -> int:
    print("\n=== M12.2 Speaking OpenAI TTS (shared runtime) ===\n", flush=True)

    import app.services.language_speaking_audio_frontend.tts_runtime as voice_mod
    from app.core.config import get_settings
    from app.services.language_speaking_audio_frontend.tts_runtime import (
        TTS_AUDIO_FORMAT,
        TTS_AUDIO_MIME,
        synthesize_spoken_line,
    )
    from app.services.language_speaking_live_bridge.voice import synthesize_scene_line

    settings = get_settings()
    src = inspect.getsource(voice_mod)
    # Legacy alias must remain for dormant Scene Practice paths.
    check("legacy synthesize_scene_line aliases shared TTS", synthesize_scene_line is synthesize_spoken_line)

    # --- 1. Ownership purity: TTS only, no reasoning, no scene logic ---
    # Inspect real imports, not prose in docstrings.
    imported_modules: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.update(a.name for a in node.names)
    check(
        "no claude imports/calls",
        not any("claude" in m.lower() for m in imported_modules)
        and "generate_claude" not in src,
    )
    check("no chat completions", "chat/completions" not in src)
    check("no realtime endpoint", "/v1/realtime" not in src)
    check("uses audio/speech endpoint", "/v1/audio/speech" in src)
    check(
        "no scene imports",
        not any(
            part in m
            for m in imported_modules
            for part in ("scene_director", "rehearsal", "live_bridge.engine")
        ),
    )
    check(
        "no prompt/instruction building",
        '"instructions"' not in src and '"messages"' not in src and '"system"' not in src,
    )

    # --- 2. Statelessness: no module-level mutable state, no storage ---
    tree = ast.parse(src)
    mutable_globals = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, (ast.Dict, ast.List, ast.Set, ast.Call)) and not (
                isinstance(value, ast.Call)
                and getattr(value.func, "attr", getattr(value.func, "id", ""))
                in ("getLogger", "get_settings")
            ):
                mutable_globals.append(ast.dump(node)[:60])
    check("no module-level mutable state", not mutable_globals, str(mutable_globals))
    check("no file writes", "open(" not in src and "write_bytes" not in src)
    check("no caching", "cache" not in src.lower() and "lru" not in src.lower())
    check("mime is mpeg for mp3", TTS_AUDIO_FORMAT == "mp3" and TTS_AUDIO_MIME == "audio/mpeg")

    # --- 3. Config present ---
    check("config SPEAKING_TTS_MODEL", getattr(settings, "SPEAKING_TTS_MODEL", "") != "")
    check("config SPEAKING_TTS_VOICE", getattr(settings, "SPEAKING_TTS_VOICE", "") != "")
    check(
        "config SPEAKING_TTS_TIMEOUT_SECONDS",
        int(getattr(settings, "SPEAKING_TTS_TIMEOUT_SECONDS", 0)) > 0,
    )

    # --- 4. Never-fail contract ---
    calls: list = []

    check("empty text -> None", asyncio.run(synthesize_spoken_line("")) is None)
    check("whitespace text -> None", asyncio.run(synthesize_spoken_line("   ")) is None)

    # OpenAI contract tests disable Supertonic so the HTTP pass-through is isolated.
    async def _no_supertonic(_text: str):
        return None

    orig_key = settings.OPENAI_API_KEY
    settings.OPENAI_API_KEY = ""
    try:
        with patch.object(voice_mod, "_synthesize_supertonic_line", _no_supertonic):
            check("no api key -> None", asyncio.run(synthesize_spoken_line("Hi there.")) is None)
            check("no api key -> no network call", len(calls) == 0)
    finally:
        settings.OPENAI_API_KEY = orig_key

    settings.OPENAI_API_KEY = settings.OPENAI_API_KEY or "sk-test-not-real"
    try:
        with patch.object(voice_mod, "_synthesize_supertonic_line", _no_supertonic):
            # Success path
            calls.clear()
            with patch.object(
                voice_mod.httpx,
                "AsyncClient",
                lambda **_k: _FakeClient(_FakeResponse(b"ID3fakeaudio"), calls),
            ):
                result = asyncio.run(synthesize_spoken_line("We're still at the cafe. What now?"))
            check("success returns bytes+mime", result == (b"ID3fakeaudio", "audio/mpeg"))
            check("one stateless call", len(calls) == 1)
            body = calls[0]["json"]
            check("payload is text passthrough", body["input"] == "We're still at the cafe. What now?")
            check("payload model from config", body["model"] == settings.SPEAKING_TTS_MODEL)
            check("payload voice from config", body["voice"] == settings.SPEAKING_TTS_VOICE)
            check("payload format mp3", body["response_format"] == "mp3")
            check(
                "payload has no reasoning fields",
                all(k not in body for k in ("messages", "instructions", "temperature", "tools")),
            )

            # Long line truncated, never rejected
            calls.clear()
            with patch.object(
                voice_mod.httpx,
                "AsyncClient",
                lambda **_k: _FakeClient(_FakeResponse(b"ID3fakeaudio"), calls),
            ):
                result = asyncio.run(synthesize_spoken_line("y" * 5000))
            check("long line truncated", result is not None and len(calls[0]["json"]["input"]) <= 1000)

            # HTTP error -> None (turn continues in text mode)
            with patch.object(
                voice_mod.httpx,
                "AsyncClient",
                lambda **_k: _FakeClient(_FakeResponse(b"", status=500), []),
            ):
                check("http 500 -> None", asyncio.run(synthesize_spoken_line("Hello scene.")) is None)

            # Network exception -> None
            with patch.object(
                voice_mod.httpx,
                "AsyncClient",
                lambda **_k: _FakeClient(RuntimeError("boom"), []),
            ):
                check("network error -> None", asyncio.run(synthesize_spoken_line("Hello scene.")) is None)

            # Empty audio body -> None
            with patch.object(
                voice_mod.httpx,
                "AsyncClient",
                lambda **_k: _FakeClient(_FakeResponse(b""), []),
            ):
                check("empty audio -> None", asyncio.run(synthesize_spoken_line("Hello scene.")) is None)
    finally:
        settings.OPENAI_API_KEY = orig_key

    # --- 5. Nothing else changed: Scene Director untouched by M12.2 ---
    director_src = (
        BACKEND / "app/services/language_speaking_live_bridge/scene_director.py"
    ).read_text(encoding="utf-8")
    check(
        "scene director has no tts",
        "audio/speech" not in director_src and "synthesize_scene_line" not in director_src,
    )
    rehearsal_src = (
        BACKEND / "app/services/language_speaking_live_bridge/rehearsal.py"
    ).read_text(encoding="utf-8")
    check(
        "rehearsal module stays dialogue-only (TTS via engine)",
        "from app.services.language_speaking_live_bridge.voice" not in rehearsal_src,
    )

    print(f"\nResult: {PASS} passed, {FAIL} failed\n", flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
