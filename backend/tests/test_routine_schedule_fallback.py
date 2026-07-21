from __future__ import annotations

import asyncio
from types import SimpleNamespace

from app.services import claude_service
from app.services.routine_service import _generate_schedule_claude, _validate_slots


def _profile() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        student_id=5,
        grade_level="7",
        school_start="07:30",
        school_end="13:00",
        wake_time="06:30",
        sleep_time="22:00",
        school_days_json="[0,1,2,3,4]",
        activities_json="{}",
    )


def run(coro):
    return asyncio.run(coro)


def test_routine_schedule_generation_falls_back_when_claude_is_unconfigured(monkeypatch):
    monkeypatch.setattr(claude_service, "is_claude_configured", lambda: False)

    schedule = run(
        _generate_schedule_claude(
            None,
            _profile(),
            {"0": "بعد المدرسة عندي راحة قصيرة وبعدين دراسة."},
            ["رياضيات"],
        )
    )

    assert sorted(schedule.keys()) == ["0", "1", "2", "3", "4", "5", "6"]
    assert _validate_slots(schedule) == []
    assert any(slot["type"] == "school" for slot in schedule["0"])
    assert any(slot["type"] == "study" and slot["subject"] == "رياضيات" for slots in schedule.values() for slot in slots)


def test_routine_schedule_generation_falls_back_when_claude_returns_conflicts(monkeypatch):
    monkeypatch.setattr(claude_service, "is_claude_configured", lambda: True)
    monkeypatch.setattr(
        claude_service,
        "generate_claude_json_sync",
        lambda *args, **kwargs: (
            '{"days":{"0":['
            '{"start":"10:00","end":"11:00","type":"study","title":"A"},'
            '{"start":"10:30","end":"11:30","type":"study","title":"B"}'
            ']}}'
        ),
    )

    schedule = run(_generate_schedule_claude(None, _profile(), {}, ["إنجليزي"]))

    assert sorted(schedule.keys()) == ["0", "1", "2", "3", "4", "5", "6"]
    assert _validate_slots(schedule) == []
    assert any(slot["type"] == "study" and slot["subject"] == "إنجليزي" for slots in schedule.values() for slot in slots)


def test_routine_schedule_generation_ignores_non_day_keys(monkeypatch):
    monkeypatch.setattr(claude_service, "is_claude_configured", lambda: False)

    schedule = run(
        _generate_schedule_claude(
            None,
            _profile(),
            {"notes": "extra metadata", "_attempt": 1, "0": "دراسة بعد المدرسة"},
            [],
        )
    )

    assert sorted(schedule.keys()) == ["0", "1", "2", "3", "4", "5", "6"]
    assert _validate_slots({**schedule, "notes": [{"start": "10:00", "end": "11:00", "title": "ignore"}]}) == []
