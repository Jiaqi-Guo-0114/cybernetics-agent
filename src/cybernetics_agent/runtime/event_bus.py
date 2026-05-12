"""
事件总线。

支持基于事件类型的发布/订阅模型。
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Dict, List, Optional

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
        self._subscribers: Dict[str, List["ICyberneticsModule"]] = {}
        self._all_subscribers: List["ICyberneticsModule"] = []
        self._event_log: List["CyberneticsEvent"] = []
        self._max_log_size = 1000
        self._lock = threading.Lock()

    def subscribe(
        self,
        module: "ICyberneticsModule",
        event_types: Optional[List[str]] = None,
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

    def unsubscribe(self, module: "ICyberneticsModule") -> None:
        """取消订阅。"""
        with self._lock:
            if module in self._all_subscribers:
                self._all_subscribers.remove(module)
            for subscribers in self._subscribers.values():
                if module in subscribers:
                    subscribers.remove(module)

    def emit(self, event: "CyberneticsEvent") -> None:
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
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List["CyberneticsEvent"]:
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

    def get_stats(self) -> Dict[str, int]:
        """获取事件统计。"""
        stats: Dict[str, int] = {}
        for event in self._event_log:
            key = event.event_type.value
            stats[key] = stats.get(key, 0) + 1
        return stats


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/runtime", 1)[0])
    from core.base import CyberneticsEvent, EventType, ICyberneticsModule

    # 测试 1: 基本发射/订阅
    bus = EventBus()

    class DummyModule(ICyberneticsModule):
        name = "dummy"
        received: List[str] = []

        def on_event(self, event):
            self.received.append(event.event_type.value)
            return event

        def get_status(self):
            return {"received": len(self.received)}

    mod = DummyModule({}, None)  # type: ignore
    bus.subscribe(mod)

    evt = CyberneticsEvent.create(EventType.TOOL_CALL, "sess_001", {"tool": "search"})
    bus.emit(evt)
    assert "tool_call" in mod.received
    print("  ✅ 测试 1 通过：基本发射/订阅")

    # 测试 2: 事件消耗
    class BlockingModule(ICyberneticsModule):
        name = "blocker"

        def on_event(self, event):
            return None  # 消耗所有事件

        def get_status(self):
            return {}

    blocker = BlockingModule({}, None)  # type: ignore
    bus2 = EventBus()
    bus2.subscribe(blocker)

    # 再添加一个应该收不到事件的模块
    mod2 = DummyModule({}, None)  # type: ignore
    bus2.subscribe(mod2)

    evt2 = CyberneticsEvent.create(EventType.TOOL_RESULT, "sess_001")
    bus2.emit(evt2)
    assert len(mod2.received) == 0  # 被 blocker 拦截了
    print("  ✅ 测试 2 通过：事件消耗")

    # 测试 3: 统计
    bus3 = EventBus()
    bus3.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1"))
    bus3.emit(CyberneticsEvent.create(EventType.TOOL_CALL, "s1"))
    bus3.emit(CyberneticsEvent.create(EventType.TOOL_ERROR, "s1"))
    stats = bus3.get_stats()
    assert stats.get("tool_call", 0) == 2
    assert stats.get("tool_error", 0) == 1
    print("  ✅ 测试 3 通过：事件统计")

    print("\n  ✅ 事件总线所有冒烟测试通过！")
