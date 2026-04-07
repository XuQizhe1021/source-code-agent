import copy
from typing import Any, Dict, List, Optional, Set


class SessionContext:
    """
    AF:
    - 表示一次对话会话中的消息上下文，按时间顺序维护可发送给模型的消息序列。

    RI:
    - _messages 是消息字典列表。
    - 每条消息必须包含且仅关注 role 与 content 两个核心字段。
    - role 必须属于 {'system', 'user', 'assistant'}。
    - content 必须是 str。
    - 消息数量不得超过 _max_messages。
    """

    _allowed_roles: Set[str] = {"system", "user", "assistant"}

    def __init__(self, initial_messages: Optional[List[Dict[str, Any]]] = None, max_messages: int = 200) -> None:
        self._max_messages = max_messages
        self._messages: List[Dict[str, str]] = []

        if initial_messages:
            for message in initial_messages:
                self.add_message(message)

        self._check_rep()

    def add_message(self, message: Dict[str, Any]) -> None:
        normalized = self._normalize_message(message)
        self._messages.append(normalized)
        self._check_rep()

    def prepend_message(self, message: Dict[str, Any]) -> None:
        normalized = self._normalize_message(message)
        self._messages.insert(0, normalized)
        self._check_rep()

    def add_messages(self, messages: List[Dict[str, Any]]) -> None:
        for message in messages:
            self.add_message(message)

    def get_messages(self) -> List[Dict[str, str]]:
        return copy.deepcopy(self._messages)

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, str]:
        if not isinstance(message, dict):
            raise TypeError("message 必须是 dict")

        if "role" not in message:
            raise ValueError("message 缺少 role")
        if "content" not in message:
            raise ValueError("message 缺少 content")

        role = message["role"]
        content = message["content"]

        if role not in self._allowed_roles:
            raise ValueError(f"非法 role: {role}")
        if not isinstance(content, str):
            raise TypeError("content 必须是 str")

        return {"role": role, "content": content}

    def _check_rep(self) -> None:
        if not isinstance(self._max_messages, int) or self._max_messages <= 0:
            raise ValueError("max_messages 必须是正整数")

        if len(self._messages) > self._max_messages:
            raise ValueError(f"消息数量超过上限: {self._max_messages}")

        for message in self._messages:
            if not isinstance(message, dict):
                raise AssertionError("内部消息必须是 dict")
            if set(message.keys()) != {"role", "content"}:
                raise AssertionError("内部消息键必须为 role/content")
            if message["role"] not in self._allowed_roles:
                raise AssertionError("内部消息 role 非法")
            if not isinstance(message["content"], str):
                raise AssertionError("内部消息 content 必须是 str")
