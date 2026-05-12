"""
Hermes Agent 适配器。

利用 Hermes 的 plugin hook 机制接入控制论层。

使用示例:
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> from cybernetics_agent.adapters import HermesAdapter
    >>> ctx = CyberneticsContext(CyberneticsConfig.from_json("cybernetics.json"))
    >>> adapter = HermesAdapter(ctx)
    >>> adapter.install(hermes_plugin_context)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAdapter
from ..core.base import EventType


class HermesAdapter(BaseAdapter):
    """
    Hermes Agent 插件适配器。

    通过 Hermes 的 hook 机制插入事件采集：
    - post_tool_call: 工具调用结束
    - post_llm_response: LLM 响应
    - on_error: 错误处理
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self._hooks_registered: Dict[str, Any] = {}

    def install(self, target: Any) -> None:
        """
        安装适配器到 Hermes 插件上下文。

        参数:
            target: Hermes 的 PluginContext 对象
                   需要支持 register_hook(hook_name, callback) 方法
        """
        # 注册工具调用 hook
        target.register_hook("post_tool_call", self._on_tool_call)
        self._hooks_registered["post_tool_call"] = self._on_tool_call

        # 注册 LLM 响应 hook
        target.register_hook("post_llm_response", self._on_llm_response)
        self._hooks_registered["post_llm_response"] = self._on_llm_response

        # 注册错误 hook
        target.register_hook("on_error", self._on_error)
        self._hooks_registered["on_error"] = self._on_error

        self._installed = True

    def uninstall(self) -> None:
        """卸载适配器。"""
        # 注: 实际中需要从 target 中取消注册 hook
        # 这里只做状态标记
        self._hooks_registered.clear()
        self._installed = False

    def _on_tool_call(
        self,
        tool_name: str,
        result: Any,
        session_id: str,
        **kwargs: Any,
    ) -> None:
        """处理工具调用结束事件。"""
        is_error = isinstance(result, Exception)
        if is_error:
            self.emit(EventType.TOOL_ERROR, {
                "tool_name": tool_name,
                "error": str(result),
                "error_type": type(result).__name__,
            }, session_id=session_id)
        else:
            self.emit(EventType.TOOL_RESULT, {
                "tool_name": tool_name,
                "result": result,
                "success": True,
            }, session_id=session_id)

    def _on_llm_response(
        self,
        model: str,
        response: Any,
        duration: float,
        session_id: str,
        **kwargs: Any,
    ) -> None:
        """处理 LLM 响应事件。"""
        # 尝试提取 token 信息
        completion_tokens = 0
        if hasattr(response, "usage"):
            usage = response.usage
            if hasattr(usage, "completion_tokens"):
                completion_tokens = usage.completion_tokens

        self.emit(EventType.LLM_RESPONSE, {
            "model": model,
            "completion_tokens": completion_tokens,
            "duration": duration,
        }, session_id=session_id)

    def _on_error(
        self,
        error: Exception,
        session_id: str,
        **kwargs: Any,
    ) -> None:
        """处理错误事件。"""
        self.emit(EventType.ERROR, {
            "error": str(error),
            "error_type": type(error).__name__,
        }, session_id=session_id)


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    # 模拟 Hermes PluginContext
    class MockPluginContext:
        def __init__(self):
            self.hooks = {}

        def register_hook(self, name, callback):
            self.hooks[name] = callback

    ctx = CyberneticsContext(CyberneticsConfig())
    adapter = HermesAdapter(ctx)

    mock_plugin = MockPluginContext()
    adapter.install(mock_plugin)

    assert adapter.is_installed() is True
    assert len(mock_plugin.hooks) == 3
    print("  ✅ 冒烟测试通过：Hermes 适配器安装")
