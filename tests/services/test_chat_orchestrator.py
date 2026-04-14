import pytest

from app.services.chat_orchestrator import ChatOrchestrator


class _Msg:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class _ChatRequest:
    def __init__(self):
        self.messages = [_Msg("user", "你好")]
        self.stream = True
        self.session_id = "s1"
        self.config = {}
        self.file_ids = []


class _Agent:
    def __init__(self):
        self.model_id = "model-1"
        self.system_prompt = "你是测试助手"
        self.config = {}
        self.enable_web_search = False
        self.knowledge_bases = []
        self.graphs = []


class _DummyDB:
    pass


@pytest.mark.asyncio
async def test_orchestrator_stream_chat_happy_path(monkeypatch):
    async def _fake_model_inference(_db, _model_id, _payload):
        async def _gen():
            yield {"choices": [{"delta": {"content": "你好，世界"}}]}

        return _gen()

    monkeypatch.setattr("app.services.chat_orchestrator.execute_model_inference", _fake_model_inference)
    monkeypatch.setattr("app.services.chat_orchestrator.agent_utils.get_model", lambda _db, _mid: object())
    monkeypatch.setattr("app.services.chat_orchestrator.agent_utils.get_chat_history", lambda **_kwargs: [])

    saved = {"called": False}

    def _fake_create_chat_history(**_kwargs):
        saved["called"] = True

    monkeypatch.setattr("app.services.chat_orchestrator.agent_utils.create_chat_history", _fake_create_chat_history)

    orchestrator = ChatOrchestrator(_DummyDB())
    events = []
    async for event in orchestrator.stream_chat(
        agent=_Agent(),
        agent_id="agent-1",
        chat_request=_ChatRequest(),
        current_user_id="u1",
        is_share_access=False,
        token=None,
        api_key_id=None,
    ):
        events.append(event["event"])

    assert "status" in events
    assert "message_chunk" in events
    assert events[-1] == "done"
    assert saved["called"] is True

