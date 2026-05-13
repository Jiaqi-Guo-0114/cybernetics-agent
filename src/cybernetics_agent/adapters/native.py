"""纯 Python 适配器。"""

from __future__ import annotations

from typing import Any, Callable

from .base import BaseAdapter, _Ctx


class NativeAdapter(BaseAdapter):
    """纯 Python 适配器。通过装饰器接入控制论层。"""

    def install(self, target: Any) -> None:
        self._installed = True

    def instrument_tool(self, name: str | None = None) -> Callable:
        """工具装饰器。"""
        return self.decorator(name)

    def instrument_method(self, name: str | None = None) -> Callable:
        """方法装饰器。"""
        def _d(func: Callable) -> Callable:
            n = name or func.__name__
            def _w(self_arg: Any, *a: Any, **k: Any) -> Any:
                return self._wrap(n, func, self_arg, *a, **k)
            return _w
        return _d

    def context_manager(self, name: str = "block"):
        """上下文管理器。"""
        return _Ctx(self, name)
