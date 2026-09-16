"""REST API 合约测试。"""

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "api.db")})


@pytest.fixture
def client(app):
    return app.test_client()


def create_task(client, task_text="完成 API 测试"):
    return client.post("/api/sessions", json={"task_text": task_text})


def test_get_active_session_returns_null_when_empty(client):
    response = client.get("/api/sessions/active")

    assert response.status_code == 200
    assert response.get_json() == {"session": None}


def test_create_pause_resume_complete_and_list_sessions(client):
    created_response = create_task(client)
    created = created_response.get_json()["session"]

    paused = client.post(f"/api/sessions/{created['id']}/pause")
    resumed = client.post(f"/api/sessions/{created['id']}/resume")
    completed = client.post(f"/api/sessions/{created['id']}/complete")
    history = client.get("/api/sessions?limit=10")

    assert created_response.status_code == 201
    assert paused.status_code == 200
    assert paused.get_json()["session"]["status"] == "paused"
    assert resumed.status_code == 200
    assert resumed.get_json()["session"]["status"] == "active"
    assert completed.status_code == 200
    assert completed.get_json()["session"]["status"] == "completed"
    assert history.status_code == 200
    assert [item["id"] for item in history.get_json()["sessions"]] == [created["id"]]


def test_abandon_session_returns_success_and_releases_task_slot(client):
    created = create_task(client).get_json()["session"]

    response = client.post(f"/api/sessions/{created['id']}/abandon")

    assert response.status_code == 200
    assert response.get_json()["session"]["status"] == "abandoned"
    assert create_task(client, "开始下一件事").status_code == 201


@pytest.mark.parametrize(
    ("path", "kwargs"),
    [
        ("/api/sessions", {}),
        ("/api/sessions", {"data": "{}", "content_type": "text/plain"}),
        ("/api/sessions", {"json": []}),
        ("/api/sessions", {"json": {"task_text": "任务", "extra": True}}),
        ("/api/sessions", {"json": {"task_text": 123}}),
    ],
)
def test_create_session_rejects_invalid_json_requests(client, path, kwargs):
    response = client.post(path, **kwargs)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_duplicate_create_and_duplicate_complete_return_conflict(client):
    created = create_task(client).get_json()["session"]

    duplicate_create = create_task(client, "另一件事")
    first_complete = client.post(f"/api/sessions/{created['id']}/complete")
    duplicate_complete = client.post(f"/api/sessions/{created['id']}/complete")

    assert duplicate_create.status_code == 409
    assert first_complete.status_code == 200
    assert duplicate_complete.status_code == 409


@pytest.mark.parametrize("path", ["/api/sessions/999/pause", "/api/sessions/999/complete"])
def test_missing_session_returns_not_found(client, path):
    response = client.post(path)

    assert response.status_code == 404
    assert "error" in response.get_json()


@pytest.mark.parametrize("limit", ["0", "51", "many"])
def test_invalid_history_limit_returns_bad_request(client, limit):
    response = client.get(f"/api/sessions?limit={limit}")

    assert response.status_code == 400
    assert "error" in response.get_json()
