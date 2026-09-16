"""专注助手的 REST API 路由。"""

from flask import Blueprint, jsonify, request

from src.db import get_db
from src.errors import SessionNotFoundError, StateConflictError, ValidationError
from src.services import FocusSessionService
from src import repositories
from src.analytics import daily_summary, report, summary, time_buckets
from src.cleanup_service import cleanup_stale_sessions
from src.import_export import export_json, import_json


api = Blueprint("api", __name__, url_prefix="/api")


def _service() -> FocusSessionService:
    """为当前请求创建使用同一数据库连接的业务服务。"""
    return FocusSessionService(get_db())


def _json_body() -> dict:
    """读取且验证 JSON 对象请求体。"""
    if not request.is_json:
        raise ValidationError("请求 Content-Type 必须为 application/json")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return payload


def _create_payload() -> dict:
    """限制创建会话的请求字段。"""
    payload = _json_body()
    if set(payload) - {"task_text", "duration_minutes"} or "task_text" not in payload:
        raise ValidationError("请求体只能包含 task_text 和 duration_minutes 字段")
    if not isinstance(payload["task_text"], str):
        raise ValidationError("task_text 必须是文本")
    if "duration_minutes" in payload and (
        isinstance(payload["duration_minutes"], bool)
        or not isinstance(payload["duration_minutes"], int)
    ):
        raise ValidationError("duration_minutes 必须是整数")
    payload.setdefault("duration_minutes", 25)
    return payload


def _parse_limit() -> int:
    """读取并验证完成记录条数。"""
    raw_limit = request.args.get("limit", "10")
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError) as error:
        raise ValidationError("limit 必须是 1 到 50 的整数") from error
    if not 1 <= limit <= 50:
        raise ValidationError("limit 必须是 1 到 50 的整数")
    return limit


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": str(error)}), 400


@api.errorhandler(SessionNotFoundError)
def handle_not_found_error(error):
    return jsonify({"error": str(error)}), 404


@api.errorhandler(StateConflictError)
def handle_state_conflict_error(error):
    return jsonify({"error": str(error)}), 409


@api.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify({"error": str(error)}), 400


@api.get("/sessions/active")
def get_active_session():
    return jsonify({"session": _service().get_active_session()})


@api.post("/sessions")
def create_session():
    payload = _create_payload()
    session = _service().create_session(
        payload["task_text"], payload["duration_minutes"]
    )
    return jsonify({"session": session}), 201


@api.post("/sessions/<int:session_id>/pause")
def pause_session(session_id: int):
    session = _service().pause_session(session_id)
    return jsonify({"session": session})


@api.post("/sessions/<int:session_id>/resume")
def resume_session(session_id: int):
    session = _service().resume_session(session_id)
    return jsonify({"session": session})


@api.post("/sessions/<int:session_id>/complete")
def complete_session(session_id: int):
    session = _service().complete_session(session_id)
    return jsonify({"session": session})


@api.post("/sessions/<int:session_id>/abandon")
def abandon_session(session_id: int):
    session = _service().abandon_session(session_id)
    return jsonify({"session": session})


@api.get("/sessions")
def list_completed_sessions():
    sessions = _service().list_completed_sessions(_parse_limit())
    return jsonify({"sessions": sessions})


@api.get("/sessions/search")
def search_sessions():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("page_size", 20))))
    sessions, total = repositories.list_sessions(get_db(), limit=size, offset=(page - 1) * size,
        status=request.args.get("status"), keyword=request.args.get("keyword"),
        start_date=request.args.get("start_date"), end_date=request.args.get("end_date"))
    return jsonify({"sessions": sessions, "page": page, "page_size": size, "total": total})


@api.get("/stats/summary")
def stats_summary(): return jsonify(summary(get_db()))

@api.get("/stats/daily")
def stats_daily(): return jsonify({"days": daily_summary(get_db(), int(request.args.get("days", 30)))})

@api.get("/stats/time-buckets")
def stats_time_buckets(): return jsonify(time_buckets(get_db()))

@api.get("/stats/report")
def stats_report(): return jsonify(report(get_db()))

@api.get("/sessions/export")
def sessions_export():
    response = jsonify({"sessions": repositories.all_sessions(get_db())})
    response.headers["Content-Disposition"] = "attachment; filename=focus-sessions.json"
    return response

@api.post("/sessions/import")
def sessions_import():
    payload = _json_body(); count = import_json(get_db(), payload.get("sessions", []), replace=bool(payload.get("replace", False)))
    return jsonify({"imported": count})

@api.post("/sessions/cleanup")
def sessions_cleanup():
    minutes = int(request.args.get("timeout_minutes", 180))
    return jsonify({"abandoned_ids": cleanup_stale_sessions(get_db(), minutes)})
