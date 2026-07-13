"""Real PostgreSQL concurrency coverage for the placement exam state protocol.

These tests deliberately use independent ``AsyncSession`` instances.  Mocks are limited to
external audio/STT/AI work; row locking, JSONB writes, and endpoint state validation all execute
against the dedicated PostgreSQL test database.
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm.attributes import flag_modified

from app.api import language_exam
from app.models.language.analytics import LanguageAnalytics
from app.models.language.catalog import Language
from app.models.language.exam import LanguageExamSession
from app.models.language.profile import LanguageStudentProfile
from app.models.user import User, UserRole
from app.schemas.language_exam import (
    CEFRLevel,
    ExamNarrativeSchema,
    McqAnswerIn,
    SpeakingGradeSchema,
    SpeakingTurnAssessment,
    WritingGradeSchema,
)
from app.services import language_exam_service
from app.services.language_audio_security_service import ValidatedAudio
from app.services.language_exam_service import ExamAIError
from app.services.language_transcription_service import ConversationTranscription


pytestmark = [pytest.mark.postgresql, pytest.mark.concurrency]


@pytest_asyncio.fixture
async def exam_record_factory(postgres_session_factory):
    """Create isolated ORM rows and remove every committed row after each test."""

    tracked_sessions: list[str] = []
    tracked_users: list[int] = []
    tracked_languages: list[int] = []

    async def create(*, state: dict, status: str = "in_progress") -> SimpleNamespace:
        marker = uuid.uuid4().hex
        async with postgres_session_factory() as db:
            student = User(
                email=f"placement-concurrency-{marker}@example.test",
                name="Placement concurrency student",
                hashed_password="not-used-in-tests",
                role=UserRole.student,
            )
            language = Language(
                code=f"t{marker[:12]}",
                name_en=f"Test language {marker[:8]}",
                name_ar=f"Test language {marker[:8]}",
                is_active=True,
            )
            db.add_all([student, language])
            await db.flush()

            exam = LanguageExamSession(
                id=uuid.uuid4().hex,
                student_id=student.id,
                language_id=language.id,
                current_step=1,
                max_steps=max(1, len(state.get("sections") or [])),
                exam_state=copy.deepcopy(state),
                status=status,
                is_completed=False,
            )
            db.add(exam)
            await db.commit()

            tracked_sessions.append(exam.id)
            tracked_users.append(student.id)
            tracked_languages.append(language.id)
            return SimpleNamespace(
                session_id=exam.id,
                student_id=student.id,
                language_id=language.id,
                student=SimpleNamespace(id=student.id),
            )

    yield create

    async with postgres_session_factory() as db:
        if tracked_users and tracked_languages:
            await db.execute(
                delete(LanguageAnalytics).where(
                    LanguageAnalytics.student_id.in_(tracked_users),
                    LanguageAnalytics.language_id.in_(tracked_languages),
                )
            )
            await db.execute(
                delete(LanguageStudentProfile).where(
                    LanguageStudentProfile.student_id.in_(tracked_users),
                    LanguageStudentProfile.language_id.in_(tracked_languages),
                )
            )
        if tracked_users:
            # Concurrent initiate creates an additional session after the factory returns, so
            # clean by owned student as well as by the factory's initially tracked ids.
            await db.execute(
                delete(LanguageExamSession).where(
                    LanguageExamSession.student_id.in_(tracked_users)
                )
            )
        elif tracked_sessions:
            await db.execute(
                delete(LanguageExamSession).where(LanguageExamSession.id.in_(tracked_sessions))
            )
        if tracked_users:
            await db.execute(delete(User).where(User.id.in_(tracked_users)))
        if tracked_languages:
            await db.execute(delete(Language).where(Language.id.in_(tracked_languages)))
        await db.commit()


def _preparing_state(*, revision: int = 3, prep_token: str = "prep-token-0000000000000001") -> dict:
    return {
        "version": 3,
        "state_revision": revision,
        "sections": ["speaking", "listening", "reading", "grammar_vocab", "writing"],
        "cursor": 0,
        "content_prep_token": prep_token,
        "content_prep_status": "preparing",
        "speaking": {
            "turn": 1,
            "total_turns": 3,
            "pending_question": "Tell me about your day.",
            "turn_token": "speaking-token-00000000000001",
            "results": [],
            "done": False,
            "evidence_status": "missing_student_response",
        },
        "listening": {"ready": False, "done": False, "asked": [], "pool": {}},
        "reading": {"ready": False, "done": False, "asked": [], "pool": {}},
        "grammar_vocab": {"ready": False, "done": False, "asked": [], "pool": {}},
        "writing": {"ready": False, "done": False, "response": None},
        "request_receipts": [],
    }


async def _stored_exam(postgres_session_factory, session_id: str) -> LanguageExamSession:
    async with postgres_session_factory() as db:
        return (
            await db.execute(
                select(LanguageExamSession).where(LanguageExamSession.id == session_id)
            )
        ).scalar_one()


async def _wait_until_blocked(task: asyncio.Task, *, delay: float = 0.08) -> None:
    """Give PostgreSQL enough time to place the second actor behind the held row lock."""

    await asyncio.sleep(delay)
    assert not task.done(), "the second transaction unexpectedly bypassed the row lock"


def _install_fast_content_preparation(monkeypatch) -> None:
    """Replace content sources, not the PostgreSQL state/merge path, with deterministic data."""

    async def question_pool(_db, *, skill, **_kwargs):
        item = {
            "level": "A2",
            "question": f"Prepared {skill} question?",
            "options": ["one", "two"],
            "correct_index": 0,
        }
        if skill == "reading":
            item["passage"] = "A prepared reading passage."
        if skill == "listening":
            item["audio_url"] = "/language-assets/en/placement/listening/test.wav"
        return {"A2": item}

    async def empty_pool(*_args, **_kwargs):
        return {}

    async def writing_prompt(*_args, **_kwargs):
        return "Write about a memorable day."

    async def no_generated_content(**_kwargs):
        return {"items": []}

    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(language_exam, "_question_bank_pool", question_pool)
    monkeypatch.setattr(language_exam, "_seeded_pool", empty_pool)
    monkeypatch.setattr(language_exam, "_generated_pool", empty_pool)
    monkeypatch.setattr(language_exam, "_writing_prompt", writing_prompt)
    monkeypatch.setattr(
        language_exam.ai_engine,
        "generate_comprehension_set",
        no_generated_content,
    )


async def test_prepare_content_preserves_concurrent_speaking_evidence(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    state = _preparing_state()
    record = await exam_record_factory(state=state)
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))
    _install_fast_content_preparation(monkeypatch)

    speaker_locked = asyncio.Event()
    release_speaker = asyncio.Event()
    evidence_bytes = b"server-verified-speaking-evidence"
    evidence_hash = hashlib.sha256(evidence_bytes).hexdigest()

    async def fake_read(_file) -> ValidatedAudio:
        return ValidatedAudio(
            data=evidence_bytes,
            mime_type="audio/webm",
            suffix=".webm",
            sha256=evidence_hash,
            duration_seconds=4.0,
        )

    async def fake_transcribe(_audio: ValidatedAudio) -> ConversationTranscription:
        return ConversationTranscription(
            text="I studied and then played football with my friends",
            engine="test-stt",
            model="test-model",
        )

    async def fake_assess(**kwargs) -> SpeakingTurnAssessment:
        return SpeakingTurnAssessment(
            transcription=kwargs["transcript"],
            grammar_vocab_feedback="No material issue.",
            pronunciation_feedback="",
            fluency_note="Coherent response.",
            estimated_level=CEFRLevel.A2,
            next_question="What did you enjoy most?",
        )

    original_load_session = language_exam._load_session

    async def pause_after_speaking_lock(db, session_id, student, *, for_update=False):
        exam = await original_load_session(
            db,
            session_id,
            student,
            for_update=for_update,
        )
        if for_update:
            speaker_locked.set()
            await asyncio.wait_for(release_speaker.wait(), timeout=5)
        return exam

    monkeypatch.setattr(language_exam, "_read_speaking_audio", fake_read)
    monkeypatch.setattr(language_exam, "_verified_server_transcription", fake_transcribe)
    monkeypatch.setattr(language_exam.ai_engine, "assess_speaking", fake_assess)
    monkeypatch.setattr(language_exam, "_load_session", pause_after_speaking_lock)

    async def submit_speaking() -> None:
        async with postgres_session_factory() as db:
            await language_exam.speaking_turn(
                record.session_id,
                BackgroundTasks(),
                file=SimpleNamespace(filename="verified.webm"),
                duration_seconds=None,
                request_id="speaking-request-0001",
                state_revision=state["state_revision"],
                turn_token=state["speaking"]["turn_token"],
                student=record.student,
                db=db,
            )

    speaker_task = asyncio.create_task(submit_speaking())
    await asyncio.wait_for(speaker_locked.wait(), timeout=5)
    prepare_task = asyncio.create_task(
        language_exam._prepare_content(record.session_id, record.language_id, "A2")
    )
    await _wait_until_blocked(prepare_task)
    release_speaker.set()
    await asyncio.wait_for(asyncio.gather(speaker_task, prepare_task), timeout=10)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    latest = stored.exam_state
    assert latest["speaking"]["results"][0]["audio_sha256"] == evidence_hash
    assert latest["speaking"]["turn"] == 2
    assert latest["speaking"]["turn_token"] != state["speaking"]["turn_token"]
    assert latest["request_receipts"][0]["request_id"] == "speaking-request-0001"
    assert all(latest[section]["ready"] is True for section in language_exam.PREPARED_SECTIONS)
    assert latest["state_revision"] == state["state_revision"] + 2


async def test_prepare_content_cannot_revive_an_abandoned_exam(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    state = _preparing_state(revision=10)
    record = await exam_record_factory(state=state)
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    _install_fast_content_preparation(monkeypatch)

    abandon_locked = asyncio.Event()
    release_abandon = asyncio.Event()

    async def abandon_under_lock() -> None:
        async with postgres_session_factory() as db:
            exam = (
                await db.execute(
                    select(LanguageExamSession)
                    .where(LanguageExamSession.id == record.session_id)
                    .with_for_update()
                )
            ).scalar_one()
            abandoned = copy.deepcopy(exam.exam_state or {})
            abandoned["abandoned_at"] = datetime.now(timezone.utc).isoformat()
            language_exam._bump_state_revision(abandoned)
            exam.exam_state = abandoned
            exam.status = "abandoned"
            flag_modified(exam, "exam_state")
            abandon_locked.set()
            await asyncio.wait_for(release_abandon.wait(), timeout=5)
            await db.commit()

    abandon_task = asyncio.create_task(abandon_under_lock())
    await asyncio.wait_for(abandon_locked.wait(), timeout=5)
    prepare_task = asyncio.create_task(
        language_exam._prepare_content(record.session_id, record.language_id, "A2")
    )
    await _wait_until_blocked(prepare_task)
    release_abandon.set()
    await asyncio.wait_for(asyncio.gather(abandon_task, prepare_task), timeout=10)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    latest = stored.exam_state
    assert stored.status == "abandoned"
    assert latest["abandoned_at"]
    assert latest["state_revision"] == state["state_revision"] + 1
    assert all(latest[section]["ready"] is False for section in language_exam.PREPARED_SECTIONS)


def _mcq_state() -> dict:
    return {
        "version": 3,
        "state_revision": 7,
        "sections": ["reading"],
        "cursor": 0,
        "reading": {
            "mode": "adaptive",
            "pool": {
                "A2": {
                    "passage": "A short passage.",
                    "question": "Which answer is correct?",
                    "options": ["correct", "wrong"],
                    "correct_index": 0,
                    "question_token": "mcq-question-token-0000000001",
                },
                "B1": {
                    "passage": "The next passage.",
                    "question": "This must remain unanswered.",
                    "options": ["next correct", "next wrong"],
                    "correct_index": 0,
                    "question_token": "mcq-question-token-0000000002",
                },
            },
            "current_level": "A2",
            "asked": [],
            "max_steps": 2,
            "ready": True,
            "done": False,
            "evidence_status": "missing_student_response",
        },
        "request_receipts": [],
    }


async def test_two_concurrent_mcq_answers_only_apply_one_revision_and_token(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    state = _mcq_state()
    record = await exam_record_factory(state=state)
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)

    async def submit(request_id: str):
        async with postgres_session_factory() as db:
            try:
                response = await language_exam.answer_mcq(
                    record.session_id,
                    McqAnswerIn(
                        choice_index=0,
                        request_id=request_id,
                        state_revision=state["state_revision"],
                        question_token=state["reading"]["pool"]["A2"]["question_token"],
                    ),
                    student=record.student,
                    db=db,
                )
                return "ok", response
            except HTTPException as exc:
                await db.rollback()
                return "error", exc

    outcomes = await asyncio.wait_for(
        asyncio.gather(
            submit("concurrent-mcq-request-0001"),
            submit("concurrent-mcq-request-0002"),
        ),
        timeout=10,
    )

    successes = [value for kind, value in outcomes if kind == "ok"]
    failures = [value for kind, value in outcomes if kind == "error"]
    assert len(successes) == 1
    assert len(failures) == 1
    assert failures[0].status_code == 409
    assert failures[0].detail["code"] == "stale_exam_state"
    assert failures[0].detail["current_state_revision"] == state["state_revision"] + 1

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    latest = stored.exam_state
    assert latest["state_revision"] == state["state_revision"] + 1
    assert latest["reading"]["asked"] == [
        {"level": "A2", "correct": True, "chosen_index": 0}
    ]
    assert latest["reading"]["current_level"] == "B1"
    assert len(latest["request_receipts"]) == 1


def _speaking_state() -> dict:
    return {
        "version": 3,
        "state_revision": 13,
        "sections": ["speaking"],
        "cursor": 0,
        "learner_grade": None,
        "speaking": {
            "scenario": {
                "scenario": "At a community event",
                "ai_persona": "Host",
                "student_role": "Guest",
                "setting": "Community hall",
            },
            "turn": 1,
            "total_turns": 2,
            "pending_question": "What brought you to this event?",
            "turn_token": "speaking-current-token-00000001",
            "results": [],
            "done": False,
            "evidence_status": "missing_student_response",
        },
        "request_receipts": [],
    }


async def test_two_concurrent_audio_files_cannot_fill_two_speaking_turns(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    state = _speaking_state()
    record = await exam_record_factory(state=state)
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))

    async def fake_read(file) -> ValidatedAudio:
        content = str(file.filename).encode("utf-8")
        return ValidatedAudio(
            data=content,
            mime_type="audio/webm",
            suffix=".webm",
            sha256=hashlib.sha256(content).hexdigest(),
            duration_seconds=3.0,
        )

    async def fake_transcribe(audio: ValidatedAudio) -> ConversationTranscription:
        return ConversationTranscription(
            text=f"I came to meet neighbours and help with the event {audio.sha256[:4]}",
            engine="test-stt",
            model="test-model",
        )

    assess_arrivals = 0
    assess_lock = asyncio.Lock()
    both_assessing = asyncio.Event()

    async def fake_assess(**kwargs) -> SpeakingTurnAssessment:
        nonlocal assess_arrivals
        async with assess_lock:
            assess_arrivals += 1
            if assess_arrivals == 2:
                both_assessing.set()
        await asyncio.wait_for(both_assessing.wait(), timeout=5)
        return SpeakingTurnAssessment(
            transcription=kwargs["transcript"],
            grammar_vocab_feedback="No material issue.",
            pronunciation_feedback="",
            fluency_note="Coherent response.",
            estimated_level=CEFRLevel.A2,
            next_question="What activity would you like to join next?",
        )

    monkeypatch.setattr(language_exam, "_read_speaking_audio", fake_read)
    monkeypatch.setattr(language_exam, "_verified_server_transcription", fake_transcribe)
    monkeypatch.setattr(language_exam.ai_engine, "assess_speaking", fake_assess)

    async def submit(filename: str, request_id: str):
        async with postgres_session_factory() as db:
            try:
                response = await language_exam.speaking_turn(
                    record.session_id,
                    BackgroundTasks(),
                    file=SimpleNamespace(filename=filename),
                    duration_seconds=None,
                    request_id=request_id,
                    state_revision=state["state_revision"],
                    turn_token=state["speaking"]["turn_token"],
                    student=record.student,
                    db=db,
                )
                return "ok", response
            except HTTPException as exc:
                await db.rollback()
                return "error", exc

    outcomes = await asyncio.wait_for(
        asyncio.gather(
            submit("first.webm", "concurrent-speaking-request-1"),
            submit("second.webm", "concurrent-speaking-request-2"),
        ),
        timeout=10,
    )

    successes = [value for kind, value in outcomes if kind == "ok"]
    failures = [value for kind, value in outcomes if kind == "error"]
    assert len(successes) == 1
    assert len(failures) == 1
    assert failures[0].status_code == 409
    assert failures[0].detail["code"] == "stale_exam_state"

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    latest = stored.exam_state
    assert latest["state_revision"] == state["state_revision"] + 1
    assert latest["speaking"]["turn"] == 2
    assert len(latest["speaking"]["results"]) == 1
    assert len(latest["request_receipts"]) == 1


async def test_speaking_stt_wait_does_not_hold_the_exam_row_lock(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """The slow STT phase must run after releasing every transaction and row lock."""

    state = _speaking_state()
    record = await exam_record_factory(state=state)
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))

    audio = ValidatedAudio(
        data=b"single-server-audio",
        mime_type="audio/webm",
        suffix=".webm",
        sha256=hashlib.sha256(b"single-server-audio").hexdigest(),
        duration_seconds=3.0,
    )
    stt_started = asyncio.Event()
    release_stt = asyncio.Event()

    async def fake_read(_file) -> ValidatedAudio:
        return audio

    async def waiting_stt(_audio: ValidatedAudio) -> ConversationTranscription:
        stt_started.set()
        await asyncio.wait_for(release_stt.wait(), timeout=5)
        return ConversationTranscription(
            text="I came to meet my neighbours and help organize this event",
            engine="test-stt",
            model="test-model",
        )

    async def fake_assess(**kwargs) -> SpeakingTurnAssessment:
        return SpeakingTurnAssessment(
            transcription=kwargs["transcript"],
            grammar_vocab_feedback="No material issue.",
            pronunciation_feedback="",
            fluency_note="Coherent response.",
            estimated_level=CEFRLevel.A2,
            next_question="What would you organize next?",
        )

    monkeypatch.setattr(language_exam, "_read_speaking_audio", fake_read)
    monkeypatch.setattr(language_exam, "_verified_server_transcription", waiting_stt)
    monkeypatch.setattr(language_exam.ai_engine, "assess_speaking", fake_assess)

    async def submit():
        async with postgres_session_factory() as db:
            return await language_exam.speaking_turn(
                record.session_id,
                BackgroundTasks(),
                file=SimpleNamespace(filename="single.webm"),
                duration_seconds=None,
                request_id="single-speaking-request-0001",
                state_revision=state["state_revision"],
                turn_token=state["speaking"]["turn_token"],
                student=record.student,
                db=db,
            )

    submit_task = asyncio.create_task(submit())
    await asyncio.wait_for(stt_started.wait(), timeout=5)

    # NOWAIT is intentional: this would raise LockNotAvailableError immediately if speaking_turn
    # retained the row lock (or even an earlier SELECT FOR UPDATE) during STT.
    async with postgres_session_factory() as competing_db:
        locked = (
            await competing_db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == record.session_id)
                .with_for_update(nowait=True)
            )
        ).scalar_one()
        assert locked.id == record.session_id
        await competing_db.rollback()

    release_stt.set()
    response = await asyncio.wait_for(submit_task, timeout=10)
    assert response.state_revision == state["state_revision"] + 1

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    assert len(stored.exam_state["speaking"]["results"]) == 1


async def _async(value):
    return value


async def test_two_concurrent_initiates_create_one_active_exam(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """The two-phase initiate flow must recheck under the per-user PostgreSQL row lock."""

    # An abandoned historical row supplies the real user/language identities without being an
    # active attempt that initiate_exam could resume.
    record = await exam_record_factory(
        state={"version": 3, "state_revision": 1, "sections": [], "cursor": 0},
        status="abandoned",
    )
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        language_exam,
        "get_default_language",
        lambda _db: _async(SimpleNamespace(id=record.language_id)),
    )
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))
    monkeypatch.setattr(language_exam, "_student_grade", lambda *_args, **_kwargs: _async(None))

    scenario_arrivals = 0
    scenario_lock = asyncio.Lock()
    both_generating = asyncio.Event()

    async def generate_scenario(**_kwargs) -> dict:
        nonlocal scenario_arrivals
        async with scenario_lock:
            scenario_arrivals += 1
            if scenario_arrivals == 2:
                both_generating.set()
        await asyncio.wait_for(both_generating.wait(), timeout=5)
        return {
            "scenario": "At a community event",
            "ai_persona": "Host",
            "student_role": "Guest",
            "setting": "Community hall",
            "opening_question": "What brought you to the event?",
        }

    monkeypatch.setattr(
        language_exam.ai_engine,
        "generate_scenario_and_opening",
        generate_scenario,
    )

    async def initiate():
        async with postgres_session_factory() as db:
            return await language_exam.initiate_exam(
                BackgroundTasks(),
                student=record.student,
                db=db,
            )

    responses = await asyncio.wait_for(
        asyncio.gather(initiate(), initiate()),
        timeout=15,
    )

    assert scenario_arrivals == 2
    assert responses[0].session_id == responses[1].session_id
    async with postgres_session_factory() as db:
        active = (
            await db.execute(
                select(LanguageExamSession).where(
                    LanguageExamSession.student_id == record.student_id,
                    LanguageExamSession.language_id == record.language_id,
                    LanguageExamSession.status.in_(("in_progress", "evaluating")),
                )
            )
        ).scalars().all()
    assert len(active) == 1
    assert active[0].id == responses[0].session_id


async def test_new_exam_session_never_includes_interview_in_sections(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """Product decision: new AI Exam sessions must never include "interview" in their persisted
    sections. Speaking stays mandatory and unaffected (its own section is unchanged)."""
    assert "interview" not in language_exam.SECTIONS
    assert "speaking" in language_exam.SECTIONS
    assert language_exam.SPEAKING_TURNS == 3

    record = await exam_record_factory(
        state={"version": 3, "state_revision": 1, "sections": [], "cursor": 0},
        status="abandoned",
    )
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        language_exam,
        "get_default_language",
        lambda _db: _async(SimpleNamespace(id=record.language_id)),
    )
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))
    monkeypatch.setattr(language_exam, "_student_grade", lambda *_args, **_kwargs: _async(None))

    async def generate_scenario(**_kwargs) -> dict:
        return {
            "scenario": "At a community event",
            "ai_persona": "Host",
            "student_role": "Guest",
            "setting": "Community hall",
            "opening_question": "What brought you to the event?",
        }

    monkeypatch.setattr(language_exam.ai_engine, "generate_scenario_and_opening", generate_scenario)

    async with postgres_session_factory() as db:
        student = await db.get(User, record.student_id)
        response = await language_exam.initiate_exam(BackgroundTasks(), student=student, db=db)

    stored = await _stored_exam(postgres_session_factory, response.session_id)
    assert "interview" not in stored.exam_state["sections"]
    assert "interview" not in stored.exam_state
    assert stored.exam_state["speaking"]["total_turns"] == 3


async def test_initiate_exam_does_not_touch_expired_student_attributes_after_ai_call(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """Regression test for a live MissingGreenlet 500: initiate_exam must not read
    student.id/language.id as bare ORM attributes after the mid-function commit that precedes
    the external AI call. In production, expire_on_commit marks them stale and a slow-enough
    network call lets the connection pool recycle the connection; the next bare attribute read
    then tries an implicit lazy-reload outside any awaited call and raises MissingGreenlet.

    That exact failure is connection-pool-timing dependent (confirmed empirically: a 50ms
    asyncio.sleep between commit and the next access was not sufficient to reproduce it against
    the test database, even against the unfixed code). To make this a reliable regression guard
    rather than a flaky timing-dependent one, this test forces the same *condition* the
    production bug depends on — student/language becoming unusable after the pre-AI-call commit —
    by expiring and detaching them from the session at exactly that point. Real ORM objects are
    used for both (unlike the concurrent-initiate test above, which passes a SimpleNamespace for
    student and so never exercises this at all). Without the fix, this raises
    sqlalchemy.orm.exc.DetachedInstanceError from the same lines the real MissingGreenlet did.
    """

    record = await exam_record_factory(
        state={"version": 3, "state_revision": 1, "sections": [], "cursor": 0},
        status="abandoned",
    )
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(language_exam, "_effective_level", lambda *_args, **_kwargs: _async("A2"))
    monkeypatch.setattr(language_exam, "_student_grade", lambda *_args, **_kwargs: _async(None))

    async def generate_scenario(**_kwargs) -> dict:
        return {
            "scenario": "At a community event",
            "ai_persona": "Host",
            "student_role": "Guest",
            "setting": "Community hall",
            "opening_question": "What brought you to the event?",
        }

    monkeypatch.setattr(language_exam.ai_engine, "generate_scenario_and_opening", generate_scenario)

    async with postgres_session_factory() as db:
        student = await db.get(User, record.student_id)
        language = await db.get(Language, record.language_id)
        monkeypatch.setattr(language_exam, "get_default_language", lambda _db: _async(language))

        real_commit = db.commit
        expired_once = False

        async def commit_then_expire_and_detach():
            nonlocal expired_once
            await real_commit()
            if not expired_once:
                expired_once = True
                db.expire(student)
                db.expire(language)
                db.expunge(student)
                db.expunge(language)

        monkeypatch.setattr(db, "commit", commit_then_expire_and_detach)

        response = await language_exam.initiate_exam(
            BackgroundTasks(),
            student=student,
            db=db,
        )

    assert response.session_id is not None
    async with postgres_session_factory() as db:
        active = (
            await db.execute(
                select(LanguageExamSession).where(
                    LanguageExamSession.student_id == record.student_id,
                    LanguageExamSession.status.in_(("in_progress", "evaluating")),
                )
            )
        ).scalar_one()
    assert active.id == response.session_id


def _completed_evidence_state() -> dict:
    objective = {
        "ready": True,
        "pool": {"A2": {"question": "q", "options": ["a"], "correct_index": 0}},
        "asked": [{"level": "A2", "correct": True, "chosen_index": 0}],
        "done": True,
        "evidence_status": "completed",
    }
    speaking_results = [
        {
            "question": f"Speaking question {index}",
            "transcription": f"Verified speaking response number {index}",
            "audio_sha256": hashlib.sha256(f"speaking-{index}".encode()).hexdigest(),
        }
        for index in range(3)
    ]
    return {
        "version": 3,
        "state_revision": 21,
        "sections": list(language_exam.SECTIONS),
        "cursor": len(language_exam.SECTIONS),
        "listening": copy.deepcopy(objective),
        "reading": copy.deepcopy(objective),
        "grammar_vocab": copy.deepcopy(objective),
        "writing": {
            "ready": True,
            "prompt": "Write a detailed response.",
            "min_words": 40,
            "response": " ".join(f"word{index}" for index in range(45)),
            "done": True,
            "evidence_status": "completed",
        },
        "speaking": {
            "total_turns": 3,
            "results": speaking_results,
            "done": True,
            "evidence_status": "completed",
        },
        # No "interview" section — matches a genuine no-interview session (product decision:
        # guided interview removed; "sections" already derives from language_exam.SECTIONS above,
        # which no longer includes it).
        "evaluation": {
            "evaluation_status": "pending",
            "evaluation_attempt": 0,
            "evaluation_owner": None,
            "evaluation_lease_expires_at": None,
        },
        "request_receipts": [],
    }


async def test_evaluation_lease_has_one_owner_and_one_expired_lease_successor(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    record = await exam_record_factory(state=_completed_evidence_state(), status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)

    initial_claims = await asyncio.wait_for(
        asyncio.gather(
            language_exam._claim_evaluation_lease(record.session_id),
            language_exam._claim_evaluation_lease(record.session_id),
        ),
        timeout=10,
    )
    initial_winners = [claim for claim in initial_claims if claim is not None]
    assert len(initial_winners) == 1
    first_owner = initial_winners[0][0]

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    assert stored.exam_state["evaluation"]["evaluation_owner"] == first_owner
    assert stored.exam_state["evaluation"]["evaluation_attempt"] == 1

    async with postgres_session_factory() as db:
        exam = (
            await db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == record.session_id)
                .with_for_update()
            )
        ).scalar_one()
        expired = copy.deepcopy(exam.exam_state or {})
        expired["evaluation"]["evaluation_lease_expires_at"] = (
            datetime.now(timezone.utc) - timedelta(seconds=1)
        ).isoformat()
        exam.exam_state = expired
        flag_modified(exam, "exam_state")
        await db.commit()

    recovery_claims = await asyncio.wait_for(
        asyncio.gather(
            language_exam._claim_evaluation_lease(record.session_id),
            language_exam._claim_evaluation_lease(record.session_id),
        ),
        timeout=10,
    )
    recovery_winners = [claim for claim in recovery_claims if claim is not None]
    assert len(recovery_winners) == 1
    successor_owner = recovery_winners[0][0]
    assert successor_owner != first_owner

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    evaluation = stored.exam_state["evaluation"]
    assert evaluation["evaluation_status"] == "running"
    assert evaluation["evaluation_owner"] == successor_owner
    assert evaluation["evaluation_attempt"] == 2
    assert datetime.fromisoformat(evaluation["evaluation_lease_expires_at"]) > datetime.now(
        timezone.utc
    )


async def test_two_concurrent_evaluation_retries_enqueue_one_worker(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    state = _completed_evidence_state()
    state["state_revision"] = 31
    state["evaluation"] = {
        "evaluation_status": "scorer_unavailable",
        "evaluation_attempt": 1,
        "evaluation_owner": None,
        "evaluation_lease_expires_at": None,
        "error_code": "scorer_unavailable",
    }
    record = await exam_record_factory(state=state, status="failed")
    monkeypatch.setattr(language_exam, "check_or_raise", lambda *_args, **_kwargs: None)

    backgrounds = [BackgroundTasks(), BackgroundTasks()]

    async def retry(index: int):
        async with postgres_session_factory() as db:
            return await language_exam.retry_exam_evaluation(
                record.session_id,
                backgrounds[index],
                student=record.student,
                db=db,
            )

    responses = await asyncio.wait_for(
        asyncio.gather(retry(0), retry(1)),
        timeout=10,
    )

    assert all(response.session_id == record.session_id for response in responses)
    assert sum(len(background.tasks) for background in backgrounds) == 1
    stored = await _stored_exam(postgres_session_factory, record.session_id)
    assert stored.status == "evaluating"
    assert stored.exam_state["evaluation"]["evaluation_status"] == "pending"
    assert stored.exam_state["state_revision"] == state["state_revision"] + 1


async def test_ai_grading_failure_creates_no_profile_or_analytics_projection(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    record = await exam_record_factory(state=_completed_evidence_state(), status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)

    async def unavailable_speaking_grader(**_kwargs):
        raise ExamAIError("authoritative speaking scorer unavailable")

    monkeypatch.setattr(language_exam.ai_engine, "grade_speaking", unavailable_speaking_grader)

    await language_exam._run_evaluation(record.session_id)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    evaluation = stored.exam_state["evaluation"]
    assert stored.status == "failed"
    assert stored.is_completed is False
    assert stored.assessment_report is None
    assert evaluation["evaluation_status"] == "scorer_unavailable"
    assert evaluation["error_code"] == "scorer_unavailable"
    assert evaluation["evaluation_lease_expires_at"] is None

    async with postgres_session_factory() as db:
        analytics = await db.get(
            LanguageAnalytics,
            {"student_id": record.student_id, "language_id": record.language_id},
        )
        profile = (
            await db.execute(
                select(LanguageStudentProfile).where(
                    LanguageStudentProfile.student_id == record.student_id,
                    LanguageStudentProfile.language_id == record.language_id,
                )
            )
        ).scalar_one_or_none()
    assert analytics is None
    assert profile is None


async def test_malformed_ai_grading_output_leaves_the_session_safely_failed(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """A schema-invalid (not merely absent) AI grading response must fail the exam the same
    safe way an outright-unavailable grader already does: no level, no profile/analytics rows,
    no silent completion."""

    record = await exam_record_factory(state=_completed_evidence_state(), status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(language_exam.ai_engine, "_mock", False)

    async def malformed_llm_json(*_args, **_kwargs):
        # Schema-invalid: "fluency" is out of the 0.0-10.0 range Pydantic enforces.
        return (
            '{"level": "B1", "fluency": 999.0, "lexical": 5.0, "grammar": 5.0, '
            '"pronunciation": 0.0, "score": 5.0}'
        )

    monkeypatch.setattr(language_exam_service, "generate_llm_json", malformed_llm_json)

    await language_exam._run_evaluation(record.session_id)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    evaluation = stored.exam_state["evaluation"]
    assert stored.status == "failed"
    assert stored.is_completed is False
    assert stored.assessment_report is None
    assert evaluation["evaluation_status"] == "scorer_unavailable"
    assert evaluation["error_code"] == "scorer_unavailable"

    async with postgres_session_factory() as db:
        analytics = await db.get(
            LanguageAnalytics,
            {"student_id": record.student_id, "language_id": record.language_id},
        )
        profile = (
            await db.execute(
                select(LanguageStudentProfile).where(
                    LanguageStudentProfile.student_id == record.student_id,
                    LanguageStudentProfile.language_id == record.language_id,
                )
            )
        ).scalar_one_or_none()
    assert analytics is None
    assert profile is None


async def test_evaluation_heartbeat_prevents_a_second_live_worker(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """A healthy slow scorer renews its lease, so no second billable evaluation starts."""

    record = await exam_record_factory(state=_completed_evidence_state(), status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(language_exam, "EVALUATION_LEASE_SECONDS", 1)

    first_grader_waiting = asyncio.Event()
    release_first_grader = asyncio.Event()
    grader_calls = 0
    grader_call_lock = asyncio.Lock()

    speaking_grade = SpeakingGradeSchema(
        level=CEFRLevel.B1,
        fluency=5.0,
        lexical=5.0,
        grammar=5.0,
        pronunciation=0.0,
        score=5.0,
        feedback="Pronunciation was unassessed.",
        detected_errors=[],
    )
    writing_grade = WritingGradeSchema(
        level=CEFRLevel.B1,
        task_achievement=5.0,
        coherence=5.0,
        lexical=5.0,
        grammar=5.0,
        score=5.0,
        feedback="A complete response.",
        detected_errors=[],
    )
    narrative = ExamNarrativeSchema(
        summary="The verified evidence supports a conservative B1 placement.",
        strengths=["Communicates connected ideas."],
        weaknesses=["Needs more grammatical range."],
        recommendations=["Practise connected speech.", "Review verb forms.", "Read daily."],
        detected_errors=[],
        recommended_starting_lesson_topic="Past and present verb forms",
    )

    async def controlled_speaking_grade(**_kwargs) -> SpeakingGradeSchema:
        nonlocal grader_calls
        async with grader_call_lock:
            grader_calls += 1
            call_number = grader_calls
        if call_number == 1:
            first_grader_waiting.set()
            await asyncio.wait_for(release_first_grader.wait(), timeout=10)
        return speaking_grade

    async def successful_writing_grade(**_kwargs) -> WritingGradeSchema:
        return writing_grade

    async def successful_narrative(**_kwargs) -> ExamNarrativeSchema:
        return narrative

    monkeypatch.setattr(language_exam.ai_engine, "grade_speaking", controlled_speaking_grade)
    monkeypatch.setattr(language_exam.ai_engine, "grade_writing", successful_writing_grade)
    monkeypatch.setattr(language_exam.ai_engine, "build_final_narrative", successful_narrative)

    original_next_retake = language_exam.next_allowed_retake_at
    projection_calls = 0

    def counted_next_retake(now):
        nonlocal projection_calls
        projection_calls += 1
        return original_next_retake(now)

    monkeypatch.setattr(language_exam, "next_allowed_retake_at", counted_next_retake)

    stale_worker = asyncio.create_task(language_exam._run_evaluation(record.session_id))
    await asyncio.wait_for(first_grader_waiting.wait(), timeout=5)
    # Wait beyond the original one-second lease. The heartbeat must have extended it.
    await asyncio.sleep(1.2)
    successor_worker = asyncio.create_task(language_exam._run_evaluation(record.session_id))
    await asyncio.wait_for(successor_worker, timeout=10)
    release_first_grader.set()
    await asyncio.wait_for(stale_worker, timeout=10)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    assert stored.status == "completed"
    assert stored.is_completed is True
    assert stored.assessment_report is not None
    assert stored.exam_state["evaluation"]["evaluation_status"] == "completed"
    assert stored.exam_state["evaluation"]["evaluation_attempt"] == 1
    assert grader_calls == 1
    assert projection_calls == 1

    async with postgres_session_factory() as db:
        analytics_rows = (
            await db.execute(
                select(LanguageAnalytics).where(
                    LanguageAnalytics.student_id == record.student_id,
                    LanguageAnalytics.language_id == record.language_id,
                )
            )
        ).scalars().all()
        profile_rows = (
            await db.execute(
                select(LanguageStudentProfile).where(
                    LanguageStudentProfile.student_id == record.student_id,
                    LanguageStudentProfile.language_id == record.language_id,
                )
            )
        ).scalars().all()
    assert len(analytics_rows) == 1
    assert len(profile_rows) == 1


async def test_no_interview_exam_completes_without_live_phase_unavailable_penalty(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """A fully-evidenced no-interview session (3 speaking turns + listening/reading/grammar_vocab
    + writing, no "interview" section at all) must reach evaluation, complete normally, and set
    placement_completed_at through the ordinary AI Exam completion flow. It must NOT be penalized
    with cross_phase_consistency="live_phase_unavailable" (and the accompanying low confidence
    cap) merely because interview was intentionally removed by design — that label previously
    meant "the interview phase ran but produced no results", not "there was no interview phase to
    begin with"."""

    state = _completed_evidence_state()
    assert "interview" not in state["sections"]
    record = await exam_record_factory(state=state, status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)

    speaking_grade = SpeakingGradeSchema(
        level=CEFRLevel.B1, fluency=5.0, lexical=5.0, grammar=5.0, pronunciation=0.0,
        score=5.0, feedback="Pronunciation was unassessed.", detected_errors=[],
    )
    writing_grade = WritingGradeSchema(
        level=CEFRLevel.B1, task_achievement=5.0, coherence=5.0, lexical=5.0, grammar=5.0,
        score=5.0, feedback="A complete response.", detected_errors=[],
    )
    narrative = ExamNarrativeSchema(
        summary="No-interview placement.",
        strengths=["Communicates clearly."],
        weaknesses=["Needs more grammatical range."],
        recommendations=["Practise connected speech.", "Review verb forms.", "Read daily."],
        detected_errors=[],
        recommended_starting_lesson_topic="Past and present verb forms",
    )

    async def successful_speaking_grade(**_kwargs) -> SpeakingGradeSchema:
        return speaking_grade

    async def successful_writing_grade(**_kwargs) -> WritingGradeSchema:
        return writing_grade

    async def successful_narrative(**_kwargs) -> ExamNarrativeSchema:
        return narrative

    monkeypatch.setattr(language_exam.ai_engine, "grade_speaking", successful_speaking_grade)
    monkeypatch.setattr(language_exam.ai_engine, "grade_writing", successful_writing_grade)
    monkeypatch.setattr(language_exam.ai_engine, "build_final_narrative", successful_narrative)

    await language_exam._run_evaluation(record.session_id)

    stored = await _stored_exam(postgres_session_factory, record.session_id)
    assert stored.status == "completed"
    assert stored.is_completed is True
    assert stored.assessment_report is not None
    assert "interview" not in (stored.exam_state.get("sections") or [])
    assert stored.assessment_report["cross_phase_consistency"] != "live_phase_unavailable"
    assert stored.assessment_report["confidence"] > 0.5

    async with postgres_session_factory() as db:
        profile = (
            await db.execute(
                select(LanguageStudentProfile).where(
                    LanguageStudentProfile.student_id == record.student_id,
                    LanguageStudentProfile.language_id == record.language_id,
                )
            )
        ).scalar_one()
    assert profile.placement_completed_at is not None


