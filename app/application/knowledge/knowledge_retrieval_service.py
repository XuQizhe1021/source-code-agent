import asyncio
import copy
import hashlib
import json
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, Optional, Tuple

from app.application.knowledge.ports import EmbeddingGatewayPort, KnowledgeRepositoryPort


class _TTLCache:
    """进程内轻量缓存：只做短 TTL 热点加速，不做跨进程一致性承诺。"""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, value = item
            if expires_at <= now:
                self._store.pop(key, None)
                return None
            # 返回深拷贝避免调用方误改缓存内容，减少重复序列化也保证隔离。
            return copy.deepcopy(value)

    def set(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        expires_at = time.time() + max(ttl_seconds, 1)
        with self._lock:
            self._store[key] = (expires_at, copy.deepcopy(value))


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

    _shared_result_cache = _TTLCache()

    def __init__(
        self,
        repository: KnowledgeRepositoryPort,
        embedding_gateway: EmbeddingGatewayPort,
        cache_ttl_seconds: int = 30,
        embedding_timeout_seconds: float = 8.0,
        vector_search_timeout_seconds: float = 4.0,
    ) -> None:
        self.repository = repository
        self.embedding_gateway = embedding_gateway
        self.cache_ttl_seconds = cache_ttl_seconds
        self.embedding_timeout_seconds = embedding_timeout_seconds
        self.vector_search_timeout_seconds = vector_search_timeout_seconds
        # 高频读场景中，同参数短时间重复请求很多，用小型 TTL 缓存直接复用结果，减少模型和向量库压力。
        self._result_cache = self._shared_result_cache

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

        cache_key = self._build_cache_key(
            knowledge_id=knowledge_id,
            model_id=model_id,
            query=query,
            similarity_threshold=similarity_threshold,
            top_k=top_k,
        )
        cached_response = self._result_cache.get(cache_key)
        if cached_response is not None:
            return cached_response

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

        # 外部依赖可能变慢，给嵌入推理加超时并降级返回，避免主链路长时间阻塞。
        try:
            query_embedding = await asyncio.wait_for(
                self.embedding_gateway.embed_query(model_id, query),
                timeout=self.embedding_timeout_seconds,
            )
        except asyncio.TimeoutError:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "向量化依赖超时，已降级为空结果，请稍后重试",
            }

        # 向量检索是同步调用，这里转线程并限制等待时长，避免慢检索拖垮请求线程。
        try:
            hits = await asyncio.wait_for(
                asyncio.to_thread(
                    self.embedding_gateway.search_similar,
                    knowledge_id=knowledge_id,
                    query_vector=query_embedding,
                    limit=top_k,
                ),
                timeout=self.vector_search_timeout_seconds,
            )
        except asyncio.TimeoutError:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "向量检索超时，已降级为空结果，请稍后重试",
            }

        processed_results = []
        source_file_name_cache: Dict[str, str] = {}
        for hit in hits:
            knowledge_file_id = hit.get("file_id", "")
            if knowledge_file_id not in source_file_name_cache:
                source_file_name_cache[knowledge_file_id] = (
                    self.repository.get_knowledge_file_name(knowledge_file_id) or "未知文件"
                )
            source_file = source_file_name_cache[knowledge_file_id]

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

        response = {
            "query": query,
            "results": processed_results,
            "total": len(processed_results),
        }
        self._result_cache.set(cache_key, response, ttl_seconds=self.cache_ttl_seconds)
        return response

    def _build_cache_key(
        self,
        *,
        knowledge_id: str,
        model_id: str,
        query: str,
        similarity_threshold: float,
        top_k: int,
    ) -> str:
        cache_payload = {
            "knowledge_id": knowledge_id,
            "model_id": model_id,
            "query": query.strip(),
            "similarity_threshold": similarity_threshold,
            "top_k": top_k,
        }
        payload_str = json.dumps(cache_payload, ensure_ascii=True, sort_keys=True)
        return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
