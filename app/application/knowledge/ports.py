from typing import Any, Dict, List, Optional, Protocol


class KnowledgeRecordPort(Protocol):
    """知识库记录最小视图，应用层只依赖必要字段。"""

    embedding_model: Optional[str]


class KnowledgeRepositoryPort(Protocol):
    """
    Repository 抽象端口：隔离应用层与 ORM 细节。
    为什么要抽象：
    - 让用例逻辑不直接依赖 SQLAlchemy，后续可替换为其它存储实现；
    - 单元测试可直接注入 fake repository，避免真实数据库依赖。
    """

    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeRecordPort]:
        ...

    def count_indexed_files(self, knowledge_id: str) -> int:
        ...

    def get_knowledge_file_name(self, knowledge_file_id: str) -> Optional[str]:
        ...


class EmbeddingGatewayPort(Protocol):
    """
    External Gateway 抽象端口：隔离应用层与向量库/模型调用细节。
    为什么要抽象：
    - 用例层只关心“能否嵌入、能否检索”，不关心具体 SDK；
    - 当模型服务或向量库切换时，只需替换 adapter，不改业务流程。
    """

    def is_vector_store_ready(self) -> bool:
        ...

    async def embed_query(self, model_id: str, query: str) -> List[float]:
        ...

    def search_similar(
        self,
        knowledge_id: str,
        query_vector: List[float],
        limit: int,
    ) -> List[Dict[str, Any]]:
        ...
