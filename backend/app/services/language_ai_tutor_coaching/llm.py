"""LLM adapter for coaching — Claude optional; template fallback default for safety."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.services.language_ai_tutor_coaching.flags import coaching_llm_enabled
from app.services.language_ai_tutor_coaching.types import CoachingPromptBundle

logger = logging.getLogger(__name__)

PROVIDER_CLAUDE = "claude-coaching"
PROVIDER_TEMPLATE = "template_fallback"


async def generate_coaching_utterance(
    prompt: CoachingPromptBundle,
    *,
    fallback: str,
) -> tuple[str, str, str | None, str | None]:
    """Return (utterance, provider, reflection, motivation)."""
    if not coaching_llm_enabled():
        return fallback, PROVIDER_TEMPLATE, None, None

    try:
        from app.services.claude_service import generate_claude_json, is_claude_configured
    except Exception:  # noqa: BLE001
        return fallback, PROVIDER_TEMPLATE, None, None

    if not is_claude_configured():
        return fallback, PROVIDER_TEMPLATE, None, None

    try:
        raw = await generate_claude_json(
            prompt.user,
            system=prompt.system,
            temperature=0.35,
            max_output_tokens=800,
        )
        data: dict[str, Any]
        if isinstance(raw, dict):
            data = raw
        else:
            text = str(raw or "").strip()
            fence = re.search(r"\{[\s\S]*\}", text)
            data = json.loads(fence.group(0) if fence else text)
        utterance = str(data.get("utterance") or "").strip() or fallback
        reflection = data.get("reflection_question")
        motivation = data.get("motivation_line")
        return (
            utterance,
            PROVIDER_CLAUDE,
            str(reflection).strip() if reflection else None,
            str(motivation).strip() if motivation else None,
        )
    except Exception:  # noqa: BLE001
        logger.exception("coaching_llm_failed")
        return fallback, PROVIDER_TEMPLATE, None, None
