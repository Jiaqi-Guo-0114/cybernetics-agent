"""
AsyncEventBus 测试。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent.core.base import CyberneticsEvent, EventType, ICyberneticsModule
from cybernetics_agent.runtime.async_event_bus import AsyncEventBus


class DummyAsyncModule(ICyberneticsModule):
    """模拟异步模块。"""

    name = "dummy_async"
    enabled = True

    def __init__(self) -> None:
        self.events: list[CyberneticsEvent] = []

    async def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent:
        self.events.append(event)
        return event

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"events": len(self.events)}


class DummySyncModule(ICyberneticsModule):
    """模拟同步模块。"""

    name = "dummy_sync"
    enabled = True

    def __init__(self) -> None:
        self.events: list[CyberneticsEvent] = []

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent:
        self.events.append(event)
        return event

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {"events": len(self.events)}


class StopModule(ICyberneticsModule):
    """模拟停止传播的模块。"""

    name = "stopper"
    enabled = True

    def __init__(self) -> None:
        super().__init__({}, None)

    def on_event(self, event: CyberneticsEvent) -> CyberneticsEvent | None:
        return None

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_status(self) -> dict:
        return {}


def test_async_event_bus_basic():
    """基本异步事件发射和订阅。"""
    async def _run():
        bus = AsyncEventBus()
        mod = DummyAsyncModule()
        await bus.subscribe(mod)

        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"tool": "search"},
        )
        await bus.emit(event)

        assert len(mod.events) == 1
        assert mod.events[0].payload["tool"] == "search"

    asyncio.run(_run())


def test_async_event_bus_sync_subscriber():
    """同步订阅者应该被正确处理。"""
    async def _run():
        bus = AsyncEventBus()
        mod = DummySyncModule()
        await bus.subscribe(mod)

        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"tool": "search"},
        )
        await bus.emit(event)

        assert len(mod.events) == 1

    asyncio.run(_run())


def test_async_event_bus_stop_propagation():
    """订阅者返回 None 应该停止传播。"""
    async def _run():
        bus = AsyncEventBus()
        stopper = StopModule()
        mod = DummyAsyncModule()

        await bus.subscribe(stopper)  # 先订阅，先收到
        await bus.subscribe(mod)

        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={"tool": "search"},
        )
        await bus.emit(event)

        assert len(mod.events) == 0  # 被 stopper 拦截

    asyncio.run(_run())


def test_async_event_bus_event_type_filter():
    """按事件类型过滤订阅。"""
    async def _run():
        bus = AsyncEventBus()
        mod = DummyAsyncModule()
        await bus.subscribe(mod, event_types=["tool_result"])

        event1 = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={},
        )
        event2 = CyberneticsEvent.create(
            event_type=EventType.LLM_REQUEST,
            session_id="s1",
            payload={},
        )
        await bus.emit(event1)
        await bus.emit(event2)

        assert len(mod.events) == 1
        assert mod.events[0].event_type == EventType.TOOL_RESULT

    asyncio.run(_run())


def test_async_event_bus_unsubscribe():
    """取消订阅。"""
    async def _run():
        bus = AsyncEventBus()
        mod = DummyAsyncModule()
        await bus.subscribe(mod)
        await bus.unsubscribe(mod)

        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={},
        )
        await bus.emit(event)

        assert len(mod.events) == 0

    asyncio.run(_run())


def test_async_event_bus_recent_events():
    """获取最近事件。"""
    async def _run():
        bus = AsyncEventBus()
        for i in range(5):
            event = CyberneticsEvent.create(
                event_type=EventType.TOOL_RESULT,
                session_id="s1",
                payload={"i": i},
            )
            await bus.emit(event)

        recent = await bus.get_recent_events(limit=3)
        assert len(recent) == 3
        assert recent[-1].payload["i"] == 4

    asyncio.run(_run())


def test_async_event_bus_stats():
    """事件统计。"""
    async def _run():
        bus = AsyncEventBus()
        for _ in range(3):
            await bus.emit(CyberneticsEvent.create(
                event_type=EventType.TOOL_RESULT,
                session_id="s1",
                payload={},
            ))
        for _ in range(2):
            await bus.emit(CyberneticsEvent.create(
                event_type=EventType.LLM_REQUEST,
                session_id="s1",
                payload={},
            ))

        stats = await bus.get_stats()
        assert stats.get("tool_result") == 3
        assert stats.get("llm_request") == 2

    asyncio.run(_run())


def test_async_event_bus_clear_log():
    """清空日志。"""
    async def _run():
        bus = AsyncEventBus()
        await bus.emit(CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id="s1",
            payload={},
        ))
        await bus.clear_log()
        recent = await bus.get_recent_events()
        assert len(recent) == 0

    asyncio.run(_run())


def test_async_event_bus_concurrent_emit():
    """并发发射亍应导致数据损坏。"""
    async def _run():
        bus = AsyncEventBus()
        mod = DummyAsyncModule()
        await bus.subscribe(mod)

        async def emit_n(n: int):
            for i in range(n):
                await bus.emit(CyberneticsEvent.create(
                    event_type=EventType.TOOL_RESULT,
                    session_id="s1",
                    payload={"i": i},
                ))

        await asyncio.gather(emit_n(50), emit_n(50))
        assert len(mod.events) == 100

    asyncio.run(_run())
