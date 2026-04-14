from __future__ import annotations

import json
import time
from typing import Any, AsyncGenerator, Dict, Optional

from sqlalchemy.orm import Session

from app.domain.session_context import SessionContext
from app.domain.session_memory import RecentWindowPolicy, SessionMemoryManager
from app.models.agent import AgentShareToken
from app.services.document_context_service import DocumentContextService
from app.services.retrieval_strategies import (
    EnhancementStrategyDispatcher,
    GraphRetrievalStrategy,
    KnowledgeRetrievalStrategy,
    WebSearchStrategy,
)
from app.utils import agent as agent_utils
from app.utils.model import execute_model_inference


class ChatOrchestrator:
    """
    聊天编排器（共享于多入口）。

    为什么抽这一层：
    1) endpoint 应该只做鉴权与参数绑定，不应承载业务细节；
    2) `/{agent_id}/chat` 和 `chat-with-api-key` 复用同一条主流程，避免“修一处漏一处”。
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_service = DocumentContextService()

    async def stream_chat(
        self,
        *,
        agent: Any,
        agent_id: str,
        chat_request: Any,
        current_user_id: str,
        is_share_access: bool,
        token: Optional[str] = None,
        api_key_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            yield _event("status", {"object": "chat.completion.status", "status": "开始处理请求"})

            messages = chat_request.messages
            user_message = messages[-1].content if messages and messages[-1].role == "user" else ""
            session_id = chat_request.session_id or f"session_{int(time.time())}"
            config_override = chat_request.config or {}
            file_ids = chat_request.file_ids or []

            if not user_message:
                yield _event("error", {"error": "请求中缺少用户消息"})
                yield {"event": "done", "data": "[DONE]"}
                return

            model_id = agent.model_id
            if not model_id:
                yield _event("error", {"error": "该智能体未关联模型，请先在智能体设置中关联一个对话模型"})
                yield {"event": "done", "data": "[DONE]"}
                return

            if not agent_utils.get_model(self.db, model_id):
                yield _event("error", {"error": f"模型不存在: {model_id}"})
                yield {"event": "done", "data": "[DONE]"}
                return

            start_time = time.time()
            response_content = ""
            used_tokens = 0
            sources = []
            web_search_results = []
            graph_list = {"nodes": [], "links": []}
            has_file_content = False

            session_context = SessionContext()
            memory_manager = SessionMemoryManager(
                policy=RecentWindowPolicy(max_turns=3),
                max_chars_per_message=400,
            )

            # 文件处理下沉到独立服务，避免主流程被 I/O 细节污染。
            file_result = await self.document_service.process_files(file_ids, self.db)
            for event_item in file_result.events:
                yield event_item
            if file_result.system_message:
                session_context.prepend_message({"role": "system", "content": file_result.system_message})
                has_file_content = file_result.has_file_content

            yield _event("think", {"object": "chat.completion.think", "status": "AI开始思考该如何回答您的问题"})

            if agent.system_prompt:
                session_context.add_message({"role": "system", "content": agent.system_prompt})

            config = {**(agent.config or {}), **config_override}
            strategies = []
            if agent.enable_web_search:
                strategies.append(WebSearchStrategy())
            if agent.knowledge_bases:
                strategies.append(
                    KnowledgeRetrievalStrategy(
                        db=self.db,
                        knowledge_bases=list(agent.knowledge_bases),
                        config=config,
                    )
                )
            if agent.graphs:
                strategies.append(GraphRetrievalStrategy(graphs=list(agent.graphs)))

            # 统一策略调度是本次重构核心：新增增强通道时只新增策略，不改主流程。
            dispatcher = EnhancementStrategyDispatcher(strategies)
            enhancement_payload = await dispatcher.run(user_message)
            for event_item in enhancement_payload.events:
                yield event_item
            for system_text in enhancement_payload.system_messages:
                session_context.add_message({"role": "system", "content": system_text})
            sources.extend(enhancement_payload.sources)
            web_search_results.extend(enhancement_payload.web_search_results)
            if enhancement_payload.graph_list.get("nodes") or enhancement_payload.graph_list.get("links"):
                graph_list = enhancement_payload.graph_list

            history_records = agent_utils.get_chat_history(
                db=self.db,
                agent_id=agent_id,
                session_id=session_id,
                skip=0,
                limit=6,
            )
            for memory_msg in memory_manager.from_history_records(history_records):
                session_context.add_message(memory_msg)
            for msg in messages:
                session_context.add_message({"role": msg.role, "content": msg.content})

            yield _event("reasoning", {"object": "chat.completion.reasoning", "status": "AI正在整合信息推理回答"})
            yield _event(
                "info",
                {
                    "object": "chat.completion.info",
                    "sources": sources,
                    "web_search_results": web_search_results,
                    "graphList": graph_list,
                },
            )
            yield _event("answer", {"object": "chat.completion.answer", "status": "AI开始生成答案"})

            model_response = await execute_model_inference(
                self.db,
                model_id,
                {"messages": session_context.get_messages(), "stream": True, **config},
            )

            async for chunk in model_response:
                if isinstance(chunk, dict):
                    choice = (chunk.get("choices") or [{}])[0]
                    delta = choice.get("delta", {})
                    content_piece = delta.get("content")
                    if content_piece:
                        response_content += content_piece
                    if delta.get("tool_calls"):
                        yield {"event": "tool_calls", "data": chunk}
                    elif choice.get("finish_reason") == "tool_calls":
                        yield {"event": "tool_call_result", "data": chunk}
                    else:
                        yield {"event": "message_chunk", "data": chunk}
                    continue
                try:
                    parsed = json.loads(chunk)
                    response_content += (
                        parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    )
                except Exception:
                    pass
                yield {"event": "message_chunk", "data": chunk}

            response_time = int((time.time() - start_time) * 1000)
            access_type = "share" if is_share_access else "user"
            share_token_id = None
            if token:
                share_token_obj = self.db.query(AgentShareToken).filter(AgentShareToken.token == token).first()
                if share_token_obj:
                    share_token_id = share_token_obj.id

            extra_data = {"response_time_ms": response_time, "tokens_used": used_tokens}
            if sources:
                extra_data["sources"] = sources
            if web_search_results:
                extra_data["web_results"] = web_search_results
            if has_file_content:
                extra_data["has_file_content"] = True

            try:
                agent_utils.create_chat_history(
                    db=self.db,
                    agent_id=agent_id,
                    session_id=session_id,
                    user_id=current_user_id,
                    user_message=user_message,
                    agent_response=response_content,
                    tokens_used=used_tokens,
                    response_time=response_time,
                    extra_data=extra_data,
                    access_type=access_type,
                    api_key_id=api_key_id,
                    share_token_id=share_token_id,
                    model_id=model_id,
                )
            except Exception as history_error:
                yield _event("status", {"object": "chat.completion.status", "status": f"记录聊天历史失败: {history_error}"})

            yield _event("status", {"object": "chat.completion.status", "status": "回答完成"})
            yield {"event": "done", "data": "[DONE]"}
        except Exception as exc:
            yield _event("error", {"error": f"生成响应时出错: {exc}"})
            yield {"event": "done", "data": "[DONE]"}


def _event(event: str, payload: Dict[str, Any]) -> Dict[str, str]:
    return {"event": event, "data": json.dumps(payload, ensure_ascii=False)}

