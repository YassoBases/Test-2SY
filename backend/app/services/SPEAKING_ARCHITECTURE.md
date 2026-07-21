# Speaking System Architecture (S0 Foundation)

This document defines the **target architecture**, **package boundaries**, **dependency rules**,
**data retention policy**, and **legacy freeze policy** for the Speaking skill. S0 establishes
contracts only — no WhisperX, WavLM, SpeechBrain, OpenSMILE, Praat, LiveKit, or new model calls.

---

## Target runtime flow

Batch uploads and future streaming converge on the same canonical path:

```
Browser mic / file upload / (future LiveKit stream)
  → SpeakingAudioSession
  → Audio Frontend (provider orchestration)
  → SpeakingSpeechEvidence
  → Analysis engines (pronunciation, fluency, prosody, educational analyzer)
  → Speaking Rule Engine
  → SpeakingEvaluationEngineResult
  → Coach (render-only) + Explainability + Progression
  → SpeakingSpeechOutputProvider (Supertonic)
```

**Single source of truth:** `SpeakingEvaluationEngineResult` owns pass/fail/readiness gates.
Educational analyzer and coach add facts and copy only — they never decide promotion or official CEFR.

---

## Package layers

| Layer | Packages |
|-------|----------|
| Session | `language_speaking_audio_session` |
| Providers | `language_speaking_providers` |
| Audio | `language_speaking_audio_frontend` |
| Analysis | `language_speaking_pronunciation`, `_fluency`, `_prosody`, `_educational_analyzer` |
| Evaluation | `language_speaking_evaluator` |
| Curriculum | `language_speaking_curriculum`, `_knowledge_model`, `_diagnostic` |
| Planning | `language_speaking_lesson_planner` |
| Generation | `language_speaking_generation`, `language_speaking_educational_package` (E1 Learning Package) |
| Policy | `language_speaking_interruption` |
| Pedagogy | `language_speaking_coach` |
| Facts | `language_speaking_explainability` |
| Runtime | `language_speaking_evaluation_runtime` |
| Experience | `language_speaking_lesson_experience`, `language_speaking_lesson_runtime` (E2), `language_speaking_discussion` (E3), `language_speaking_discussion_eval` (E4 discussion→S7 adapter), `language_speaking_live_bridge` (M10 prep→GPT rehearsal→EVI context) |
| Journey | `language_speaking_journey` |
| Progression | `language_speaking_progression`, `_learning_stage`, `_transition_gate`, `_promotion_*`, `_official_promotion` |
| Legacy | `language_speaking_legacy_adapter` |

Shared enums and core types live in `language_speaking/` (not a skill engine).

Full ownership registry: `language_speaking/ownership.py`.

---

## Dependency rules

1. **Providers** may be imported only by `language_speaking_audio_frontend`, `language_speaking_providers`, and `language_speaking_legacy_adapter` — never by coach, journey, or API layers.
2. **Educational analyzer** produces JSON facts only; **rule engine** owns PASS/FAIL/READY/COMPLETE.
3. **Progression engines** consume `SpeakingEvaluationEngineResult` only; never raw audio or provider SDKs.
4. **Coach** consumes evaluation + diagnostic priority; never selects the first STT/grammar error.
5. **Official CEFR** (`official_speaking_cefr`) is writable only by `language_speaking_official_promotion` at runtime (+ initial placement bulk write in `language_progression_service`).
6. **Legacy adapter** is the only package that may import remaining flat legacy modules (transcription, pronunciation, reply TTS, coach).
7. **Frontend** is render-only — no readiness formulas, stage math, or pronunciation thresholds.
8. **ElevenLabs is excluded** from Speaking speech output; Supertonic is the target provider.

---

## Provider boundaries (S0 contracts)

