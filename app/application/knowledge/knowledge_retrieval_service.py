from dataclasses import dataclass
from typing import Any, Dict

from app.application.knowledge.ports import EmbeddingGatewayPort, KnowledgeRepositoryPort


@dataclass
class KnowledgeUseCaseError(Exception):
    """应用层错误：由 Endpoint 统一做 HTTP 异常映射。"""

    status_code: int
    detail: str


class KnowledgeRetrievalService:
    """
    知识检索用例服务。
    为什么放在应用层：
    - 这里是“参数规范化 + 业务判断 + 结果拼装”的用例编排；
    - 通过端口依赖而不是直接调 utils/SDK，可替换实现并提升可测性。
    """

    def __init__(
        self,
        repository: KnowledgeRepositoryPort,
        embedding_gateway: EmbeddingGatewayPort,
    ) -> None:
        self.repository = repository
        self.embedding_gateway = embedding_gateway

    async def retrieve(self, knowledge_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        knowledge = self.repository.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            raise KnowledgeUseCaseError(status_code=404, detail="知识库不存在")

        query = params.get("query", "")
        if not query:
            raise KnowledgeUseCaseError(status_code=400, detail="查询文本不能为空")

        similarity_threshold = params.get("similarity_threshold", params.get("similarityThreshold", 0.7))
        top_k = params.get("top_k", params.get("topK", 5))
        try:
            similarity_threshold = float(similarity_threshold)
            top_k = int(top_k)
        except (TypeError, ValueError):
            similarity_threshold = 0.7
            top_k = 5

        model_id = knowledge.embedding_model
        if not model_id:
            raise KnowledgeUseCaseError(status_code=400, detail="知识库未配置嵌入模型")

        file_count = self.repository.count_indexed_files(knowledge_id)
        if file_count == 0:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "知识库中没有已索引的文件，无法进行检索",
            }

        if not self.embedding_gateway.is_vector_store_ready():
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "向量存储服务不可用，请检查 pymilvus 安装和配置",
            }

        query_embedding = await self.embedding_gateway.embed_query(model_id, query)
        hits = self.embedding_gateway.search_similar(
            knowledge_id=knowledge_id,
            query_vector=query_embedding,
            limit=top_k,
        )

        processed_results = []
        for hit in hits:
            knowledge_file_id = hit.get("file_id", "")
            source_file = self.repository.get_knowledge_file_name(knowledge_file_id) or "未知文件"

            score = hit.get("score", 0)
            score = max(0, min(1, score))
            if score >= similarity_threshold:
                processed_results.append(
                    {
                        "content": hit.get("text", ""),
                        "score": score,
                        "source_file": source_file,
                        "file_id": knowledge_file_id,
                        "chunk_id": hit.get("chunk_index", 0),
                    }
                )

        return {
            "query": query,
            "results": processed_results,
            "total": len(processed_results),
        }
