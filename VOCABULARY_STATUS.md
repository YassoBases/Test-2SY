# Vocabulary module — session status

Branch: `feature/vocabulary-fixed-bank` (off `main`). Six commits, grouped logically:

1. **Seed-script safeguards + cleanup tool** — DEBUG guard on 4 seed scripts, plus a
   dry-run-by-default utility to find/remove `_test`-suffixed rows that leaked into
   live vocabulary data.
2. **Word bank schema (migrations 0001, 0009–0012)** — AI daily-usage tracking, mastery
   counters, and the fixed per-level word bank itself (1,350 words, 150–300 per CEFR
   level, ascending — renamed in place from the never-populated old catalog table).
3. **Service layer** — daily batch now served from the fixed word bank (zero live LLM
   calls on the request path), Gemini image generation/caching, offline generator
   removed, a real `translation_ar` data bug fixed. Also carries the quiz feature's
   endpoints/schemas (shared request-handler module with the rest of this commit).
4. **Frontend card rebuild** — new shared `VocabularyWordCard.vue` (bigger, more
   spacious, toggleable Arabic reveal), daily batch as a single-card Previous/Next view
   separate from the Review Bank tab, offline generator UI removed, a real Review Bank
   scoping bug fixed (was showing the whole level bank instead of only served words),
   and the reported Hear/Say it audio signature-mismatch bug fixed.
5. **Image pre-generation background job** — predicts words active students will reach
   soon and pre-generates their images ahead of time; verified idempotent and confirmed
   it never falsely marks a word as "served."
6. **Daily vocabulary quiz** — spelling + pronunciation checks over words the student
   has *already* learned (never new ones), next to the existing Daily challenge card.

## What's verified

Everything above was checked against the real dev database and/or a live browser
session this session — not just written and assumed working. Specifics available on
request; the short version: word bank seeded to exact target counts (1,350/1,350
across all 6 levels), daily batch generation confirmed to make zero LLM calls, image
generation/caching confirmed with real Gemini output, the Review Bank scoping fix and
Arabic-toggle fix confirmed via screenshot, the image pre-warm job confirmed idempotent
with no false "served" marking, and the quiz confirmed end-to-end (spelling grading
both correct/incorrect paths, pronunciation wired to the existing STT pipeline,
completion recorded in the activity log).

## Known open items

- **Word-bank Arabic image-prompt quality**: a template revision was applied so newly
  generated images ground themselves in the word's definition + part of speech instead
  of picking an arbitrary concrete object for abstract words. Only spot-checked on a
  handful of words — not re-run across the full 1,350-word bank.
- **Legacy duplicate content-item rows**: pre-word-bank rows (`source: "ai_generated"`
  or unset) can still exist as duplicates of the same (word, level) pair from before
  migration 0012's uniqueness constraint. A one-off cleanup was done for words visible
  in one test student's Review Bank; a full-bank audit found no further occurrences at
  the time, but the DB wasn't swept exhaustively for every level.
- **Quiz spelling masking**: the definition/example masking is a simple whole-word,
  case-insensitive match — an inflected form in the example sentence (e.g. "negotiated"
  when the target is "negotiate") only masks the stem, leaving the suffix visible.
  Cosmetic, not a scoring bug.
- **Image pre-generation job**: not yet wired into an actual cron/scheduler — the
  script exists and is verified working, but nothing currently invokes it on a
  schedule.
- **Pronunciation scoring in the quiz**: only exercised with synthetic/silent audio in
  this session's automated verification (real speech was verified separately, earlier,
  against the same underlying pipeline) — not retested with real speech through the
  quiz UI specifically.
- **`docker-compose.yml`** has unrelated, unverified local changes (Postgres
  healthcheck dependency, image env passthrough, container command changes) sitting in
  the working tree — deliberately left out of this branch since they're not part of
  this session's vocabulary work and weren't tested here.
