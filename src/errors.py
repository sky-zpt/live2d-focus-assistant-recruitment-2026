"""业务层向 API 层传递的可识别异常。"""


class SessionError(Exception):
    """专注会话相关异常的基类。"""


class ValidationError(SessionError):
    """用户输入不符合规则。"""


class SessionNotFoundError(SessionError):
    """请求的专注会话不存在。"""


class StateConflictError(SessionError):
    """当前会话状态不允许执行请求的操作。"""
