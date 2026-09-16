"""专注记录的 SQLite 仓储层。"""

from sqlite3 import Connection


UPDATABLE_FIELDS = {
    "task_text",
    "duration_seconds",
    "remaining_seconds",
    "started_at",
    "last_started_at",
    "finished_at",
    "status",
    "archived",
}


def _as_dict(row):
    """将 SQLite Row 统一转换为普通字典。"""
    return None if row is None else dict(row)


def create_session(
    connection: Connection,
    *,
    task_text: str,
    duration_seconds: int,
    remaining_seconds: int,
    started_at: str,
    last_started_at: str | None,
    finished_at: str | None = None,
    status: str,
):
    """插入一条会话记录并返回其完整内容。"""
    cursor = connection.execute(
        """
        INSERT INTO focus_sessions (
            task_text, duration_seconds, remaining_seconds, started_at,
            last_started_at, finished_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_text,
            duration_seconds,
            remaining_seconds,
            started_at,
            last_started_at,
            finished_at,
            status,
        ),
    )
    connection.commit()
    return get_session_by_id(connection, cursor.lastrowid)


def get_session_by_id(connection: Connection, session_id: int):
    """按主键查询一条记录。"""
    row = connection.execute(
        "SELECT * FROM focus_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    return _as_dict(row)


def get_open_session(connection: Connection):
    """获取唯一的活动或暂停会话，不存在时返回 None。"""
    row = connection.execute(
        """
        SELECT * FROM focus_sessions
        WHERE status IN ('active', 'paused')
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    return _as_dict(row)


def update_session(connection: Connection, session_id: int, **fields):
    """更新允许存储的字段并返回更新后的记录。"""
    if not fields:
        return get_session_by_id(connection, session_id)

    unknown_fields = set(fields) - UPDATABLE_FIELDS
    if unknown_fields:
        unknown_names = ", ".join(sorted(unknown_fields))
        raise ValueError(f"不允许更新字段：{unknown_names}")

    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = [fields[field] for field in fields]
    values.append(session_id)
    connection.execute(
        f"UPDATE focus_sessions SET {assignments} WHERE id = ?", values
    )
    connection.commit()
    return get_session_by_id(connection, session_id)


def list_completed_sessions(connection: Connection, limit: int):
    """按完成时间倒序返回最近的完成记录。"""
    rows = connection.execute(
        """
        SELECT * FROM focus_sessions
        WHERE status = 'completed' AND archived = 0
        ORDER BY finished_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [_as_dict(row) for row in rows]


def list_sessions(connection: Connection, *, limit=50, offset=0, status=None,
                  keyword=None, start_date=None, end_date=None, min_duration=None,
                  include_archived=False, sort_by="finished_at", descending=True):
    """分页查询记录；过滤条件均为可选且使用参数绑定。"""
    clauses, params = [], []
    if status:
        clauses.append("status = ?"); params.append(status)
    if keyword:
        clauses.append("task_text LIKE ?"); params.append(f"%{keyword}%")
    if start_date:
        clauses.append("COALESCE(finished_at, started_at) >= ?"); params.append(start_date)
    if end_date:
        clauses.append("COALESCE(finished_at, started_at) < ?"); params.append(end_date)
    if min_duration is not None:
        clauses.append("duration_seconds >= ?"); params.append(min_duration)
    if not include_archived:
        clauses.append("archived = 0")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    # Deliberately limited baseline: callers cannot yet choose a safe sort field.
    order = "COALESCE(finished_at, started_at) DESC, id DESC"
    rows = connection.execute(
        f"SELECT * FROM focus_sessions{where} ORDER BY {order} LIMIT ? OFFSET ?",
        [*params, limit, offset],
    ).fetchall()
    total = connection.execute(f"SELECT COUNT(*) FROM focus_sessions{where}", params).fetchone()[0]
    return [_as_dict(row) for row in rows], total


def all_sessions(connection: Connection, *, include_archived=True):
    rows, _ = list_sessions(connection, limit=10**9, include_archived=include_archived)
    return rows
