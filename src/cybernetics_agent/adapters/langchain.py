"""
LangChain 适配器。"""

from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class LangChainAdapter(BaseAdapter):
    """LangChain 适配器。"""

    def install(self, target: Any) -> None:
        try:
            from langchain.callbacks.base import BaseCallbackHandler
        except ImportError:
            raise ImportError("pip install langchain")

        class _Handler(BaseCallbackHandler):
            def __init__(self, adapter: "LangChainAdapter"):
                self._a = adapter

            def on_llm_start(self, serialized: dict, prompts: list, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("LLM_REQUEST"), {
                    "model": serialized.get("id", ["unknown"])[-1],
                    "prompt_tokens": sum(len(p) for p in prompts),
                })

            def on_llm_end(self, response: Any, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("LLM_RESPONSE"), {
                    "model": "unknown", "completion_tokens": getattr(response, "total_tokens", 0),
                })

            def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("TOOL_CALL"), {
                    "tool_name": serialized.get("name", "unknown"), "input": input_str,
                })

            def on_tool_end(self, output: str, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("TOOL_RESULT"), {
                    "tool_name": kwargs.get("serialized", {}).get("name", "unknown"),
                    "success": True,
                })

            def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("TOOL_ERROR"), {
                    "tool_name": kwargs.get("serialized", {}).get("name", "unknown"),
                    "error": str(error), "error_type": type(error).__name__,
                })

        target.callbacks = getattr(target, "callbacks", []) + [_Handler(self)]
        self._installed = True
