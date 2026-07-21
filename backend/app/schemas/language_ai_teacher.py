"""Student Autonomous AI Teacher API schemas (Phase F)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AiTeacherStatusOut(BaseModel):
    enabled: bool


class AiTeacherSessionOut(BaseModel):
    enabled: bool = True
    session: dict = Field(default_factory=dict)
