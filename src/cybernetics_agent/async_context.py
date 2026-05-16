"""
异步运行时上下文。

与同步的 CyberneticsContext 并行存在，各自独立。
使用 AsyncEventBus 实现全异步事件处理。

EventStore 和 MetricsCollector 等 IO 密集型操作通过
asyncio.to_thread 投射到线程池，避免阻塞事件循环。
"""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config import CyberneticsConfig
from .core.base import CyberneticsEvent, EventType, ICyberneticsModule
from .runtime.async_event_bus import AsyncEventBus
from .runtime.event_store import EventStore
from .runtime.metrics_collector import MetricsCollector
from .runtime.plugin_loader import PluginLoader
from .runtime.state_manager import StateManager

if TYPE_CHECKING:
    from pathlib import Path


class AsyncCyberneticsContext:
    """
    异步控制论运行时上下文。

    是整个异步控制论层的中心胞，负责：
    - 管理模块生命周期（异步）
    - 路由事件（异步）
    - 维护全局状态
    - 采集统计指标

    使用示例:
        >>> from cybernetics_agent import AsyncCyberneticsContext, CyberneticsConfig
        >>> config = CyberneticsConfig.from_json("cybernetics.json")
        >>> ctx = AsyncCyberneticsContext(config)
        >>> await ctx.emit_tool_result("search", ["result1", "result2"])
    """

    def __init__(self, config: CyberneticsConfig, tracer: Any | None = None) -> None:
        self.config = config
        self.event_bus = AsyncEventBus()
        self.state_manager = StateManager(config.storage)
        self.metrics = MetricsCollector()
        self._modules: dict[str, ICyberneticsModule] = {}
        self._session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self._lock = asyncio.Lock()
        self._plugin_loader = PluginLoader()
        self._tracer = tracer

    async def load_plugins(self, plugin_dirs: list[str] | None = None) -> int:
        """
        异步加载插件目录中的所有插件。

        Args:
            plugin_dirs: 插件目录列表，默认使用配置中的 plugins.paths

        Returns:
            成功加载的插件数量
        """
        if plugin_dirs is None:
            plugin_cfg = getattr(self.config, "plugins", None) or {}
            plugin_dirs = plugin_cfg.get("paths", ["./plugins"]) if isinstance(plugin_cfg, dict) else ["./plugins"]

        loaded = 0
        for dir_str in plugin_dirs:
            plugin_dir = Path(dir_str)
            discovered = self._plugin_loader.discover(plugin_dir)
            for info in discovered:
                plugin_cfg = (getattr(self.config, "plugins", None) or {}).get(info.name, {}) if isinstance(getattr(self.config, "plugins", None), dict) else {}
                instance = self._plugin_loader.load(info, plugin_cfg, self)
                if instance:
                    await self.register_module(instance)
                    loaded += 1

        return loaded

    async def unload_plugin(self, name: str) -> bool:
        """异步卸载指定插件。"""
        self._plugin_loader.unload(name)
        await self.unregister_module(name)
        return True

    async def list_plugins(self) -> dict[str, Any]:
        """列出已加载的插件状态。"""
        return {
            "loaded": self._plugin_loader.list_loaded(),
            "modules": list(self._modules.keys()),
        }

    @property
    def session_id(self) -> str:
        """当前 session ID。"""
        return self._session_id

    async def register_module(self, module: ICyberneticsModule) -> None:
        """
        异步注册模块。

        模块注册后会自动订阅事件总线。
        """
        if not module.enabled:
            return
        async with self._lock:
            self._modules[module.name] = module
        await self.event_bus.subscribe(module)
        module.initialize()

    async def unregister_module(self, name: str) -> None:
        """异步卸载模块。"""
        async with self._lock:
            module = self._modules.pop(name, None)
        if module:
            await self.event_bus.unsubscribe(module)
            module.shutdown()

    async def emit(self, event: CyberneticsEvent) -> None:
        """
        异步发射事件到事件总线。

        所有订阅了该事件类型的模块会收到通知。
        """
        if self._tracer is not None:
            with self._tracer.trace_event(event):
                await self._do_emit(event)
        else:
            await self._do_emit(event)

    async def _do_emit(self, event: CyberneticsEvent) -> None:
        """内部异步发射事件。"""
        await self.event_bus.emit(event)
        self.metrics.record_event(event)
        await asyncio.to_thread(self.state_manager.save_event, event)

    async def emit_tool_result(
        self,
        tool_name: str,
        result: Any,
        success: bool = True,
        duration: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """便捷方法：异步发射工具调用结果事件。"""
        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_RESULT,
            session_id=self._session_id,
            payload={
                "tool_name": tool_name,
                "result": result,
                "success": success,
                "duration": duration,
            },
            metadata=metadata or {},
        )
        await self.emit(event)

    async def emit_tool_error(
        self,
        tool_name: str,
        error: str,
        error_type: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """便捷方法：异步发射工具错误事件。"""
        event = CyberneticsEvent.create(
            event_type=EventType.TOOL_ERROR,
            session_id=self._session_id,
            payload={
                "tool_name": tool_name,
                "error": error,
                "error_type": error_type,
            },
            metadata=metadata or {},
        )
        await self.emit(event)

    async def emit_llm_request(
        self,
        model: str,
        prompt_tokens: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """便捷方法：异步发射 LLM 请求事件。"""
        event = CyberneticsEvent.create(
            event_type=EventType.LLM_REQUEST,
            session_id=self._session_id,
            payload={"model": model, "prompt_tokens": prompt_tokens},
            metadata=metadata or {},
        )
        await self.emit(event)

    async def emit_llm_response(
        self,
        model: str,
        completion_tokens: int = 0,
        duration: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """便捷方法：异步发射 LLM 响应事件。"""
        event = CyberneticsEvent.create(
            event_type=EventType.LLM_RESPONSE,
            session_id=self._session_id,
            payload={
                "model": model,
                "completion_tokens": completion_tokens,
                "duration": duration,
            },
            metadata=metadata or {},
        )
        await self.emit(event)

    async def get_module(self, name: str) -> ICyberneticsModule | None:
        """异步获取指定名称的模块实例。"""
        async with self._lock:
            return self._modules.get(name)

    async def get_all_modules(self) -> dict[str, ICyberneticsModule]:
        """异步获取所有已注册模块。"""
        async with self._lock:
            return dict(self._modules)

    async def get_status(self) -> dict[str, Any]:
        """异步获取整体状态报告。"""
        async with self._lock:
            modules = dict(self._modules)
        return {
            "session_id": self._session_id,
            "project_name": self.config.project_name,
            "modules": {
                name: mod.get_status()
                for name, mod in modules.items()
            },
            "metrics": self.metrics.get_summary(),
        }

    async def shutdown(self) -> None:
        """异步关闭上下文，清理所有模块。"""
        async with self._lock:
            names = list(self._modules.keys())
        for name in names:
            await self.unregister_module(name)
        self.state_manager.close()
