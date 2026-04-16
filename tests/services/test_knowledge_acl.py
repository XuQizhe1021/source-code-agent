import pytest

from app.application.acl.knowledge_acl import KnowledgeACL
from app.application.events.event_bus import event_bus


@pytest.mark.asyncio
async def test_knowledge_acl_returns_dto_and_publishes_event(monkeypatch):
    async def _fake_retrieve(self, knowledge_id, params):
        return {
            "results": [
                {
                    "content": "命中文本",
                    "score": 0.88,
                    "source_file": "文档A",
                    "file_id": "f1",
                    "chunk_id": 1,
                }
            ]
        }

    monkeypatch.setattr(
        "app.application.knowledge.knowledge_retrieval_service.KnowledgeRetrievalService.retrieve",
        _fake_retrieve,
    )

    received = []
    event_bus.subscribe("knowledge.retrieved", lambda payload: received.append(payload))

    acl = KnowledgeACL(db=None)
    snippets = await acl.retrieve_for_agent(
        query="测试问题",
        knowledge_bases=[{"id": "kb1", "name": "知识库A"}],
        config={},
    )

    assert len(snippets) == 1
    assert snippets[0].knowledge_id == "kb1"
    assert snippets[0].knowledge_name == "知识库A"
    assert received[-1]["count"] == 1
