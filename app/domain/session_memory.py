from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass(frozen=True)
class MemoryTurn:
    user_message: str
    agent_response: str


class MemoryPolicy(ABC):
    @abstractmethod
    def select(self, turns: Sequence[MemoryTurn]) -> List[MemoryTurn]:
        pass


class RecentWindowPolicy(MemoryPolicy):
    def __init__(self, max_turns: int = 3) -> None:
        self._max_turns = max_turns
        self._check_rep()

    def _check_rep(self) -> None:
        if not isinstance(self._max_turns, int) or self._max_turns <= 0:
            raise ValueError("max_turns 必须是正整数")

    def select(self, turns: Sequence[MemoryTurn]) -> List[MemoryTurn]:
        self._check_rep()
        if not turns:
            return []
        return list(turns[-self._max_turns:])


class SessionMemoryManager:
    def __init__(self, policy: MemoryPolicy, max_chars_per_message: int = 400) -> None:
        self._policy = policy
        self._max_chars_per_message = max_chars_per_message
        self._check_rep()

    def _check_rep(self) -> None:
        if not isinstance(self._max_chars_per_message, int) or self._max_chars_per_message <= 0:
            raise ValueError("max_chars_per_message 必须是正整数")
        if not isinstance(self._policy, MemoryPolicy):
            raise TypeError("policy 必须实现 MemoryPolicy")

    def _clip(self, text: str) -> str:
        if len(text) <= self._max_chars_per_message:
            return text
        return text[: self._max_chars_per_message]

    def from_history_records(self, history_records: Sequence[Any]) -> List[Dict[str, str]]:
        self._check_rep()
        turns: List[MemoryTurn] = []
        for record in reversed(list(history_records)):
            user_message = getattr(record, "user_message", "")
            agent_response = getattr(record, "agent_response", "")
            if isinstance(user_message, str) and isinstance(agent_response, str):
                if user_message.strip() or agent_response.strip():
                    turns.append(MemoryTurn(user_message=user_message, agent_response=agent_response))

        selected_turns = self._policy.select(turns)
        memory_messages: List[Dict[str, str]] = []
        for turn in selected_turns:
            if turn.user_message.strip():
                memory_messages.append({"role": "user", "content": self._clip(turn.user_message)})
            if turn.agent_response.strip():
                memory_messages.append({"role": "assistant", "content": self._clip(turn.agent_response)})
        return memory_messages