async def test_placement_completed_at_is_set_once_and_survives_a_retake(
    monkeypatch,
    postgres_session_factory,
    exam_record_factory,
) -> None:
    """AI Exam completion is the sole writer of placement_completed_at; a retake must not reset it."""

    record = await exam_record_factory(state=_completed_evidence_state(), status="evaluating")
    monkeypatch.setattr(language_exam, "AsyncSessionLocal", postgres_session_factory)
    monkeypatch.setattr(language_exam, "check", lambda *_args, **_kwargs: True)

    speaking_grade = SpeakingGradeSchema(
        level=CEFRLevel.B1,
        fluency=5.0,
        lexical=5.0,
        grammar=5.0,
        pronunciation=0.0,
        score=5.0,
        feedback="Pronunciation was unassessed.",
        detected_errors=[],
    )
    writing_grade = WritingGradeSchema(
        level=CEFRLevel.B1,
        task_achievement=5.0,
        coherence=5.0,
        lexical=5.0,
        grammar=5.0,
        score=5.0,
        feedback="A complete response.",
        detected_errors=[],
    )
    narrative = ExamNarrativeSchema(
        summary="First placement.",
        strengths=["Communicates connected ideas."],
        weaknesses=["Needs more grammatical range."],
        recommendations=["Practise connected speech.", "Review verb forms.", "Read daily."],
        detected_errors=[],
        recommended_starting_lesson_topic="Past and present verb forms",
    )

    async def successful_speaking_grade(**_kwargs) -> SpeakingGradeSchema:
        return speaking_grade

    async def successful_writing_grade(**_kwargs) -> WritingGradeSchema:
        return writing_grade

    async def successful_narrative(**_kwargs) -> ExamNarrativeSchema:
        return narrative

    monkeypatch.setattr(language_exam.ai_engine, "grade_speaking", successful_speaking_grade)
    monkeypatch.setattr(language_exam.ai_engine, "grade_writing", successful_writing_grade)
    monkeypatch.setattr(language_exam.ai_engine, "build_final_narrative", successful_narrative)

    await language_exam._run_evaluation(record.session_id)

    async def _load_profile() -> LanguageStudentProfile:
        async with postgres_session_factory() as db:
            return (
                await db.execute(
                    select(LanguageStudentProfile).where(
                        LanguageStudentProfile.student_id == record.student_id,
                        LanguageStudentProfile.language_id == record.language_id,
                    )
                )
            ).scalar_one()

    profile = await _load_profile()
    assert profile.placement_completed_at is not None
    first_completed_at = profile.placement_completed_at
    first_last_assessment = profile.last_assessment_date

    # Simulate a retake: a second, independently-completed session for the same student/language.
    async with postgres_session_factory() as db:
        second_exam = LanguageExamSession(
            id=uuid.uuid4().hex,
            student_id=record.student_id,
            language_id=record.language_id,
            current_step=1,
            max_steps=len(language_exam.SECTIONS),
            exam_state=copy.deepcopy(_completed_evidence_state()),
            status="evaluating",
            is_completed=False,
        )
        db.add(second_exam)
        await db.commit()
        second_session_id = second_exam.id

    await language_exam._run_evaluation(second_session_id)

    second_stored = await _stored_exam(postgres_session_factory, second_session_id)
    assert second_stored.status == "completed"
    assert second_stored.is_completed is True

    profile = await _load_profile()
    assert profile.placement_completed_at == first_completed_at
    assert profile.last_assessment_date is not None
    assert profile.last_assessment_date >= first_last_assessment
