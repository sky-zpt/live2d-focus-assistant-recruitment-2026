"""专注会话业务服务测试。"""

from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from src.errors import SessionNotFoundError, StateConflictError, ValidationError
from src.services import FOCUS_DURATION_SECONDS, FocusSessionService


TIMEZONE = timezone(timedelta(hours=8))


class Clock:
    """测试用可推进时钟。"""

    def __init__(self, value):
        self.value = value

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += timedelta(seconds=seconds)


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "service.db")})


@pytest.fixture
def service(app):
    clock = Clock(datetime(2026, 9, 14, 9, 0, tzinfo=TIMEZONE))
    with app.app_context():
        from src.db import get_db

        yield FocusSessionService(get_db(), now=clock.now), clock


def test_create_session_strips_task_and_uses_fixed_duration(service):
    session, _clock = service

    created = session.create_session("  完成服务层测试  ")

    assert created["task_text"] == "完成服务层测试"
    assert created["duration_seconds"] == FOCUS_DURATION_SECONDS
    assert created["remaining_seconds"] == FOCUS_DURATION_SECONDS
    assert created["status"] == "active"


@pytest.mark.parametrize("task_text", ["", "   ", "x" * 81, None])
def test_create_session_rejects_invalid_task_text(service, task_text):
    session, _clock = service

    with pytest.raises(ValidationError):
        session.create_session(task_text)


def test_create_session_rejects_when_an_open_session_exists(service):
    session, _clock = service
    session.create_session("第一件事")

    with pytest.raises(StateConflictError, match="未结束"):
        session.create_session("第二件事")


def test_pause_calculates_remaining_time_and_resume_uses_new_start_time(service):
    session, clock = service
    created = session.create_session("阅读文档")
    clock.advance(321)

    paused = session.pause_session(created["id"])

    assert paused["status"] == "paused"
    assert paused["remaining_seconds"] == 1179
    assert paused["last_started_at"] is None

    clock.advance(200)
    resumed = session.resume_session(created["id"])

    assert resumed["status"] == "active"
    assert resumed["last_started_at"] == "2026-09-14T09:08:41+08:00"


def test_active_session_reports_finished_timer_without_auto_completing(service):
    session, clock = service
    created = session.create_session("专注到底")
    clock.advance(FOCUS_DURATION_SECONDS + 10)

    current = session.get_active_session()

    assert current["id"] == created["id"]
    assert current["remaining_seconds"] == 0
    assert current["timer_finished"] is True
    assert current["status"] == "active"


def test_complete_only_allows_open_session_and_cannot_repeat(service):
    session, clock = service
    created = session.create_session("完成任务")
    clock.advance(120)

    completed = session.complete_session(created["id"])

    assert completed["status"] == "completed"
    assert completed["remaining_seconds"] == 1380
    assert completed["finished_at"] == "2026-09-14T09:02:00+08:00"
    with pytest.raises(StateConflictError):
        session.complete_session(created["id"])


def test_operations_reject_missing_session(service):
    session, _clock = service

    with pytest.raises(SessionNotFoundError):
        session.pause_session(999)
    with pytest.raises(SessionNotFoundError):
        session.resume_session(999)
    with pytest.raises(SessionNotFoundError):
        session.complete_session(999)
    with pytest.raises(SessionNotFoundError):
        session.abandon_session(999)


def test_abandon_releases_open_session_for_a_new_task(service):
    session, _clock = service
    created = session.create_session("暂时放下")

    abandoned = session.abandon_session(created["id"])

    assert abandoned["status"] == "abandoned"
    assert session.create_session("重新开始")["status"] == "active"
