import pytest

from app.application.knowledge.knowledge_retrieval_service import (
    KnowledgeRetrievalService,
    KnowledgeUseCaseError,
)


class _Knowledge:
    def __init__(self, embedding_model: str = "embed-model"):
        self.embedding_model = embedding_model


class _FakeRepository:
    def __init__(self):
        self.files = {
            "f1": "手册A",
            "f2": "手册B",
        }

    def get_knowledge_by_id(self, knowledge_id: str):
        if knowledge_id == "missing":
            return None
        return _Knowledge()

    def count_indexed_files(self, knowledge_id: str) -> int:
        return 2

    def get_knowledge_file_name(self, knowledge_file_id: str):
        return self.files.get(knowledge_file_id)


class _FakeGateway:
    def is_vector_store_ready(self) -> bool:
        return True

    async def embed_query(self, model_id: str, query: str):
        return [0.1, 0.2, 0.3]

    def search_similar(self, knowledge_id: str, query_vector, limit: int):
        return [
            {"file_id": "f1", "text": "命中1", "score": 1.2, "chunk_index": 1},
            {"file_id": "f2", "text": "命中2", "score": -0.3, "chunk_index": 2},
        ]


@pytest.mark.asyncio
async def test_retrieval_service_filters_and_clamps_scores():
    service = KnowledgeRetrievalService(repository=_FakeRepository(), embedding_gateway=_FakeGateway())
    result = await service.retrieve(
        knowledge_id="k1",
        params={"query": "怎么部署", "similarity_threshold": 0.5, "top_k": 5},
    )

    assert result["total"] == 1
    assert result["results"][0]["source_file"] == "手册A"
    assert result["results"][0]["score"] == 1


@pytest.mark.asyncio
async def test_retrieval_service_raises_when_knowledge_missing():
    service = KnowledgeRetrievalService(repository=_FakeRepository(), embedding_gateway=_FakeGateway())
    with pytest.raises(KnowledgeUseCaseError) as exc_info:
        await service.retrieve(knowledge_id="missing", params={"query": "q"})

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "知识库不存在"
