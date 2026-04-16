import pytest

from app.services.retrieval_strategies import (
    EnhancementStrategyDispatcher,
    KnowledgeRetrievalStrategy,
    WebSearchStrategy,
)
from app.services.strategy_base import BaseEnhancementStrategy, EnhancementPayload


class _DummyStrategy(BaseEnhancementStrategy):
    def __init__(self, name: str):
        self.name = name

    async def execute(self, query: str) -> EnhancementPayload:
        payload = EnhancementPayload()
        payload.events.append({"event": "dummy", "data": self.name})
        payload.system_messages.append(f"ctx:{self.name}:{query}")
        payload.sources.append({"source_file": self.name})
        return payload


@pytest.mark.asyncio
async def test_dispatcher_merges_payloads():
    dispatcher = EnhancementStrategyDispatcher([_DummyStrategy("A"), _DummyStrategy("B")])
    merged = await dispatcher.run("hello")
    assert [item["data"] for item in merged.events] == ["A", "B"]
    assert merged.system_messages == ["ctx:A:hello", "ctx:B:hello"]
    assert [item["source_file"] for item in merged.sources] == ["A", "B"]


@pytest.mark.asyncio
async def test_knowledge_strategy_uses_acl_contract(monkeypatch):
    async def _fake_retrieve_for_agent(self, *, query, knowledge_bases, config):
        return []

    monkeypatch.setattr(
        "app.application.acl.knowledge_acl.KnowledgeACL.retrieve_for_agent",
        _fake_retrieve_for_agent,
    )
    strategy = KnowledgeRetrievalStrategy(db=None, knowledge_bases=[type("KB", (), {"id": "kb1"})()], config={})
    payload = await strategy.execute("query")
    assert payload.sources == []
    assert payload.events[-1]["event"] == "vector_search_complete"


@pytest.mark.asyncio
async def test_web_strategy_formats_results(monkeypatch):
    async def _fake_search(_query):
        return {"results": [{"title": "t", "content": "c", "url": "u"}]}

    class _Formatter:
        @staticmethod
        def format_search_results(_results):
            return "formatted web context"

    monkeypatch.setattr("app.services.retrieval_strategies.search_web", _fake_search)
    monkeypatch.setattr("app.services.retrieval_strategies.get_web_search_client", lambda: _Formatter())

    payload = await WebSearchStrategy().execute("hi")
    assert payload.system_messages == ["formatted web context"]
    assert payload.web_search_results[0]["title"] == "t"
    assert payload.sources[0]["type"] == "web_search"
