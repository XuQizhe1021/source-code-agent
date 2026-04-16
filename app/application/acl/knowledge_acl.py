from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.adapters.knowledge.gateways import ModelEmbeddingGateway
from app.adapters.knowledge.repositories import SqlAlchemyKnowledgeRepository
from app.application.acl.contracts import KnowledgeSnippetDTO
from app.application.events.event_bus import event_bus
from app.application.knowledge.knowledge_retrieval_service import (
    KnowledgeRetrievalService,
    KnowledgeUseCaseError,
)


class KnowledgeACL:
    """
    Agent -> Knowledge 防腐层。
    关键边界说明：
    - Agent 域只调用 ACL，不直接访问 Knowledge 域内部模型/查询细节；
    - 跨域返回统一 DTO 契约，防止“共享内部结构”导致隐式耦合。
    """

    def __init__(self, db: Session) -> None:
        repository = SqlAlchemyKnowledgeRepository(db)
        gateway = ModelEmbeddingGateway(db)
        self.retrieval_service = KnowledgeRetrievalService(repository=repository, embedding_gateway=gateway)

    async def retrieve_for_agent(
        self,
        *,
        query: str,
        knowledge_bases: List[Any],
        config: Dict[str, Any],
    ) -> List[KnowledgeSnippetDTO]:
        similarity_threshold = float(config.get("similarity_threshold", 0.7))
        top_k = int(config.get("top_k", 5))
        snippets: List[KnowledgeSnippetDTO] = []
        knowledge_ids: List[str] = []

        for kb in knowledge_bases:
            kb_id = _read_field(kb, "id")
            if not kb_id:
                continue
            kb_name = _read_field(kb, "name") or "知识库"
            knowledge_ids.append(kb_id)

            try:
                result = await self.retrieval_service.retrieve(
                    knowledge_id=kb_id,
                    params={
                        "query": query,
                        "similarity_threshold": similarity_threshold,
                        "top_k": top_k,
                    },
                )
            except (KnowledgeUseCaseError, RuntimeError):
                # 保持原链路容错行为：单个知识库失败不阻塞整体问答。
                continue

            for item in result.get("results", []):
                snippets.append(
                    KnowledgeSnippetDTO(
                        content=item.get("content", ""),
                        score=float(item.get("score", 0)),
                        source_file=item.get("source_file", "未知文件"),
                        file_id=item.get("file_id", ""),
                        chunk_id=int(item.get("chunk_id", 0)),
                        knowledge_id=kb_id,
                        knowledge_name=kb_name,
                    )
                )

        # 最小事件化：跨域检索完成后通过事件发布，后续动作由订阅者决定，避免硬编码直连。
        event_bus.publish(
            "knowledge.retrieved",
            {
                "query": query,
                "count": len(snippets),
                "knowledge_ids": knowledge_ids,
            },
        )
        return snippets


def _read_field(obj: Any, field_name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(field_name)
    return getattr(obj, field_name, None)
