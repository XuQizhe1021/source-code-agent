from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.application.knowledge.ports import EmbeddingGatewayPort
from app.utils.embedding import EmbeddingManager
from app.utils.model import execute_model_inference


class ModelEmbeddingGateway(EmbeddingGatewayPort):
    """模型与向量库网关适配器，封装现有外部调用细节。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def is_vector_store_ready(self) -> bool:
        vector_store = EmbeddingManager.get_vector_store()
        return vector_store is not None and vector_store.client is not None

    async def embed_query(self, model_id: str, query: str) -> List[float]:
        result = await execute_model_inference(
            self.db,
            model_id,
            {
                "input": [query],
                "model_type": "embedding",
            },
        )
        if "error" in result:
            raise RuntimeError(f"生成查询向量失败: {result['error']}")

        embeddings = result.get("embeddings", [])
        if not embeddings:
            raise RuntimeError("生成查询向量失败: embeddings 为空")
        return embeddings[0]

    def search_similar(
        self,
        knowledge_id: str,
        query_vector: List[float],
        limit: int,
    ) -> List[Dict[str, Any]]:
        vector_store = EmbeddingManager.get_vector_store()
        if not vector_store:
            return []
        return vector_store.search_similar(
            knowledge_id=knowledge_id,
            query_vector=query_vector,
            limit=limit,
            filter_expr=None,
        )
