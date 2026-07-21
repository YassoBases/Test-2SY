# Canonical Grammar Lessons Operator Guide

Phase 5.3D introduces blueprint-driven, sectioned offline authoring for canonical grammar lessons. It does not change `/student/grammar/lesson/start`, student UI behavior, progression, mastery, unlocking, completion, chat, voice, or task evaluation.

## Prerequisites

- Use Python 3.11 via `backend/.venv311`.
- Apply migrations before authoring:

```powershell
cd backend
$env:JWT_SECRET="local-migration-only-strong-placeholder"
.\.venv311\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

## Recommended Authoring Flow

Generate a sectioned draft from a fixture, with no provider call:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py generate-sectioned-draft --grammar-id gram_present_simple --cefr-level A2 --locale ar-SY --fixture-json path\to\sectioned_fixture.json
```

The workflow creates or reuses the lesson identity, creates one parent revision, then authors these units in order:

1. `blueprint`
2. `concept`
3. `examples`
4. `rules`
5. `practice`
6. `production`

Each unit attempt is stored independently. The parent revision becomes `reviewable` only after all required units are accepted and the deterministic assembler produces a valid canonical 14-section lesson.

Real-provider sectioned generation is operator-controlled. It requires both `--real-provider` and `--confirm-outbound-claude`:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py generate-sectioned-draft --grammar-id gram_be_present --cefr-level A2 --locale ar-SY --real-provider --confirm-outbound-claude
```

The sectioned adapter enforces a six-call hard limit for one full lesson and applies per-unit output caps:

- `blueprint`: 1500 tokens
- `concept`: 2000 tokens
- `examples`: 2000 tokens
- `rules`: 2400 tokens
- `practice`: 2200 tokens
- `production`: 1400 tokens

Each unit records provider, model, stop reason, input tokens, output tokens, truncation status, parse diagnostics, validation diagnostics, and a private raw artifact reference when raw output exists.

## Unit Inspection

List unit attempts for a revision:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py units --revision-id <uuid>
```

Inspect a unit attempt:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py inspect-unit --attempt-id <uuid>
```

Inspection is student-safe by default. It shows public payload summaries, status, diagnostics, content hash, provider/model metadata, and raw artifact references. It does not show private metadata such as expected answers, hints, feedback reasoning, success criteria, misconceptions, or retry prompts.

Use `--private-diagnostics` only for local operator debugging. It still does not expose private teaching metadata or raw provider output.

Write a student-safe HTML review artifact for a completed revision:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py inspect --revision-id <uuid> --write-html-artifact
```

The HTML artifact is stored under the private grammar canonical authoring artifact directory, outside public/static frontend assets.

## Partial Retry

Retry one failed unit without regenerating accepted units:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py retry-unit --revision-id <uuid> --unit-key practice --fixture-json path\to\sectioned_fixture.json
```

Retrying a unit that already has an accepted attempt requires an explicit supersede:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py retry-unit --revision-id <uuid> --unit-key examples --fixture-json path\to\sectioned_fixture.json --supersede-accepted
```

Superseding records the old accepted unit as `superseded` and allows a new accepted attempt for the same revision and unit key. Audit history is preserved.

## Assembly

Assemble or reassemble a parent revision after all required units are accepted:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py assemble --revision-id <uuid>
```

Assembly is deterministic. It maps accepted unit payloads into the canonical 14-section student content, merges private teaching metadata on the server side, runs cross-section checks, and then runs the existing full canonical lesson validator. Assembly never publishes.

## Whole-Draft Legacy Commands

The Phase 5.3C whole-draft commands remain available for compatibility:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py generate-draft --grammar-id gram_present_simple --cefr-level A2 --locale ar-SY --fixture-json path\to\fixture.json
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py validate --revision-id <uuid>
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py inspect --revision-id <uuid>
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py retry --revision-id <failed-or-stale-generating-uuid>
```

Use sectioned authoring for new canonical lesson production.

## Publish And Archive

Publish only a reviewed `reviewable` revision:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py publish --revision-id <uuid>
```

Archive a non-current revision when it should no longer be considered for review:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py archive --revision-id <uuid>
```

List revisions:

```powershell
backend\.venv311\Scripts\python.exe backend\scripts\grammar_canonical_lessons.py list --grammar-id gram_present_simple --status reviewable
```

## Validation Summary

Unit validators reject invalid content before assembly:

- `blueprint`: identity mismatch, unsupported support targets, duplicate IDs, missing unit plans, raw grammar ID leakage.
- `concept`: missing Arabic-first explanation for A1-A2, generic filler, duplicated rule/example dumps.
- `examples`: fake grammar-name examples, missing target forms, missing Arabic explanations where needed.
- `rules`: missing required forms, missing immediate examples, mistakes without Arabic reasons, missing visual summary.
- `practice`: missing recognition/fill-blank/reorder/correction progression, production mixed into practice, duplicate IDs, private field leakage.
- `production`: generic "write a sentence using grammar name" prompts, premature mastery claims, private field leakage.

Cross-section assembly rejects missing required units, duplicate public IDs, missing blueprint-required forms, missing independent use, and any final canonical validator failure.

## Privacy Rules

- Student-safe inspection and future student projection must never expose `server_teaching_metadata`, expected answers, sample answers, private hints, feedback reasoning, success criteria, misconception labels, retry prompts, validation diagnostics, raw provider output, credentials, or stack traces.
- Raw provider responses are stored only as private local artifacts under `backend/uploads/private/grammar_canonical_authoring` when available.
- The database stores only `raw_artifact_ref`, never raw response content.
- Artifact names use revision/unit attempt IDs, not student names.
- Keep raw artifacts only as long as needed for local operator review and audit.