| Provider ABC | Legacy impl (frozen) | Future impl (post-S3+) |
|--------------|---------------------|------------------------|
| `SpeechTranscriptionProvider` | OpenAI transcribe + faster-whisper | WhisperX adapter (optional) |
| `SpeechEmbeddingProvider` | None | WavLM/HuBERT adapter |
| `PhonemeAlignmentProvider` | None | SpeechBrain / forced alignment |
| `AcousticFeatureProvider` | None (prosody = LLM guess today) | OpenSMILE / Praat adapter |
| `SpeakingEducationalAnalyzerProvider` | Claude via conversation AI service | Structured JSON contract |
| `SpeakingSpeechOutputProvider` | Supertonic via reply TTS service | Supertonic (default) |

Capability dataclasses declare supported controls (voice, rate, delivery metadata). No fake unsupported prosody knobs.

---

## Retention boundaries

| Data class | What it holds | Retention / access |
|------------|---------------|-------------------|
| **Raw audio** | Original WebM/WAV bytes | Short-lived session storage; delete after evidence extraction unless user/consent policy requires longer. Not passed to progression or journey. |
| **SpeakingSpeechEvidence** | Transcript, word timings, phoneme alignments (when available), pause markers, prosody features, embedding refs | Persisted per turn as derived evidence; canonical input to evaluation. Retained for trend/diagnostic use under speaking JSONB buckets (S2+). |
| **SpeakingEvaluationEngineResult** | Dimension facts, criterion statuses, pass/fail gates | Persisted on turn/session rows; sole input to progression, coach priority, explainability. |
| **Skill mastery** | Per-node mastery, confidence, evidence codes | Namespaced under `promotion_readiness_json["speaking"]` (mirror Writing). Not computed from raw audio directly. |
| **Official CEFR** | `official_speaking_cefr` on `language_progression` | Updated only by official promotion engine after SPA PASS (S18+). |

Progression must never read provider SDK outputs or raw audio — only canonical evaluation and mastery records.

---

## Legacy freeze policy

Flat legacy modules under `app/services/` are **frozen** — no new features, no new imports from new speaking packages except via `language_speaking_legacy_adapter`.

| Legacy module | Canonical target (S7+) |
|---------------|------------------------|
| `language_transcription_service` | `SpeechTranscriptionProvider` |
| `language_pronunciation_service` | Pronunciation analysis engine |
| `language_speaking_coach_service` | Coach (**unwired** — replace with `language_speaking_coach`) |
| `language_reply_tts_service` | `SpeakingSpeechOutputProvider` |
| `speaking_coach_service` | Standalone `/speaking/coach` API (separate from main flow) |

**Removed (Additional Exercises cleanup):** `language_conversation_service`, `language_conversation_ai_service`, `language_conversation_correction`, `language_conversation_scenario_service`, `language_conversation_tts_task`, `language_shadowing_service`, `language_speaking_service`, `language_speaking_feedback_service`, `language_speaking_evolution_service`.

S0 adapter may be a no-op passthrough. Journey runtime uses canonical evaluation paths (discussion / scene practice / Alex / promotion).

---

## Runtime blockers

Additional Exercises conversation blockers (`mastery_settings_attr`, `tts_signature_mismatch`, `dual_level_system`) were **retired with that surface**.

| ID | Location | Issue | Impact |
|----|----------|-------|--------|
| `dead_coach_module` | `language_speaking_coach_service.py` | Rich coach logic never called from main submit flow | Confusion for implementers; wasted prior work |

Also tracked in `language_speaking_legacy_adapter.adapter.KNOWN_RUNTIME_BLOCKERS` (may be empty after AE removal).

---

## S0 scope vs later phases

**S0 (this foundation):** Package skeleton, enums, ownership DAG, provider ABCs, canonical type stubs, legacy adapter interface, official CEFR ownership guard, this document, `verify_speaking_s0_architecture.py`.

**Not in S0:** Model implementations, skill graph data, frontend changes, progression wiring, new API routes, phoneme engines.

**S1 readiness:** Do not start S1 until S0 verification passes, legacy boundary is frozen, and hotfix blockers are fixed or explicitly shimmed.

See the S0 audit plan for the full S0–S21 roadmap.

---

## M0.5 — Educational Case Philosophy (Speaking V3)

