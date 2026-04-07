import pytest

from app.domain.session_context import SessionContext


def test_add_and_get_messages_happy_path():
    context = SessionContext()
    context.add_message({"role": "system", "content": "你是助手"})
    context.add_message({"role": "user", "content": "你好"})
    messages = context.get_messages()
    assert messages == [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好"},
    ]


def test_illegal_role_is_rejected():
    context = SessionContext()
    with pytest.raises(ValueError, match="非法 role"):
        context.add_message({"role": "invalid", "content": "x"})


def test_get_messages_does_not_leak_internal_reference():
    context = SessionContext()
    original = {"role": "user", "content": "A"}
    context.add_message(original)
    original["content"] = "B"
    outer_copy = context.get_messages()
    outer_copy.append({"role": "assistant", "content": "hack"})
    outer_copy[0]["content"] = "C"
    inner = context.get_messages()
    assert inner == [{"role": "user", "content": "A"}]


def test_check_rep_after_state_change_enforces_max_messages():
    context = SessionContext(max_messages=1)
    context.add_message({"role": "system", "content": "x"})
    with pytest.raises(ValueError, match="消息数量超过上限"):
        context.add_message({"role": "user", "content": "y"})


def test_content_type_guard():
    context = SessionContext()
    with pytest.raises(TypeError, match="content 必须是 str"):
        context.add_message({"role": "user", "content": 123})


def test_internal_state_corruption_is_detected_by_rep_check():
    context = SessionContext()
    context.add_message({"role": "user", "content": "ok"})
    context._messages[0]["role"] = "hacker"
    with pytest.raises(AssertionError, match="内部消息 role 非法"):
        context._check_rep()


def test_message_extra_field_is_rejected():
    context = SessionContext()
    with pytest.raises(ValueError, match="仅允许 role/content"):
        context.add_message({"role": "user", "content": "ok", "name": "x"})


def test_add_messages_is_atomic():
    context = SessionContext()
    context.add_message({"role": "system", "content": "s"})
    with pytest.raises(ValueError, match="非法 role"):
        context.add_messages([
            {"role": "user", "content": "u1"},
            {"role": "invalid", "content": "x"},
        ])
    assert context.get_messages() == [{"role": "system", "content": "s"}]
