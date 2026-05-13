"""
CrewAI 适配器。"""

from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class CrewAIAdapter(BaseAdapter):
    """CrewAI 适配器。"""

    def install(self, target: Any) -> None:
        try:
            import crewai  # noqa: F401
        except ImportError as err:
            raise ImportError("pip install crewai") from err

        original_execute = target.execute

        def _execute(*args: Any, **kwargs: Any) -> Any:
            self.emit(self._event_type("AGENT_START"), {"task": getattr(target, "name", "unknown")})
            try:
                result = original_execute(*args, **kwargs)
                self.emit(self._event_type("AGENT_END"), {"status": "success"})
                return result
            except Exception as e:
                self.emit(self._event_type("ERROR"), {"error": str(e)})
                raise

        target.execute = _execute
        self._installed = True
