from dataclasses import dataclass


@dataclass
class KnowledgeSnippetDTO:
    """
    Agent 与 Knowledge 跨域通信契约（DTO）。
    为什么要用 DTO：
    - 只暴露跨域必需字段，避免 Agent 域依赖 Knowledge 域内部模型结构；
    - 即使 Knowledge 域内部表结构变化，契约稳定时 Agent 域可保持不动。
    """

    content: str
    score: float
    source_file: str
    file_id: str
    chunk_id: int
    knowledge_id: str
    knowledge_name: str
