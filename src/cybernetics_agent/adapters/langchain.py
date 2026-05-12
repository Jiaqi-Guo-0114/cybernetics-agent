"""
LangChain 适配器。

通过 LangChain 的 BaseCallbackHandler 接入控制论层。

使用示例:
    >>> from langchain_openai import ChatOpenAI
    >>> from cybernetics_agent.adapters import LangChainAdapter
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> ctx = CyberneticsContext(CyberneticsConfig())
    >>> adapter = LangChainAdapter(ctx)
    >>> llm = ChatOpenAI(callbacks=[adapter])
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseAdapter
from ..core.base import EventType


class LangChainAdapter(BaseAdapter):
    """
    LangChain Callback 适配器。

    实现了 LangChain 的 BaseCallbackHandler 接口，
    在关键生命周期节点发射控制论事件。

    支持的回调方法：
    - on_llm_start / on_llm_end: LLM 调用开始/结束
    - on_tool_start / on_tool_end: 工具调用开始/结束
    - on_chain_start / on_chain_end: Chain 执行开始/结束
    - on_agent_action / on_agent_finish: Agent 动作/完成
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self._tool_start_times: Dict[str, float] = {}
        self._llm_start_times: Dict[str, float] = {}

    def install(self, target: Any) -> None:
        """
        安装适配器到 LangChain 对象。

        参数:
            target: LangChain 的 LLM 、Chain 或 Agent 对象
        """
        # LangChain 通过 callbacks 列表接入
        if hasattr(target, "callbacks"):
            if target.callbacks is None:
                target.callbacks = [self]
            elif isinstance(target.callbacks, list):
                target.callbacks.append(self)
            else:
                target.callbacks = [target.callbacks, self]
            self._installed = True

    def uninstall(self) -> None:
        """卸载适配器。"""
        self._installed = False

    # ── LLM 回调 ──

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: list,
        **kwargs: Any,
    ) -> None:
        """LLM 调用开始时触发。"""
        model = serialized.get("name", "unknown")
        run_id = kwargs.get("run_id", "unknown")
        self._llm_start_times[str(run_id)] = time.time()

        # 估算 prompt tokens
        prompt_tokens = sum(len(p.split()) for p in prompts)  # 简化估算

        self.emit(EventType.LLM_REQUEST, {
            "model": model,
            "prompt_tokens": prompt_tokens,
        })

    def on_llm_end(
        self,
        response: Any,
        **kwargs: Any,
    ) -> None:
        """LLM 调用结束时触发。"""
        run_id = str(kwargs.get("run_id", "unknown"))
        start_time = self._llm_start_times.pop(run_id, None)
        duration = time.time() - start_time if start_time else 0.0

        model = "unknown"
        completion_tokens = 0

        # 尝试从响应中提取信息
        if hasattr(response, "generations"):
            # 提取模型名称
            if response.generations and response.generations[0]:
                first_gen = response.generations[0][0]
                if hasattr(first_gen, "generation_info"):
                    info = first_gen.generation_info or {}
                    model = info.get("model_name", "unknown")

        # 尝试从 usage_metadata 提取 token
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            completion_tokens = token_usage.get("completion_tokens", 0)

        self.emit(EventType.LLM_RESPONSE, {
            "model": model,
            "completion_tokens": completion_tokens,
            "duration": duration,
        })

    def on_llm_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        """LLM 调用出错时触发。"""
        self.emit(EventType.LLM_ERROR, {
            "error": str(error),
            "error_type": type(error).__name__,
        })

    # ── 工具回调 ──

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """工具调用开始时触发。"""
        tool_name = serialized.get("name", "unknown")
        run_id = str(kwargs.get("run_id", "unknown"))
        self._tool_start_times[run_id] = time.time()

        self.emit(EventType.TOOL_CALL, {
            "tool_name": tool_name,
            "input": input_str,
        })

    def on_tool_end(
        self,
        output: Any,
        **kwargs: Any,
    ) -> None:
        """工具调用结束时触发。"""
        run_id = str(kwargs.get("run_id", "unknown"))
        start_time = self._tool_start_times.pop(run_id, None)
        duration = time.time() - start_time if start_time else 0.0

        self.emit(EventType.TOOL_RESULT, {
            "tool_name": "unknown",  # 实际中需要从 context 获取
            "result": str(output) if output else None,
            "success": True,
            "duration": duration,
        })

    def on_tool_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        """工具调用出错时触发。"""
        self.emit(EventType.TOOL_ERROR, {
            "tool_name": "unknown",
            "error": str(error),
            "error_type": type(error).__name__,
        })

    # ── Chain 回调 ──

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Chain 执行开始。"""
        pass

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Chain 执行结束。"""
        pass

    def on_chain_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        """Chain 执行出错。"""
        self.emit(EventType.ERROR, {
            "error": str(error),
            "error_type": type(error).__name__,
            "source": "chain",
        })

    # ── Agent 回调 ──

    def on_agent_action(
        self,
        action: Any,
        **kwargs: Any,
    ) -> None:
        """Agent 执行动作。"""
        pass

    def on_agent_finish(
        self,
        finish: Any,
        **kwargs: Any,
    ) -> None:
        """Agent 完成任务。"""
        pass


# 导入 time 模块
import time


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    # 模拟 LangChain LLM 对象
    class MockLLM:
        def __init__(self):
            self.callbacks = None

    ctx = CyberneticsContext(CyberneticsConfig())
    adapter = LangChainAdapter(ctx)

    mock_llm = MockLLM()
    adapter.install(mock_llm)

    assert adapter.is_installed() is True
    assert adapter in mock_llm.callbacks
    print("  ✅ 冒烟测试通过：LangChain 适配器安装")
