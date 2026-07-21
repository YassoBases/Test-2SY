"""LLM adapter for AI Tutor — Claude with template fallback; never educational writes."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.services.language_ai_tutor.flags import ai_tutor_llm_enabled
from app.services.language_ai_tutor.prompts import template_fallback_utterance
from app.services.language_ai_tutor.types import TutorContext, TutorPromptBundle

logger = logging.getLogger(__name__)

PROVIDER_CLAUDE = "claude-ai-tutor"
PROVIDER_TEMPLATE = "template_fallback"


def _extract_utterance(payload: dict[str, Any] | None, *, fallback: str) -> str:
    if not isinstance(payload, dict):
        return fallback
    text = payload.get("utterance") or payload.get("assistant_utterance") or ""
    text = str(text).strip()
    return text or fallback


async def generate_tutor_utterance(
    ctx: TutorContext,
    prompt: TutorPromptBundle,
    *,
    student_message: str = "",
) -> tuple[str, str]:
    """Return (utterance, provider). Never writes educational state."""
    fallback = template_fallback_utterance(
        ctx, prompt_kind=prompt.prompt_kind, student_message=student_message
    )
    if not ai_tutor_llm_enabled():
        return fallback, PROVIDER_TEMPLATE

    try:
        from app.services.claude_service import generate_claude_json, is_claude_configured
    except Exception:  # noqa: BLE001
        return fallback, PROVIDER_TEMPLATE

    if not is_claude_configured():
        return fallback, PROVIDER_TEMPLATE

    try:
        raw = await generate_claude_json(
            prompt.user,
            system=prompt.system,
            temperature=0.3,
            max_output_tokens=700,
        )
        data: dict[str, Any] | None
        if isinstance(raw, dict):
            data = raw
        else:
            text = str(raw or "").strip()
            # Tolerate fenced JSON
            fence = re.search(r"\{[\s\S]*\}", text)
            data = json.loads(fence.group(0) if fence else text)
        utterance = _extract_utterance(data, fallback=fallback)
        return utterance, PROVIDER_CLAUDE
    except Exception:  # noqa: BLE001
        logger.exception("ai_tutor_llm_failed")
        return fallback, PROVIDER_TEMPLATE
