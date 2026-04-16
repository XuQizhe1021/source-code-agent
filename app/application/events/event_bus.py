from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


EventHandler = Callable[[Dict[str, Any]], None]


@dataclass
class InProcessEventBus:
    """
    最小进程内事件总线。
    为什么先用进程内：
    - 当前目标是先把“跨域后续动作”从直接调用改为事件触发，降低耦合；
    - 后续若需要跨进程/消息队列，可在不改业务调用方的前提下替换总线实现。
    """

    _handlers: Dict[str, List[EventHandler]] = field(default_factory=lambda: defaultdict(list))

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        for handler in self._handlers.get(event_name, []):
            handler(payload)


event_bus = InProcessEventBus()
