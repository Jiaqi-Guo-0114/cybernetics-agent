"""
AutoGen 适配器。

通过 Agent 包装器接入控制论层。

使用示例:
    >>> from autogen import AssistantAgent
    >>> from cybernetics_agent.adapters import AutoGenAdapter
    >>> from cybernetics_agent import CyberneticsContext, CyberneticsConfig
    >>> ctx = CyberneticsContext(CyberneticsConfig())
    >>> adapter = AutoGenAdapter(ctx)
    >>> wrapped_agent = adapter.wrap_agent(assistant)
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from .base import BaseAdapter
from ..core.base import EventType


class AutoGenAdapter(BaseAdapter):
    """
    AutoGen Agent 包装器适配器。

    通过包装 AutoGen Agent 的 send/receive 方法，
    在消息交互中插入事件采集。

    支持的接入方式：
    - wrap_agent: 包装整个 Agent
    - wrap_llm_client: 包装 LLM 客户端
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx)
        self._wrapped_agents: Dict[str, Any] = {}

    def install(self, target: Any) -> None:
        """
        安装适配器到 AutoGen 对象。

        参数:
            target: AutoGen 的 Agent 对象
        """
        if hasattr(target, "send"):
            self.wrap_agent(target)
            self._installed = True

    def uninstall(self) -> None:
        """卸载适配器。"""
        self._wrapped_agents.clear()
        self._installed = False

    def wrap_agent(self, agent: Any) -> Any:
        """
        包装 AutoGen Agent。

        拦截 send 和 receive 方法以采集事件。
        """
        agent_name = getattr(agent, "name", "unknown")

        # 包装 send 方法
        if hasattr(agent, "send"):
            original_send = agent.send

            def wrapped_send(message: Any, recipient: Any, request_reply: bool = True, silent: bool = False) -> Any:
                self.emit(EventType.USER_INPUT, {
                    "agent": agent_name,
                    "message": str(message)[:500],
                    "recipient": getattr(recipient, "name", "unknown"),
                })
                return original_send(message, recipient, request_reply, silent)

            agent.send = wrapped_send

        # 包装 receive 方法
        if hasattr(agent, "receive"):
            original_receive = agent.receive

            def wrapped_receive(message: Any, sender: Any, request_reply: bool = True, silent: bool = False) -> Any:
                self.emit(EventType.LLM_RESPONSE, {
                    "agent": agent_name,
                    "message": str(message)[:500],
                    "sender": getattr(sender, "name", "unknown"),
                })
                return original_receive(message, sender, request_reply, silent)

            agent.receive = wrapped_receive

        self._wrapped_agents[agent_name] = agent
        return agent

    def wrap_llm_client(self, client: Any) -> Any:
        """
        包装 LLM 客户端。

        用于采集 LLM 调用数据。
        """
        if hasattr(client, "create"):
            original_create = client.create

            def wrapped_create(*args: Any, **kwargs: Any) -> Any:
                model = kwargs.get("model", "unknown")
                messages = kwargs.get("messages", [])
                prompt_tokens = sum(len(str(m).split()) for m in messages)

                self.emit(EventType.LLM_REQUEST, {
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                })

                start_time = time.time()
                try:
                    response = original_create(*args, **kwargs)
                    duration = time.time() - start_time

                    completion_tokens = 0
                    if hasattr(response, "usage"):
                        completion_tokens = response.usage.completion_tokens

                    self.emit(EventType.LLM_RESPONSE, {
                        "model": model,
                        "completion_tokens": completion_tokens,
                        "duration": duration,
                    })
                    return response

                except Exception as e:
                    self.emit(EventType.LLM_ERROR, {
                        "model": model,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    })
                    raise

            client.create = wrapped_create

        return client


# ── 冒烟测试 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/adapters", 1)[0])
    from config import CyberneticsConfig
    from context import CyberneticsContext

    ctx = CyberneticsContext(CyberneticsConfig())
    adapter = AutoGenAdapter(ctx)

    # 模拟 AutoGen Agent
    class MockAgent:
        def __init__(self):
            self.name = "test_agent"

        def send(self, message, recipient, request_reply=True, silent=False):
            return "sent"

        def receive(self, message, sender, request_reply=True, silent=False):
            return "received"

    agent = MockAgent()
    wrapped = adapter.wrap_agent(agent)
    assert adapter.is_installed() is False  # 需要通过 install 才设置状态

    result = wrapped.send("hello", MockAgent())
    assert result == "sent"
    print("  ✅ 冒烟测试通过：AutoGen Agent 包装")
