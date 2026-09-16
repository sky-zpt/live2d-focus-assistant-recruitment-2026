CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_text TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    remaining_seconds INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    last_started_at TEXT,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('active', 'paused', 'completed', 'abandoned')
    ),
    archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS only_one_open_session_by_state
ON focus_sessions((1))
WHERE status IN ('active', 'paused');

CREATE INDEX IF NOT EXISTS focus_sessions_finished_at_idx
ON focus_sessions(finished_at);
CREATE INDEX IF NOT EXISTS focus_sessions_status_idx
ON focus_sessions(status);
