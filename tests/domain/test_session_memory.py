import pytest

from app.domain.session_memory import RecentWindowPolicy, SessionMemoryManager


class _Record:
    def __init__(self, user_message: str, agent_response: str):
        self.user_message = user_message
        self.agent_response = agent_response


def test_recent_window_policy_selects_latest_turns():
    policy = RecentWindowPolicy(max_turns=2)
    manager = SessionMemoryManager(policy=policy, max_chars_per_message=100)
    records = [
        _Record("u3", "a3"),
        _Record("u2", "a2"),
        _Record("u1", "a1"),
    ]
    messages = manager.from_history_records(records)
    assert messages == [
        {"role": "user", "content": "u2"},
        {"role": "assistant", "content": "a2"},
        {"role": "user", "content": "u3"},
        {"role": "assistant", "content": "a3"},
    ]


def test_memory_message_is_clipped():
    manager = SessionMemoryManager(policy=RecentWindowPolicy(max_turns=1), max_chars_per_message=5)
    records = [_Record("123456", "abcdef")]
    messages = manager.from_history_records(records)
    assert messages == [
        {"role": "user", "content": "12345"},
        {"role": "assistant", "content": "abcde"},
    ]


def test_empty_or_invalid_content_is_filtered():
    manager = SessionMemoryManager(policy=RecentWindowPolicy(max_turns=3), max_chars_per_message=100)
    records = [_Record("", ""), _Record("   ", "\n"), _Record("u", "")]
    messages = manager.from_history_records(records)
    assert messages == [{"role": "user", "content": "u"}]


def test_max_turns_guard():
    with pytest.raises(ValueError, match="max_turns 必须是正整数"):
        RecentWindowPolicy(max_turns=0)


def test_max_chars_guard():
    with pytest.raises(ValueError, match="max_chars_per_message 必须是正整数"):
        SessionMemoryManager(policy=RecentWindowPolicy(max_turns=1), max_chars_per_message=0)
