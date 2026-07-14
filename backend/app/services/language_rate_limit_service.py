"""Phase 12 — per-user rate limiting for expensive AI calls.

In-memory sliding-window limiter (single-process; swap the store for Redis at multi-instance scale).
Keeps a learner from hammering the costly AI endpoints. Fails OPEN on any internal error — a limiter
bug must never block legitimate learning.
"""

from __future__ import annotations

import time

from fastapi import HTTPException, status

# category -> (max_calls, window_seconds)
RATE_LIMITS: dict[str, tuple[int, float]] = {
    "gemini": (60, 60.0),     # general AI calls
    "speaking": (20, 60.0),   # audio turns (heavier)
    "lesson_gen": (10, 60.0), # on-demand content generation
}

# key -> list[timestamps]
_hits: dict[str, list[float]] = {}


def within_limit(timestamps: list[float], *, limit: int, window: float, now: float) -> tuple[bool, list[float]]:
    """Pure check: keep only timestamps inside the window; allow when below the limit.

    Returns (allowed, pruned_timestamps_including_now_if_allowed)."""
    cutoff = now - window
    recent = [t for t in timestamps if t >= cutoff]
    if len(recent) >= limit:
        return False, recent
    recent.append(now)
    return True, recent


def check(category: str, identifier) -> bool:
    """Stateful: record a hit for (category, identifier) and return whether it is allowed."""
    try:
        limit, window = RATE_LIMITS.get(category, (60, 60.0))
        key = f"{category}:{identifier}"
        allowed, recent = within_limit(_hits.get(key, []), limit=limit, window=window, now=time.time())
        _hits[key] = recent
        return allowed
    except Exception:  # fail open — never block learning on a limiter bug
        return True


def check_or_raise(category: str, identifier) -> None:
    """Raise HTTP 429 when the per-user limit for this category is exceeded."""
    if not check(category, identifier):
        limit, window = RATE_LIMITS.get(category, (60, 60.0))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You're going a bit fast — please wait a moment (limit {limit} per {int(window)}s).",
        )
