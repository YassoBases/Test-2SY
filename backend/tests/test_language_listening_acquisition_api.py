from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks

from app.api import language_student
from app.schemas.language_listening_acquisition import (
    ListeningAcquisitionStatusOut,
    ListeningNextResponseOut,
)
from app.schemas.language_listening_bundles import LessonExperienceBundleOut


class _Db:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


def _bundle() -> LessonExperienceBundleOut:
    return LessonExperienceBundleOut(
        lesson_id=3175,
        lifecycle_state="started",
        official_level="B1",
        lesson_level="B1",
        lesson_title="Owned Listening Lesson",
        lesson_goal={"id": "grammar", "label": "Practice the current grammar in listening."},
    )


@pytest.mark.asyncio
async def test_listening_next_commits_ready_bundle(monkeypatch) -> None:
    async def fake_acquire(db, *, student_id: int, attempt: int):
        return ListeningNextResponseOut(outcome="lesson_ready", bundle=_bundle()), False

    monkeypatch.setattr(language_student, "acquire_next_listening", fake_acquire)
    db = _Db()

    response = await language_student.listening_next(
        BackgroundTasks(),
        student=SimpleNamespace(id=109),
        db=db,
        _deployment=None,
        attempt=1,
    )

    assert response.outcome == "lesson_ready"
    assert db.commits == 1


@pytest.mark.asyncio
async def test_listening_acquisition_commits_pending_state_and_schedules_prefill(monkeypatch) -> None:
    async def fake_acquire(db, *, student_id: int, attempt: int):
        acquisition = ListeningAcquisitionStatusOut(
            status="generating",
            waiting=True,
            generation_in_progress=True,
            message_key="student.languages.listeningJourney.acquisition.preparing",
        )
        return ListeningNextResponseOut(outcome="acquisition_pending", acquisition=acquisition), True

    async def fake_prefill(*, student_id: int) -> None:
        return None

    monkeypatch.setattr(language_student, "acquire_next_listening", fake_acquire)
    monkeypatch.setattr(language_student, "background_prefill_listening_pool", fake_prefill)
    db = _Db()
    tasks = BackgroundTasks()

    response = await language_student.listening_acquisition_status(
        tasks,
        student=SimpleNamespace(id=109),
        db=db,
        _deployment=None,
        attempt=2,
    )

    assert response.outcome == "acquisition_pending"
    assert db.commits == 1
    assert len(tasks.tasks) == 1