**Locked before M1.** This section defines the educational philosophy of Speaking.
It changes the educational artifact, not the E1→E4 / Curriculum / Evaluation architecture.

### Core principle

Speaking lessons are **not** dialogue-first and **not** story-for-entertainment.
Speaking lessons are **Educational Cases**.

The student learns language by understanding, analyzing, discussing, and finally
**living one realistic situation**. Every lesson should feel like
“I experienced one real situation,” not “I memorized English.”

### Educational Case

Claude does **not** generate random stories. Claude generates **one Educational Case**
that is realistic and discussion-ready (family conflict, job interview, travel emergency,
ethical dilemma, workplace disagreement, immigration, medical visit, etc.).

Forbidden: fantasy, fiction-for-entertainment, dialogue scripts as the lesson center.

### Curriculum ownership (unchanged)

The **Curriculum Engine** remains educational owner: CEFR, grammar IDs, vocabulary,
objectives, communication objective, difficulty, and length policy.
Claude never chooses educational content — only authors one case that satisfies
frozen constraints.

### Case structure (authored artifact)

Case title, context, setting, characters + backgrounds, problem, conflict, timeline,
important events, decision point, consequences, open ending, discussion hooks,
continuation hooks. Vocabulary appears naturally (multi-recycle, no dumping).
Grammar is demonstrated in the case, never lectured inside the prose; Teaching explains
what the student already experienced.

### Discussion / Reflection / Alex

- Discussion starts from the case (understanding → reasoning → decision → opinion →
  experience → transfer), not vocabulary quizzes.
- Reflection covers language, communication, decisions, feelings, alternatives, real life.
- **Alex continues the same Educational Case** (same people, place, conflict, timeline) —
  never invents a new world.

### Implementation constraint

E1–E4, Curriculum Engine, Lesson Runtime, Discussion Runtime, Evaluation, Knowledge,
and Promotion remain reusable. Migration moves Dialogue-first → Educational Case-first
only. Phases: **M1** story default + prompts → **M2** StorySpine → **M3** Alex
same-world → **M4** themes/length policy → **M5** cleanup → **M6–M9** complexity /
personalization / progression → **M10** live speaking bridge.

---

## M10 — Live Speaking Bridge

Students must never enter live conversation without Educational Case context.

```
Educational Case → Reading → Teaching → Guided Discussion (GPT)
  → Speaking Preparation (SpeakingScenario)
  → Voice Rehearsal (GPT-4o Voice — NOT Hume)
  → Live Conversation (Hume EVI + LiveConversationContext)
  → Evaluation (one continuous attempt)
```

Ownership (`language_speaking_live_bridge`):

- Builds `SpeakingScenario` from frozen package `story_spine` (same characters/conflict/decision).
- GPT rehearses as case roles (coach only — no grading).
- Exit produces `LiveConversationContext` for Alex (opening beat continues the case).
- Never invents curriculum, CEFR, or a new story world.

Does **not** redesign E1–E4, Curriculum Engine, Educational Package authorship, or Discussion Runtime.

---

## M11 (retired) → M12 — Claude Scene Director + GPT TTS/STT

M11 GPT Realtime / WebRTC Scene Practice was **retired in M12.5**. Scene Practice now uses:

```
Claude Discussion
  → SpeakingScenario / Mission Brief (M10)
  → Scene Practice (Claude Scene Director owns every turn)
  → Student audio → STT (GPT) → Claude → persist → TTS (GPT) → audio
  → LiveConversationContext (server-owned transcript)
  → Alex Hume EVI continues same case
  → Evaluation (unchanged)
```

Claude owns dialogue, corrections, scene beats. GPT-4o is **only** STT + TTS.

API (same `/live-bridge` prefix):

- `POST /rehearsal/respond` — voice turn (STT → Claude → persist → TTS)
- `POST /rehearsal/turn` — typed accessibility fallback (same Claude director)
- Removed: `/rehearsal/realtime-session`, `/rehearsal/sync`

Verifiers: `verify_speaking_m12_*.py`; `verify_speaking_m11_realtime_scene_practice.py` is now an anti-regression that proves Realtime is gone.
