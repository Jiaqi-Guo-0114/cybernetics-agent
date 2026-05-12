"""适配器基类。"""

from __future__ import annotations

import functools
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent, EventType
    from ..context import CyberneticsContext


class BaseAdapter(ABC):
    """控制论框架适配器基类。"""

    def __init__(self, ctx: "CyberneticsContext") -> None:
        self.ctx = ctx
        self._installed = False

    @abstractmethod
    def install(self, target: Any) -> None: ...

    def uninstall(self) -> None:
        self._installed = False

    def emit(self, event_type: "EventType", payload: dict) -> None:
        from ..core.base import CyberneticsEvent
        self.ctx.emit(CyberneticsEvent.create(event_type, self.ctx.session_id, payload))

    def _wrap(self, name: str, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """执行包装函数并采集事件。"""
        self.emit(self._event_type("TOOL_CALL"), {"tool_name": name})
        start = time.time()
        try:
            result = func(*args, **kwargs)
            self.emit(self._event_type("TOOL_RESULT"), {
                "tool_name": name, "success": True, "duration": time.time() - start,
            })
            return result
        except Exception as e:
            self.emit(self._event_type("TOOL_ERROR"), {
                "tool_name": name, "error": str(e), "error_type": type(e).__name__,
                "duration": time.time() - start,
            })
            raise

    def _event_type(self, name: str) -> "EventType":
        from ..core.base import EventType
        return EventType[name]

    def decorator(self, name: Optional[str] = None) -> Callable:
        """通用工具装饰器。"""
        def _d(func: Callable) -> Callable:
            n = name or func.__name__
            @functools.wraps(func)
            def _w(*a: Any, **k: Any) -> Any:
                return self._wrap(n, func, *a, **k)
            return _w
        return _d


class _Ctx:
    """上下文管理器。"""
    def __init__(self, adapter: BaseAdapter, name: str):
        self._a, self._n, self._t = adapter, name, 0.0

    def __enter__(self) -> "_Ctx":
        self._t = time.time()
        self._a.emit(self._a._event_type("STAGE_TRANSITION"), {"stage": self._n, "status": "started"})
        return self

    def __exit__(self, et: Any, ev: Any, tb: Any) -> None:
        ok = et is None
        self._a.emit(self._a._event_type("STAGE_TRANSITION"), {
            "stage": self._n, "status": "completed" if ok else "failed",
            "duration": time.time() - self._t, "success": ok,
        })
