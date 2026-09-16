"""专注记录 JSON 导入导出。"""
import json
from datetime import datetime
from sqlite3 import Connection
from . import repositories

FIELDS = ("task_text", "duration_seconds", "remaining_seconds", "started_at", "last_started_at", "finished_at", "status", "archived")

def export_json(connection):
    return json.dumps(repositories.all_sessions(connection), ensure_ascii=False, indent=2)

def import_json(connection, payload, *, replace=False):
    records = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(records, list): raise ValueError("导入内容必须是记录数组")
    if replace: connection.execute("DELETE FROM focus_sessions")
    count = 0
    for item in records:
        if not isinstance(item, dict): raise ValueError("每条记录必须是对象")
        values = [item.get(field) for field in FIELDS]
        if not values[0] or values[6] not in {"active", "paused", "completed", "abandoned"}:
            raise ValueError("记录缺少有效任务或状态")
        connection.execute("INSERT INTO focus_sessions (task_text,duration_seconds,remaining_seconds,started_at,last_started_at,finished_at,status,archived) VALUES (?,?,?,?,?,?,?,?)", values)
        count += 1
    connection.commit(); return count
