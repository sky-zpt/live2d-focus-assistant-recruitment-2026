"""SQLite 仓储层测试。"""

import sqlite3

import pytest

from app import create_app
from src import repositories


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "focus-test.db"
    return create_app({"TESTING": True, "DATABASE": str(database_path)})


@pytest.fixture
def connection(app):
    with app.app_context():
        from src.db import get_db

        yield get_db()


def make_session(connection, **overrides):
    values = {
        "task_text": "完成仓储测试",
        "duration_seconds": 1500,
        "remaining_seconds": 1500,
        "started_at": "2026-09-14T09:00:00+08:00",
        "last_started_at": "2026-09-14T09:00:00+08:00",
        "finished_at": None,
        "status": "active",
    }
    values.update(overrides)
    return repositories.create_session(connection, **values)


def test_create_and_get_session_by_id(connection):
    created = make_session(connection)

    assert created["id"] > 0
    assert created["task_text"] == "完成仓储测试"
    assert repositories.get_session_by_id(connection, created["id"]) == created
    assert repositories.get_session_by_id(connection, 9999) is None


def test_get_open_session_returns_active_or_paused_session(connection):
    assert repositories.get_open_session(connection) is None

    created = make_session(connection, status="paused", last_started_at=None)

    assert repositories.get_open_session(connection) == created


def test_update_session_returns_updated_record(connection):
    created = make_session(connection)

    updated = repositories.update_session(
        connection,
        created["id"],
        remaining_seconds=900,
        status="paused",
        last_started_at=None,
    )

    assert updated["remaining_seconds"] == 900
    assert updated["status"] == "paused"
    assert updated["last_started_at"] is None


def test_update_session_rejects_unknown_column(connection):
    created = make_session(connection)

    with pytest.raises(ValueError, match="不允许更新字段"):
        repositories.update_session(connection, created["id"], is_admin=True)


def test_list_completed_sessions_sorts_by_finished_time_descending(connection):
    first = make_session(
        connection,
        status="completed",
        last_started_at=None,
        finished_at="2026-09-14T10:00:00+08:00",
    )
    second = make_session(
        connection,
        status="completed",
        last_started_at=None,
        finished_at="2026-09-14T11:00:00+08:00",
    )

    records = repositories.list_completed_sessions(connection, limit=10)

    assert [record["id"] for record in records] == [second["id"], first["id"]]


def test_database_allows_only_one_open_session(connection):
    make_session(connection, status="active")

    with pytest.raises(sqlite3.IntegrityError):
        make_session(connection, status="paused", last_started_at=None)


def test_repeated_application_initialization_keeps_existing_records(tmp_path):
    database_path = tmp_path / "persistent-focus.db"
    first_app = create_app({"TESTING": True, "DATABASE": str(database_path)})

    with first_app.app_context():
        from src.db import get_db

        created = make_session(get_db())

    second_app = create_app({"TESTING": True, "DATABASE": str(database_path)})
    with second_app.app_context():
        from src.db import get_db

        restored = repositories.get_session_by_id(get_db(), created["id"])

    assert restored["task_text"] == "完成仓储测试"
