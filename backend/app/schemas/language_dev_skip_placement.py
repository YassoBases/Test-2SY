"""Developer-only skip-placement request/response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

StartingCefr = Literal["A1", "A2", "B1", "B2", "C1"]


class DevSkipPlacementIn(BaseModel):
    starting_cefr: StartingCefr = "A1"
    bootstrap_learning: bool = Field(
        default=False,
        description=(
            "When true, also run Start Learning (Claude package) inline. "
            "Default false — DX skip stays fast; package is created on the Speaking page."
        ),
    )


class DevSkipPlacementOut(BaseModel):
    ok: bool = True
    placement_completed: bool = True
    starting_cefr: StartingCefr
    official_levels: dict[str, str]
    learning_path_id: int | None = None
    curriculum_entry_node_id: str | None = None
    primary_target_skill_id: str | None = None
    knowledge_model_initialized: bool = True
    daily_plan_ready: bool = False
    learning_bootstrapped: bool = False
    package_id: str | None = None
    lesson_opened: bool = False
    bootstrap_warning: str | None = None
    redirect: str = "/student/languages/speaking"
