"""
Hermes 适配器。"""

from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class HermesAdapter(BaseAdapter):
    """Hermes Agent 适配器。"""

    def install(self, target: Any) -> None:
        """插入到 Hermes AIAgent 的 tool 调用链中。"""
        original_handle = getattr(target, "handle_function_call", None)

        def _wrap(*args: Any, **kwargs: Any) -> Any:
            self.emit(self._event_type("TOOL_CALL"), {"tool_name": str(args[0]) if args else "unknown"})
            try:
                result = original_handle(*args, **kwargs) if original_handle else args[0](*args[1:], **kwargs)
                self.emit(self._event_type("TOOL_RESULT"), {"tool_name": str(args[0]) if args else "unknown", "success": True})
                return result
            except Exception as e:
                self.emit(self._event_type("TOOL_ERROR"), {"tool_name": str(args[0]) if args else "unknown", "error": str(e)})
                raise

        if original_handle:
            target.handle_function_call = _wrap
        self._installed = True
