import logging
from typing import Dict, Any

from app.application.events.event_bus import event_bus


_REGISTERED = False
_LOGGER = logging.getLogger(__name__)


def register_default_subscribers() -> None:
    """注册默认事件订阅者（幂等）。"""
    global _REGISTERED
    if _REGISTERED:
        return

    # 这是最小事件化落地：Knowledge 检索结束后通过事件触发后续动作（这里先做日志与可观测）。
    event_bus.subscribe("knowledge.retrieved", _on_knowledge_retrieved)
    _REGISTERED = True


def _on_knowledge_retrieved(payload: Dict[str, Any]) -> None:
    _LOGGER.info(
        "knowledge.retrieved event: query=%s count=%s knowledge_ids=%s",
        payload.get("query", ""),
        payload.get("count", 0),
        payload.get("knowledge_ids", []),
    )
