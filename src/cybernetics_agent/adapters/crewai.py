"""
CrewAI 适配器。

通过工具包装器接入控制论层。

使用示例:
    >>> from crewai import Agent, Task
    >>> from cybernetics_agent.adapters import CrewAIAdapter
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> ctx = CyberneticsContext(CyberneticsConfig())
    >>> adapter = CrewAIAdapter(ctx)
    >>> wrapped_tool = adapter.wrap_tool(my_tool)
"""

from __future__ import annotations

import time
import functools
from typing import Any, Callable, Dict, Optional

from .base import BaseAdapter
from ..core.base import EventType


class CrewAIAdapter(BaseAdapter):
    """
    CrewAI 工具包装器适配器。

    通过包装工具函数，在工具调用前后插入事件采集逻辑。

    支持的接入方式：
    - wrap_tool: 包装单个工具函数
    - wrap_agent: 包装整个 Agent 的工具集
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self._wrapped_tools: Dict[str, Any] = {}

    def install(self, target: Any) -> None:
        """
        安装适配器到 CrewAI 对象。

        参数:
            target: CrewAI 的 Agent 或 Tool 对象
        """
        if hasattr(target, "tools"):
            # 包装 Agent 的所有工具
            wrapped_tools = []
            for tool in target.tools:
                wrapped = self.wrap_tool(tool)
                wrapped_tools.append(wrapped)
            target.tools = wrapped_tools
            self._installed = True

    def uninstall(self) -> None:
        """卸载适配器。"""
        self._wrapped_tools.clear()
        self._installed = False

    def wrap_tool(self, tool: Any) -> Any:
        """
        包装单个工具。

        支持多种工具定义方式：
        - 函数对象
        - 带 run 方法的对象
        - 带 _run 方法的对象
        """
        tool_name = self._get_tool_name(tool)

        if callable(tool) and not hasattr(tool, "run"):
            # 函数对象
            @functools.wraps(tool)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self._execute_tool(tool_name, tool, *args, **kwargs)
            self._wrapped_tools[tool_name] = wrapper
            return wrapper

        elif hasattr(tool, "run"):
            # 带 run 方法的对象
            original_run = tool.run

            @functools.wraps(original_run)
            def wrapped_run(*args: Any, **kwargs: Any) -> Any:
                return self._execute_tool(tool_name, original_run, *args, **kwargs)

            tool.run = wrapped_run
            self._wrapped_tools[tool_name] = tool
            return tool

        elif hasattr(tool, "_run"):
            # 带 _run 方法的对象
            original_run = tool._run

            @functools.wraps(original_run)
            def wrapped_run(*args: Any, **kwargs: Any) -> Any:
                return self._execute_tool(tool_name, original_run, *args, **kwargs)

            tool._run = wrapped_run
            self._wrapped_tools[tool_name] = tool
            return tool

        return tool

    def _execute_tool(
        self,
        tool_name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """执行工具并采集事件。"""
        self.emit(EventType.TOOL_CALL, {
            "tool_name": tool_name,
            "args": str(args),
            "kwargs": str(kwargs),
        })

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            self.emit(EventType.TOOL_RESULT, {
                "tool_name": tool_name,
                "result": str(result) if result else None,
                "success": True,
                "duration": duration,
            })
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.emit(EventType.TOOL_ERROR, {
                "tool_name": tool_name,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration": duration,
            })
            raise

    def _get_tool_name(self, tool: Any) -> str:
        """获取工具名称。"""
        if hasattr(tool, "name"):
            return tool.name
        if hasattr(tool, "__name__"):
            return tool.__name__
        return "unknown_tool"


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    adapter = CrewAIAdapter(ctx)

    # 测试包装函数
    def my_search_tool(query: str) -> str:
        return f"results for {query}"

    wrapped = adapter.wrap_tool(my_search_tool)
    result = wrapped("test")
    assert result == "results for test"
    print("  ✅ 冒烟测试通过：CrewAI 工具包装")
