"""
AsyncCyberneticsContext 测试。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig
from cybernetics_agent.async_context import AsyncCyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType, ICyberneticsModule


class AsyncCollector(ICyberneticsModule):
    """异步事件收集模块。"""

    name = "async_collector"
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
        return {"count": len(self.events)}


class SyncCollector(ICyberneticsModule):
    """同步事件收集模块。"""

    name = "sync_collector"
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
        return {"count": len(self.events)}


def test_async_context_emit():
    """基本异步 emit。"""
    async def _run():
        cfg = CyberneticsConfig(project_name="test-async")
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)

        await ctx.emit_tool_result("search", ["r1"])
        assert len(mod.events) == 1
        assert mod.events[0].payload["tool_name"] == "search"

    asyncio.run(_run())


def test_async_context_emit_tool_error():
    """发射工具错误事件。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)

        await ctx.emit_tool_error("api", "timeout")
        assert len(mod.events) == 1
        assert mod.events[0].event_type == EventType.TOOL_ERROR

    asyncio.run(_run())


def test_async_context_emit_llm_events():
    """发射 LLM 请求/响应事件。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)

        await ctx.emit_llm_request("gpt-4", prompt_tokens=100)
        await ctx.emit_llm_response("gpt-4", completion_tokens=50, duration=1.2)

        assert len(mod.events) == 2
        assert mod.events[0].event_type == EventType.LLM_REQUEST
        assert mod.events[1].event_type == EventType.LLM_RESPONSE

    asyncio.run(_run())


def test_async_context_mixed_modules():
    """同步和异步模块混合使用。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        async_mod = AsyncCollector()
        sync_mod = SyncCollector()
        await ctx.register_module(async_mod)
        await ctx.register_module(sync_mod)

        await ctx.emit_tool_result("search", ["r1"])
        assert len(async_mod.events) == 1
        assert len(sync_mod.events) == 1

    asyncio.run(_run())


def test_async_context_get_module():
    """获取模块。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)

        found = await ctx.get_module("async_collector")
        assert found is mod

        missing = await ctx.get_module("nonexistent")
        assert missing is None

    asyncio.run(_run())


def test_async_context_get_all_modules():
    """获取所有模块。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)

        all_modules = await ctx.get_all_modules()
        assert "async_collector" in all_modules

    asyncio.run(_run())


def test_async_context_get_status():
    """获取状态报告。"""
    async def _run():
        cfg = CyberneticsConfig(project_name="status-test")
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)
        await ctx.emit_tool_result("search", ["r1"])

        status = await ctx.get_status()
        assert status["project_name"] == "status-test"
        assert "async_collector" in status["modules"]
        assert status["modules"]["async_collector"]["count"] == 1

    asyncio.run(_run())


def test_async_context_disabled_module():
    """禁用的模块不应被注册。"""
    class DisabledMod(ICyberneticsModule):
        name = "disabled"
        enabled = False

        def __init__(self) -> None:
            super().__init__({}, None)

        def on_event(self, event):
            return event
        def initialize(self): pass
        def shutdown(self): pass
        def get_status(self): return {}

    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = DisabledMod()
        await ctx.register_module(mod)

        all_modules = await ctx.get_all_modules()
        assert "disabled" not in all_modules

    asyncio.run(_run())


def test_async_context_session_id():
    """session_id 应该唯一。"""
    cfg = CyberneticsConfig()
    ctx1 = AsyncCyberneticsContext(cfg)
    ctx2 = AsyncCyberneticsContext(cfg)
    assert ctx1.session_id != ctx2.session_id
    assert ctx1.session_id.startswith("sess_")


def test_async_context_shutdown():
    """关闭上下文。"""
    async def _run():
        cfg = CyberneticsConfig()
        ctx = AsyncCyberneticsContext(cfg)
        mod = AsyncCollector()
        await ctx.register_module(mod)
        await ctx.shutdown()

        all_modules = await ctx.get_all_modules()
        assert len(all_modules) == 0

    asyncio.run(_run())
