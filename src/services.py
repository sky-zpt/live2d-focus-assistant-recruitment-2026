"""专注会话的业务规则与状态流转。"""

from datetime import datetime
from sqlite3 import Connection
from typing import Callable

from src import repositories
from src.errors import SessionNotFoundError, StateConflictError, ValidationError


FOCUS_DURATION_SECONDS = 25 * 60
MIN_DURATION_MINUTES = 1
MAX_DURATION_MINUTES = 120


def local_now() -> datetime:
    """返回带本地时区的当前时间。"""
    return datetime.now().astimezone()


class FocusSessionService:
    """在仓储层之上实现专注任务的校验、计时和状态规则。"""

    def __init__(
        self,
        connection: Connection,
        now: Callable[[], datetime] = local_now,
    ):
        self.connection = connection
        self.now = now

    def create_session(self, task_text: str, duration_minutes: int = 25):
        """创建并立即开始一条固定时长的专注会话。"""
        cleaned_text = self._validate_task_text(task_text)
        duration_seconds = self._validate_duration(duration_minutes)
        if repositories.get_open_session(self.connection) is not None:
            raise StateConflictError("当前已有未结束的专注任务")

        current_time = self._current_time()
        timestamp = self._to_timestamp(current_time)
        return repositories.create_session(
            self.connection,
            task_text=cleaned_text,
            duration_seconds=duration_seconds,
            remaining_seconds=duration_seconds,
            started_at=timestamp,
            last_started_at=timestamp,
            status="active",
        )

    def pause_session(self, session_id: int):
        """暂停活动会话，并结算截至当前的剩余秒数。"""
        session = self._require_session(session_id)
        self._require_status(session, {"active"}, "暂停")
        remaining_seconds = self._remaining_seconds(session, self._current_time())
        return repositories.update_session(
            self.connection,
            session_id,
            remaining_seconds=remaining_seconds,
            last_started_at=None,
            status="paused",
        )

    def resume_session(self, session_id: int):
        """继续一条已暂停的专注会话。"""
        session = self._require_session(session_id)
        self._require_status(session, {"paused"}, "继续")
        return repositories.update_session(
            self.connection,
            session_id,
            last_started_at=self._to_timestamp(self._current_time()),
            status="active",
        )

    def complete_session(self, session_id: int):
        """将活动或暂停会话标记为已完成。"""
        session = self._require_session(session_id)
        self._require_status(session, {"active", "paused"}, "完成")
        current_time = self._current_time()
        updates = {
            "finished_at": self._to_timestamp(current_time),
            "last_started_at": None,
            "status": "completed",
        }
        if session["status"] == "active":
            updates["remaining_seconds"] = self._remaining_seconds(session, current_time)
        return repositories.update_session(self.connection, session_id, **updates)

    def abandon_session(self, session_id: int):
        """放弃一条尚未结束的专注会话。"""
        session = self._require_session(session_id)
        self._require_status(session, {"active", "paused"}, "放弃")
        updates = {"last_started_at": None, "status": "abandoned"}
        if session["status"] == "active":
            updates["remaining_seconds"] = self._remaining_seconds(
                session, self._current_time()
            )
        return repositories.update_session(self.connection, session_id, **updates)

    def get_active_session(self):
        """返回当前开放会话，并附加计时是否归零的信息。"""
        session = repositories.get_open_session(self.connection)
        if session is None:
            return None

        session["remaining_seconds"] = self._remaining_seconds(
            session, self._current_time()
        )
        session["timer_finished"] = session["remaining_seconds"] == 0
        return session

    def list_completed_sessions(self, limit: int):
        """返回最近完成的会话记录。"""
        return repositories.list_completed_sessions(self.connection, limit)

    def _require_session(self, session_id: int):
        session = repositories.get_session_by_id(self.connection, session_id)
        if session is None:
            raise SessionNotFoundError("专注任务不存在")
        return session

    @staticmethod
    def _validate_task_text(task_text: str) -> str:
        if not isinstance(task_text, str):
            raise ValidationError("任务内容必须是文本")
        cleaned_text = task_text.strip()
        if not cleaned_text:
            raise ValidationError("请输入要完成的任务")
        if len(cleaned_text) > 80:
            raise ValidationError("任务内容不能超过 80 个字符")
        return cleaned_text

    @staticmethod
    def _validate_duration(duration_minutes: int) -> int:
        if isinstance(duration_minutes, bool) or not isinstance(duration_minutes, int):
            raise ValidationError("专注时长必须是整数分钟")
        if not MIN_DURATION_MINUTES <= duration_minutes <= MAX_DURATION_MINUTES:
            raise ValidationError("专注时长必须在 1 到 120 分钟之间")
        return duration_minutes * 60

    @staticmethod
    def _require_status(session: dict, allowed_statuses: set[str], action: str):
        if session["status"] not in allowed_statuses:
            raise StateConflictError(f"当前状态不能{action}")

    def _current_time(self) -> datetime:
        current_time = self.now()
        if current_time.tzinfo is None:
            raise ValueError("now() 必须返回带时区的时间")
        return current_time.astimezone()

    @staticmethod
    def _to_timestamp(value: datetime) -> str:
        return value.isoformat(timespec="seconds")

    def _remaining_seconds(self, session: dict, current_time: datetime) -> int:
        if session["status"] != "active":
            return max(0, session["remaining_seconds"])

        last_started_at = session["last_started_at"]
        if last_started_at is None:
            raise StateConflictError("活动任务缺少开始时间")
        started_time = datetime.fromisoformat(last_started_at)
        elapsed_seconds = max(0, int((current_time - started_time).total_seconds()))
        return max(0, session["remaining_seconds"] - elapsed_seconds)
