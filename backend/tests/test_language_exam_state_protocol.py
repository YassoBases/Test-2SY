"""Unit contracts for the phase-zero state and idempotency protocol."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.api.language_exam import (
    _ensure_state_protocol,
    _new_exam_token,
    _record_request,
    _request_receipt,
    _require_current_state,
    _state_revision,
    canonical_payload_hash,
    evaluation_lease_expired,
    exam_evidence_statuses,
)


def test_prompt_tokens_are_opaque_and_not_reused():
    first = _new_exam_token()
    second = _new_exam_token()

    assert len(first) >= 24
    assert first != second
    assert not first.isdecimal()


def test_existing_state_is_upgraded_without_touching_answers():
    state = {
        "reading": {"pool": {"A2": {"question": "Q"}}, "asked": [{"correct": True}]},
        "speaking": {"pending_question": "Speak", "results": [{"transcription": "hello"}]},
        "writing": {"prompt": "Write", "response": "existing answer"},
    }

    assert _ensure_state_protocol(state) is True
    assert _state_revision(state) == 1
    assert state["reading"]["pool"]["A2"]["question_token"]
    assert state["speaking"]["turn_token"]
    assert state["writing"]["prompt_token"]
    assert state["reading"]["asked"] == [{"correct": True}]
    assert state["writing"]["response"] == "existing answer"


def test_canonical_payload_hash_is_order_independent_and_input_sensitive():
    first = canonical_payload_hash(kind="mcq_answer", payload={"choice": 1, "token": "abc"})
    reordered = canonical_payload_hash(kind="mcq_answer", payload={"token": "abc", "choice": 1})
    changed = canonical_payload_hash(kind="mcq_answer", payload={"choice": 2, "token": "abc"})

    assert first == reordered
    assert first != changed
    assert len(first) == 64


def test_receipt_accepts_same_payload_and_rejects_conflicting_reuse():
    state = {"state_revision": 8}
    payload_hash = canonical_payload_hash(kind="writing_answer", payload={"text_sha256": "a" * 64})
    _record_request(
        state,
        kind="writing_answer",
        request_id="request-0001",
        payload_hash=payload_hash,
        request_revision=7,
        token="token-1234567890",
        result_reference="writing:revision:8",
    )

    receipt = _request_receipt(
        state,
        kind="writing_answer",
        request_id="request-0001",
        payload_hash=payload_hash,
    )
    assert receipt and receipt["result_reference"] == "writing:revision:8"

    with pytest.raises(HTTPException) as exc_info:
        _request_receipt(
            state,
            kind="writing_answer",
            request_id="request-0001",
            payload_hash="b" * 64,
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["code"] == "idempotency_conflict"


def test_state_revision_and_prompt_token_must_both_match():
    state = {"state_revision": 5}
    _require_current_state(
        state,
        supplied_revision=5,
        supplied_token="token-1234567890",
        expected_token="token-1234567890",
    )

    for revision, token in ((4, "token-1234567890"), (5, "different-token-1")):
        with pytest.raises(HTTPException) as exc_info:
            _require_current_state(
                state,
                supplied_revision=revision,
                supplied_token=token,
                expected_token="token-1234567890",
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["code"] == "stale_exam_state"
        assert exc_info.value.detail["current_state_revision"] == 5


def test_evaluation_lease_distinguishes_active_and_expired_workers():
    now = datetime.now(timezone.utc)
    active = {
        "evaluation": {
            "evaluation_status": "running",
            "evaluation_lease_expires_at": (now + timedelta(minutes=2)).isoformat(),
        }
    }
    expired = {
        "evaluation": {
            "evaluation_status": "running",
            "evaluation_lease_expires_at": (now - timedelta(seconds=1)).isoformat(),
        }
    }

    assert evaluation_lease_expired(active, now=now) is False
    assert evaluation_lease_expired(expired, now=now) is True


def test_evidence_status_separates_server_content_failure_from_student_omission():
    state = {
        "reading": {"ready": False, "pool": {}, "evidence_status": "content_unavailable"},
        "listening": {"ready": True, "pool": {"A2": {}}, "asked": [], "done": False},
        "grammar_vocab": {"ready": True, "pool": {"A2": {}}, "asked": [], "done": False},
        "writing": {"ready": True, "prompt": "Write", "response": None, "done": False},
        "speaking": {"total_turns": 1, "results": [], "done": False},
    }

    statuses = exam_evidence_statuses(state)

    assert statuses["reading"] == "content_unavailable"
    assert statuses["listening"] == "missing_student_response"
    assert statuses["writing"] == "missing_student_response"


def test_evidence_statuses_is_sections_driven_for_speaking_and_interview():
    """New no-interview sessions must not be blocked on evidence for a section they never have;
    old persisted sessions that still list "interview" in their own sections must still require
    it. This is the sections-driven fix that replaced a hardcoded (speaking, interview) tuple."""
    no_interview = {
        "sections": ["speaking", "writing"],
        "speaking": {"total_turns": 3, "results": [], "done": False},
        "writing": {"ready": True, "prompt": "Write", "response": None, "done": False},
    }
    statuses = exam_evidence_statuses(no_interview)
    assert "interview" not in statuses
    assert statuses["speaking"] == "missing_student_response"

    with_interview = {
        "sections": ["speaking", "writing", "interview"],
        "speaking": {"total_turns": 3, "results": [], "done": False},
        "writing": {"ready": True, "prompt": "Write", "response": None, "done": False},
        "interview": {"total_turns": 2, "results": [], "done": False},
    }
    statuses = exam_evidence_statuses(with_interview)
    assert statuses["interview"] == "missing_student_response"
