from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EnhancementPayload:
    """
    统一增强策略返回结构。

    之所以把 web/知识库/图谱都约束为同一种返回形态，
    是为了让主流程只关心“调度顺序”和“结果拼装”，
    避免再次回到每加一个通道就加一段 if-else 的泥团状态。
    """

    events: List[Dict[str, Any]] = field(default_factory=list)
    system_messages: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    web_search_results: List[Dict[str, Any]] = field(default_factory=list)
    graph_list: Dict[str, List[Dict[str, Any]]] = field(
        default_factory=lambda: {"nodes": [], "links": []}
    )


class BaseEnhancementStrategy(ABC):
    """
    信息增强策略抽象基类。

    通过显式抽象接口，保证后续新增策略时无需改动编排器核心代码，
    这是开放封闭原则在本次重构中的落地点。
    """

    @abstractmethod
    async def execute(self, query: str) -> EnhancementPayload:
        """执行策略并返回统一结构化结果。"""

