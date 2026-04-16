from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.application.acl.knowledge_acl import KnowledgeACL
from app.utils.config import get_neo4j_config
from app.utils.neo4j_utils import get_neo4j_service
from app.utils.web_search import get_web_search_client, search_web

from .strategy_base import BaseEnhancementStrategy, EnhancementPayload


class WebSearchStrategy(BaseEnhancementStrategy):
    """联网搜索策略。"""

    async def execute(self, query: str) -> EnhancementPayload:
        payload = EnhancementPayload()
        payload.events.append(
            _event("web_search", {"object": "chat.completion.web_search", "status": "正在联网搜索最新信息"})
        )
        try:
            search_results = await search_web(query)
            results = search_results.get("results", [])
            payload.web_search_results = results
            if results:
                formatter = get_web_search_client()
                payload.system_messages.append(formatter.format_search_results(search_results))
                for result in results:
                    payload.sources.append(
                        {
                            "content": result.get("content", ""),
                            "score": 1.0,
                            "source_file": result.get("title", "网络搜索结果"),
                            "url": result.get("url", ""),
                            "type": "web_search",
                        }
                    )
            payload.events.append(
                _event(
                    "web_search_complete",
                    {
                        "object": "chat.completion.web_search_complete",
                        "status": "已完成网络搜索" if results else "未找到相关网络信息",
                        "results_count": len(results),
                        "webList": results,
                    },
                )
            )
        except Exception as exc:
            payload.events.append(
                _event(
                    "web_search_complete",
                    {
                        "object": "chat.completion.web_search_complete",
                        "status": "网络搜索过程中发生错误",
                        "error": str(exc),
                        "webList": [],
                    },
                )
            )
        return payload


class KnowledgeRetrievalStrategy(BaseEnhancementStrategy):
    """知识库检索策略。"""

    def __init__(self, db: Session, knowledge_bases: List[Any], config: Dict[str, Any]) -> None:
        self.knowledge_bases = knowledge_bases
        self.config = config
        # 通过 ACL 访问 Knowledge 域，避免 Agent 域直接读取对方内部实现。
        self.knowledge_acl = KnowledgeACL(db)

    async def execute(self, query: str) -> EnhancementPayload:
        payload = EnhancementPayload()
        payload.events.append(
            _event("knowledge_search", {"object": "chat.completion.knowledge_search", "status": "正在检索知识库相关内容"})
        )
        retrieval_results: List[Dict[str, Any]] = []
        snippets = await self.knowledge_acl.retrieve_for_agent(
            query=query,
            knowledge_bases=self.knowledge_bases,
            config=self.config,
        )
        for snippet in snippets:
            retrieval_results.append(
                {
                    "content": snippet.content[:512],
                    "score": snippet.score,
                    "source_file": snippet.source_file,
                    "file_id": snippet.file_id,
                    "knowledge_id": snippet.knowledge_id,
                    "knowledge_name": snippet.knowledge_name,
                    "chunk_id": snippet.chunk_id,
                    "type": "document",
                }
            )

        if retrieval_results:
            context_lines = ["以下是知识库检索到的高相关内容，请优先参考："]
            for item in retrieval_results[:8]:
                context_lines.append(
                    f"- [{item.get('knowledge_name', '知识库')}/{item.get('source_file', '未知文件')}] {item.get('content', '')}"
                )
            payload.system_messages.append("\n".join(context_lines))
            payload.sources.extend(retrieval_results)

        payload.events.append(
            _event(
                "vector_search_complete",
                {
                    "object": "chat.completion.vector_search_complete",
                    "status": f"知识库检索完成，找到{len(retrieval_results)}条相关内容",
                    "results_count": len(retrieval_results),
                    "ragList": retrieval_results,
                },
            )
        )
        return payload


