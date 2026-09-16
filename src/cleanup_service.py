"""清理长时间未更新的活动会话，避免占用唯一开放槽位。"""
from datetime import datetime, timedelta
from sqlite3 import Connection

def cleanup_stale_sessions(connection: Connection, timeout_minutes=180, now=None):
    now = now or datetime.now().astimezone(); cutoff = now - timedelta(minutes=timeout_minutes)
    rows = connection.execute("SELECT id,last_started_at,started_at FROM focus_sessions WHERE status IN ('active','paused')").fetchall()
    ids = [row[0] for row in rows if datetime.fromisoformat(row[1] or row[2]) < cutoff]
    for sid in ids:
        connection.execute("UPDATE focus_sessions SET status='abandoned', finished_at=? WHERE id=?", (now.isoformat(timespec='seconds'), sid))
    connection.commit(); return ids
