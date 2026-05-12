"""
运行时上下文。

所有模块通过 CyberneticsContext 访问共享状态。
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Dict, Optional

from .config import CyberneticsConfig
from .core.base import CyberneticsEvent, EventType, ICyberneticsModule
from .runtime.event_bus import EventBus
from .runtime.metrics_collector import MetricsCollector
from .runtime.state_manager import StateManager


class CyberneticsContext:
    """
    控制论运行时上下文。

    是整个控制论层的中心胞，负责：
    - 管理模块生命周期
    - 路由事件
    - 维护全局状态
    - 采集统计指标

    使用示例:
        >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
        >>> config = CyberneticsConfig.from_json("cybernetics.json")
        >>> ctx = CyberneticsContext(config)
        >>> ctx.emit_tool_result("search", ["result1", "result2"])
    """

    def __init__(self, config: CyberneticsConfig) -> None:
        self.config = config
        self.event_bus = EventBus()
        self.state_manager = StateManager(config.storage)
        self.metrics = MetricsCollector()
        self._modules: Dict[str, ICyberneticsModule] = {}
        self._session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self._lock = threading.Lock()

    @property
    def session_id(self) -> str:
        """当前 session ID。"""
        return self._session_id

    def register_module(self, module: ICyberneticsModule) -> None:
        """
        注册模块。

        模块注册后会自动订阅事件总线。
        """
        if not module.enabled:
            return
        with self._lock:
            self._modules[module.name] = module
        self.event_bus.subscribe(module)
        module.initialize()

    def unregister_module(self, name: str) -> None:
        """卸载模块。"""
        with self._lock:
            module = self._modules.pop(name, None)
        if module:
            self.event_bus.unsubscribe(module)
            module.shutdown()

    def emit(self, event: CyberneticsEvent) -> None:
        """
        发射事件到事件总线。

        所有订阅了该事件类型的模块会收到通知。
        """
        self.event_bus.emit(event)
        self.metrics.record_event(event)
        self.state_manager.save_event(event)

    def emit_tool_result(
        self,
        tool_name: str,
        result: Any,
        success: bool = True,
        duration: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """便捷方法：发射工具调用结果事件。"""
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
        self.emit(event)

    def emit_tool_error(
        self,
        tool_name: str,
        error: str,
        error_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """便捷方法：发射工具错误事件。"""
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
        self.emit(event)

    def emit_llm_request(
        self,
        model: str,
        prompt_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """便捷方法：发射 LLM 请求事件。"""
        event = CyberneticsEvent.create(
            event_type=EventType.LLM_REQUEST,
            session_id=self._session_id,
            payload={"model": model, "prompt_tokens": prompt_tokens},
            metadata=metadata or {},
        )
        self.emit(event)

    def emit_llm_response(
        self,
        model: str,
        completion_tokens: int = 0,
        duration: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """便捷方法：发射 LLM 响应事件。"""
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
        self.emit(event)

    def get_module(self, name: str) -> Optional[ICyberneticsModule]:
        """获取指定名称的模块实例。"""
        with self._lock:
            return self._modules.get(name)

    def get_all_modules(self) -> Dict[str, ICyberneticsModule]:
        """获取所有已注册模块。"""
        with self._lock:
            return dict(self._modules)

    def get_status(self) -> Dict[str, Any]:
        """获取整体状态报告。"""
        with self._lock:
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

    def shutdown(self) -> None:
        """关闭上下文，清理所有模块。"""
        with self._lock:
            names = list(self._modules.keys())
        for name in names:
            self.unregister_module(name)
        self.state_manager.close()
