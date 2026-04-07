from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Sequence, Tuple


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


class CharBudgetPolicy(MemoryPolicy):
    def __init__(self, max_chars: int = 800) -> None:
        self._max_chars = max_chars
        self._check_rep()

    def _check_rep(self) -> None:
        if not isinstance(self._max_chars, int) or self._max_chars <= 0:
            raise ValueError("max_chars 必须是正整数")

    def select(self, turns: Sequence[MemoryTurn]) -> List[MemoryTurn]:
        self._check_rep()
        selected_reversed: List[MemoryTurn] = []
        consumed = 0
        for turn in reversed(list(turns)):
            turn_size = len(turn.user_message) + len(turn.agent_response)
            if selected_reversed and consumed + turn_size > self._max_chars:
                break
            if not selected_reversed and turn_size > self._max_chars:
                selected_reversed.append(turn)
                break
            selected_reversed.append(turn)
            consumed += turn_size
        return list(reversed(selected_reversed))


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

    def _sort_records(self, history_records: Sequence[Any]) -> List[Any]:
        indexed_records: List[Tuple[int, Any, Any]] = []
        for index, record in enumerate(history_records):
            created_at = getattr(record, "created_at", None)
            if isinstance(created_at, datetime):
                indexed_records.append((0, created_at, record))
            else:
                indexed_records.append((1, index, record))
        indexed_records.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in indexed_records]

    def from_history_records(self, history_records: Sequence[Any]) -> List[Dict[str, str]]:
        self._check_rep()
        turns: List[MemoryTurn] = []
        sorted_records = self._sort_records(history_records)
        for record in sorted_records:
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
