"""
纯 Python 适配器。

最简单的接入方式，直接通过编程方式使用控制论层。

使用示例:
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> from cybernetics_agent.adapters import NativeAdapter
    >>> ctx = CyberneticsContext(CyberneticsConfig())
    >>> adapter = NativeAdapter(ctx)
    >>>
    >>> # 包装任意函数
    >>> @adapter.instrument_tool("my_function")
    >>> def my_function(x, y):
    ...     return x + y
    >>>
    >>> # 包装任意类
    >>> class MyService:
    ...     @adapter.instrument_method("process")
    ...     def process(self, data):
    ...         return data.upper()
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Dict, Optional

from .base import BaseAdapter
from ..core.base import EventType


class NativeAdapter(BaseAdapter):
    """
    纯 Python 适配器。

    提供装饰器和上下文管理器，用于在任何 Python 代码中插入控制论层。
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self._instrumented: Dict[str, Any] = {}

    def install(self, target: Any) -> None:
        """
        安装适配器。

        对于纯 Python 适配器，install 可以不做任何事情，
        因为接入是通过装饰器完成的。
        """
        self._installed = True

    def uninstall(self) -> None:
        """卸载适配器。"""
        self._instrumented.clear()
        self._installed = False

    def instrument_tool(self, name: Optional[str] = None) -> Callable:
        """
        工具装饰器。

        用于包装任意函数，自动采集调用数据。

        示例:
            >>> @adapter.instrument_tool("search")
            >>> def search(query):
            ...     return results
        """
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self._execute_instrumented(tool_name, func, *args, **kwargs)

            self._instrumented[tool_name] = wrapper
            return wrapper

        return decorator

    def instrument_method(self, name: Optional[str] = None) -> Callable:
        """
        方法装饰器。

        用于包装类方法。

        示例:
            >>> class MyService:
            ...     @adapter.instrument_method("process")
            ...     def process(self, data):
            ...         return data
        """
        def decorator(func: Callable) -> Callable:
            method_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(self_arg: Any, *args: Any, **kwargs: Any) -> Any:
                return self._execute_instrumented(method_name, func, self_arg, *args, **kwargs)

            self._instrumented[method_name] = wrapper
            return wrapper

        return decorator

    def _execute_instrumented(
        self,
        name: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """执行装饰的函数并采集事件。"""
        self.emit(EventType.TOOL_CALL, {
            "tool_name": name,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
        })

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            self.emit(EventType.TOOL_RESULT, {
                "tool_name": name,
                "result_type": type(result).__name__,
                "success": True,
                "duration": duration,
            })
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.emit(EventType.TOOL_ERROR, {
                "tool_name": name,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration": duration,
            })
            raise

    def context_manager(self, name: str = "block"):
        """
        上下文管理器。

        用于包裹代码块。

        示例:
            >>> with adapter.context_manager("data_processing"):
            ...     process_data()
        """
        return _InstrumentedContext(self, name)


class _InstrumentedContext:
    """装饰的上下文管理器。"""

    def __init__(self, adapter: NativeAdapter, name: str) -> None:
        self.adapter = adapter
        self.name = name
        self.start_time = 0.0

    def __enter__(self) -> "_InstrumentedContext":
        self.start_time = time.time()
        self.adapter.emit(EventType.STAGE_TRANSITION, {
            "stage": self.name,
            "status": "started",
        })
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration = time.time() - self.start_time
        success = exc_type is None

        self.adapter.emit(EventType.STAGE_TRANSITION, {
            "stage": self.name,
            "status": "completed" if success else "failed",
            "duration": duration,
            "success": success,
        })


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    adapter = NativeAdapter(ctx)
    adapter.install(None)

    # 测试 1: 函数装饰器
    @adapter.instrument_tool("add")
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5
    print("  ✅ 测试 1 通过：函数装饰器")

    # 测试 2: 上下文管理器
    with adapter.context_manager("test_block"):
        pass
    print("  ✅ 测试 2 通过：上下文管理器")

    # 测试 3: 错误捕获
    @adapter.instrument_tool("fail")
    def fail():
        raise ValueError("故意错误")

    try:
        fail()
    except ValueError:
        pass
    print("  ✅ 测试 3 通过：错误捕获")

    print("\n  ✅ 纯 Python 适配器所有冒烟测试通过！")
