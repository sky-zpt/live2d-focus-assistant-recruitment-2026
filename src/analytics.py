"""专注历史的统计与报告函数，保持无框架、易于单独复用。"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from sqlite3 import Connection
from . import repositories


def _ended(connection):
    return [s for s in repositories.all_sessions(connection, include_archived=False) if s["status"] in {"completed", "abandoned"}]


def summary(connection):
    rows = _ended(connection)
    completed = [s for s in rows if s["status"] == "completed"]
    durations = [max(0, s["duration_seconds"] - s["remaining_seconds"]) for s in completed]
    return {"total_sessions": len(rows), "completed_sessions": len(completed),
            "abandoned_sessions": len(rows) - len(completed),
            "total_focus_seconds": sum(durations),
            "average_focus_seconds": round(sum(durations) / len(durations), 1) if durations else 0,
            "completion_rate": round(len(completed) / len(rows), 4) if rows else 0}


def daily_summary(connection, days=30):
    cutoff = date.today() - timedelta(days=days - 1)
    result = defaultdict(lambda: {"completed_sessions": 0, "abandoned_sessions": 0, "focus_seconds": 0})
    for s in _ended(connection):
        stamp = s.get("finished_at") or s.get("started_at")
        if not stamp: continue
        key = datetime.fromisoformat(stamp).date()
        if key >= cutoff:
            item = result[key.isoformat()]
            item["completed_sessions" if s["status"] == "completed" else "abandoned_sessions"] += 1
            if s["status"] == "completed": item["focus_seconds"] += max(0, s["duration_seconds"] - s["remaining_seconds"])
    return [{"date": k, **result[k]} for k in sorted(result)]


def time_buckets(connection):
    buckets = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
    for s in _ended(connection):
        if s["status"] != "completed": continue
        hour = datetime.fromisoformat(s["finished_at"] or s["started_at"]).hour
        bucket = "morning" if 5 <= hour < 12 else "afternoon" if hour < 18 else "evening" if hour < 24 else "night"
        buckets[bucket] += 1
    return buckets


def streaks(connection):
    days = sorted({datetime.fromisoformat(s["finished_at"]).date() for s in _ended(connection) if s["status"] == "completed" and s.get("finished_at")})
    longest = current = 0; previous = None
    for day in days:
        current = current + 1 if previous and day == previous + timedelta(days=1) else 1
        longest = max(longest, current); previous = day
    today = date.today(); current_streak = 0
    if days and days[-1] >= today - timedelta(days=1):
        cursor = days[-1]
        while cursor in days:
            current_streak += 1; cursor -= timedelta(days=1)
    return {"current_streak": current_streak, "longest_streak": longest}


def report(connection):
    # Baseline report intentionally exposes only the basic counters. Date-range
    # filtering, streaks and a readable text rendering are left for follow-up work.
    return summary(connection)
