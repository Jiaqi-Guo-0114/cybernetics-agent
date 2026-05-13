"""
事件总线。

支持基于事件类型的发布/订阅模型。
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent, ICyberneticsModule


class EventBus:
    """
    控制论事件总线。

    实现了发布/订阅模式，支持事件过滤和日志。

    使用示例:
        >>> bus = EventBus()
        >>> bus.subscribe(my_module)
        >>> bus.emit(event)
    """

    def __init__(self) -> None:
        # 事件类型 -> 订阅者列表
        self._subscribers: dict[str, list[ICyberneticsModule]] = {}
        self._all_subscribers: list[ICyberneticsModule] = []
        self._event_log: list[CyberneticsEvent] = []
        self._max_log_size = 1000
        self._lock = threading.Lock()

    def subscribe(
        self,
        module: ICyberneticsModule,
        event_types: list[str] | None = None,
    ) -> None:
        """
        订阅事件。

        参数:
            module: 要订阅的模块
            event_types: 关注的事件类型列表。为 None 则关注所有事件。
        """
        with self._lock:
            if event_types is None:
                self._all_subscribers.append(module)
            else:
                for et in event_types:
                    if et not in self._subscribers:
                        self._subscribers[et] = []
                    self._subscribers[et].append(module)

    def unsubscribe(self, module: ICyberneticsModule) -> None:
        """取消订阅。"""
        with self._lock:
            if module in self._all_subscribers:
                self._all_subscribers.remove(module)
            for subscribers in self._subscribers.values():
                if module in subscribers:
                    subscribers.remove(module)

    def emit(self, event: CyberneticsEvent) -> None:
        """
        发射事件到所有订阅者。

        处理流程：
        1. 记录到事件日志
        2. 通知全局订阅者
        3. 通知类型订阅者
        4. 如果某订阅者返回 None，事件停止传播
        """
        with self._lock:
            # 记录事件
            self._event_log.append(event)
            if len(self._event_log) > self._max_log_size:
                self._event_log = self._event_log[-self._max_log_size // 2:]

            current_event = event
            event_type_str = event.event_type.value

            # 通知全局订阅者
            for subscriber in list(self._all_subscribers):
                if current_event is None:
                    break
                current_event = subscriber.on_event(current_event)

            # 通知类型订阅者
            if current_event is not None and event_type_str in self._subscribers:
                for subscriber in list(self._subscribers[event_type_str]):
                    if current_event is None:
                        break
                    current_event = subscriber.on_event(current_event)

    def get_recent_events(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[CyberneticsEvent]:
        """
        获取最近的事件。

        参数:
            event_type: 过滤事件类型
            limit: 最大返回数量
        """
        events = self._event_log
        if event_type:
            events = [e for e in events if e.event_type.value == event_type]
        return events[-limit:]

    def clear_log(self) -> None:
        """清空事件日志。"""
        self._event_log.clear()

    def get_stats(self) -> dict[str, int]:
        """获取事件统计。"""
        stats: dict[str, int] = {}
        for event in self._event_log:
            key = event.event_type.value
            stats[key] = stats.get(key, 0) + 1
        return stats