class GraphRetrievalStrategy(BaseEnhancementStrategy):
    """图谱检索策略（支持不可用场景下的安全降级）。"""

    def __init__(self, graphs: List[Any]) -> None:
        self.graphs = graphs

    async def execute(self, query: str) -> EnhancementPayload:
        payload = EnhancementPayload()
        payload.events.append(
            _event("graph_search", {"object": "chat.completion.graph_search", "status": "正在查询知识图谱"})
        )
        try:
            neo4j_cfg = get_neo4j_config()
            neo4j_service = get_neo4j_service(
                uri=neo4j_cfg.get("uri"),
                username=neo4j_cfg.get("username"),
                password=neo4j_cfg.get("password"),
                database=neo4j_cfg.get("database"),
                force_new=True,
            )
            if not neo4j_service or not neo4j_service.driver or not neo4j_service.is_connected():
                payload.events.append(
                    _event(
                        "graph_search_complete",
                        {
                            "object": "chat.completion.graph_search_complete",
                            "status": "知识图谱服务不可用，已降级跳过",
                            "graphList": {"nodes": [], "links": []},
                        },
                    )
                )
                return payload

            nodes: List[Dict[str, Any]] = []
            for graph in self.graphs:
                subgraph_id = (graph.neo4j_subgraph or "").lower().replace("-", "_")
                if not subgraph_id:
                    continue
                cypher = (
                    "MATCH (n) "
                    "WHERE n.graph_id = $graph_id AND "
                    "(toLower(coalesce(n.name, '')) CONTAINS toLower($keyword) "
                    "OR toLower(coalesce(n.title, '')) CONTAINS toLower($keyword)) "
                    "RETURN n LIMIT 8"
                )
                with neo4j_service.driver.session(database=neo4j_service.database) as session:
                    records = list(session.run(cypher, graph_id=subgraph_id, keyword=query))
                for record in records:
                    node = record.get("n")
                    if not node:
                        continue
                    node_id = str(getattr(node, "id", ""))
                    properties = dict(getattr(node, "_properties", {}) or {})
                    name = properties.get("name") or properties.get("title") or f"节点{node_id}"
                    nodes.append(
                        {
                            "id": node_id,
                            "name": name,
                            "symbolSize": 50,
                            "category": "Entity",
                            "properties": properties,
                        }
                    )
                    payload.sources.append(
                        {
                            "knowledge_name": getattr(graph, "name", "知识图谱"),
                            "source_file": name,
                            "content": json.dumps(properties, ensure_ascii=False),
                            "score": 0.9,
                            "type": "graph",
                        }
                    )

            payload.graph_list = {"nodes": nodes, "links": []}
            payload.events.append(
                _event(
                    "graph_search_complete",
                    {
                        "object": "chat.completion.graph_search_complete",
                        "status": "知识图谱搜索完成" if nodes else "知识图谱中未找到相关信息",
                        "graphList": payload.graph_list,
                    },
                )
            )
        except Exception as exc:
            payload.events.append(
                _event(
                    "graph_search_error",
                    {"object": "chat.completion.graph_search_error", "status": "知识图谱查询失败", "error": str(exc)},
                )
            )
            payload.events.append(
                _event(
                    "graph_search_complete",
                    {
                        "object": "chat.completion.graph_search_complete",
                        "status": "知识图谱服务异常，已降级返回空结果",
                        "graphList": {"nodes": [], "links": []},
                    },
                )
            )
        return payload


class EnhancementStrategyDispatcher:
    """
    策略调度器。

    把“策略启用条件”和“策略执行顺序”放在单独对象中，
    这样 endpoint 只保留流程骨架，后续扩展一个新通道时改动面最小。
    """

    def __init__(self, strategies: List[BaseEnhancementStrategy]) -> None:
        self.strategies = strategies

    async def run(self, query: str) -> EnhancementPayload:
        merged = EnhancementPayload()
        for strategy in self.strategies:
            payload = await strategy.execute(query)
            merged.events.extend(payload.events)
            merged.system_messages.extend(payload.system_messages)
            merged.sources.extend(payload.sources)
            merged.web_search_results.extend(payload.web_search_results)
            if payload.graph_list.get("nodes") or payload.graph_list.get("links"):
                merged.graph_list = payload.graph_list
        return merged


def _event(event: str, payload: Dict[str, Any]) -> Dict[str, str]:
    return {"event": event, "data": json.dumps(payload, ensure_ascii=False)}
