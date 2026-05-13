"""

AutoGen 适配器。"""

from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class AutoGenAdapter(BaseAdapter):
    """AutoGen 适配器。"""

    def install(self, target: Any) -> None:
        try:
            import autogen  # noqa: F401
        except ImportError as err:
            raise ImportError("pip install pyautogen") from err

        class _Handler:
            def __init__(self, adapter: AutoGenAdapter):
                self._a = adapter

            def on_llm_start(self, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("LLM_REQUEST"), {"model": kwargs.get("model", "unknown")})

            def on_llm_end(self, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("LLM_RESPONSE"), {})

            def on_tool_call(self, tool_call: dict, **kwargs: Any) -> None:
                self._a.emit(self._a._event_type("TOOL_CALL"), {
                    "tool_name": tool_call.get("function", {}).get("name", "unknown"),
                })

        target.register_reply(_Handler(self))
        self._installed = True
