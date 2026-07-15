"""CLI entry point: backfill persistent Supertonic audio for reachable Listening bank items.

The actual scan/synthesis/idempotency logic lives in
app/services/language_listening_bank_audio_backfill_service.py (kept importable/testable there,
since backend/scripts/ is excluded from the test Docker image). This file is just the
command-line wrapper: argument parsing, opening a session, printing a summary.

Usage (from backend/, or via `docker compose exec backend python scripts/backfill_listening_bank_audio.py`):
    python scripts/backfill_listening_bank_audio.py                # dry-run, all reachable rows
    python scripts/backfill_listening_bank_audio.py --apply        # actually synthesize + persist
    python scripts/backfill_listening_bank_audio.py --apply --force            # regenerate everything
    python scripts/backfill_listening_bank_audio.py --apply --item-id 23      # target one row

Safety:
- Default mode is dry-run. Nothing is written (no synthesis, no DB writes) unless --apply is passed.
- Never runs automatically -- there is no server-startup hook for this script.
- Only ever touches skill="listening", is_active=True, is_verified=True bank rows with a
  resolvable transcript. Rows without one (the known incomplete scaffold rows referencing
  /language-assets/en/lessons/listening/, which have neither a real audio file nor a transcript)
  are reported as "no_transcript" and left completely untouched.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import AsyncSessionLocal
from app.services.language_listening_bank_audio_backfill_service import run_backfill


async def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill persistent Supertonic audio for reachable Listening placement bank items, "
            "writing audio_meta_json so the live exam prefers cached audio over runtime synthesis."
        )
    )
    parser.add_argument("--language-code", default="en")
    parser.add_argument("--apply", action="store_true", help="Write changes. Default is dry-run.")
    parser.add_argument(
        "--force",
        "--regenerate",
        dest="force",
        action="store_true",
        help="Regenerate even if the cached audio already looks valid (metadata + file both present).",
    )
    parser.add_argument(
        "--item-id",
        type=int,
        default=None,
        help="Only process this single bank item ID (must still satisfy skill/is_active/is_verified).",
    )
    args = parser.parse_args()

    async with AsyncSessionLocal() as db:
        summary = await run_backfill(
            db,
            language_code=args.language_code,
            apply=args.apply,
            force=args.force,
            item_id=args.item_id,
        )

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"{mode}: total={len(summary.results)} "
        f"synthesized={len(summary.synthesized)} "
        f"skipped={len(summary.skipped)} "
        f"would_synthesize={len(summary.would_synthesize)} "
        f"failed={len(summary.failed)} "
        f"no_transcript={len(summary.no_transcript)}"
    )
    for r in summary.results:
        detail = f" ({r.reason})" if r.reason else ""
        extra = f" -> {r.public_url}" if r.public_url else ""
        print(f"  [{r.status}] bank_item_id={r.bank_item_id} level={r.level}{detail}{extra}")

    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
