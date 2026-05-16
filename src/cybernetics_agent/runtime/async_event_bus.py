"""
异步事件总线。

支持基于事件类型的异步发布/订阅模型。
与同步的 EventBus 并行存在，各自独立。
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent, ICyberneticsModule


class AsyncEventBus:
    """
    异步控制论事件总线。

    支持异步订阅者和同步订阅者混合使用。
    对于同步订阅者，会自动投射到线程池执行。

    使用示例:
        >>> bus = AsyncEventBus()
        >>> bus.subscribe(my_module)
        >>> await bus.emit(event)
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[ICyberneticsModule]] = {}
        self._all_subscribers: list[ICyberneticsModule] = []
        self._event_log: list[CyberneticsEvent] = []
        self._max_log_size = 1000
        self._lock = asyncio.Lock()

    async def subscribe(
        self,
        module: ICyberneticsModule,
        event_types: list[str] | None = None,
    ) -> None:
        """
        异步订阅事件。

        参数:
            module: 要订阅的模块
            event_types: 关注的事件类型列表。为 None 则关注所有事件。
        """
        async with self._lock:
            if event_types is None:
                self._all_subscribers.append(module)
            else:
                for et in event_types:
                    if et not in self._subscribers:
                        self._subscribers[et] = []
                    self._subscribers[et].append(module)

    async def unsubscribe(self, module: ICyberneticsModule) -> None:
        """取消异步订阅。"""
        async with self._lock:
            if module in self._all_subscribers:
                self._all_subscribers.remove(module)
            for subscribers in self._subscribers.values():
                if module in subscribers:
                    subscribers.remove(module)

    async def emit(self, event: CyberneticsEvent) -> None:
        """
        异步发射事件到所有订阅者。

        处理流程：
        1. 记录到事件日志
        2. 并发通知所有订阅者
        3. 如果某订阅者返回 None，事件停止传播
        """
        async with self._lock:
            self._event_log.append(event)
            if len(self._event_log) > self._max_log_size:
                self._event_log = self._event_log[-self._max_log_size // 2:]

            current_event: CyberneticsEvent | None = event
            event_type_str = event.event_type.value

            all_subs = list(self._all_subscribers)
            type_subs = list(self._subscribers.get(event_type_str, []))

        # 在锁外调用订阅者，避免阻塞
        if current_event is not None:
            current_event = await self._notify_subscribers(all_subs, current_event)

        if current_event is not None and type_subs:
            current_event = await self._notify_subscribers(type_subs, current_event)

    async def _notify_subscribers(
        self,
        subscribers: list[ICyberneticsModule],
        event: CyberneticsEvent,
    ) -> CyberneticsEvent | None:
        """并发通知订阅者，支持同步和异步回调。"""
        for subscriber in subscribers:
            if event is None:
                break

            handler = subscriber.on_event
            if asyncio.iscoroutinefunction(handler):
                event = await handler(event)
            else:
                # 同步回调投射到线程池
                loop = asyncio.get_running_loop()
                event = await loop.run_in_executor(None, handler, event)

        return event

    async def get_recent_events(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[CyberneticsEvent]:
        """
        异步获取最近的事件。

        参数:
            event_type: 过滤事件类型
            limit: 最大返回数量
        """
        async with self._lock:
            events = self._event_log
            if event_type:
                events = [e for e in events if e.event_type.value == event_type]
            return events[-limit:]

    async def clear_log(self) -> None:
        """异步清空事件日志。"""
        async with self._lock:
            self._event_log.clear()

    async def get_stats(self) -> dict[str, int]:
        """异步获取事件统计。"""
        async with self._lock:
            stats: dict[str, int] = {}
            for event in self._event_log:
                key = event.event_type.value
                stats[key] = stats.get(key, 0) + 1
            return stats
