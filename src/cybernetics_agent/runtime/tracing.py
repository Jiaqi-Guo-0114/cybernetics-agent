"""
OpenTelemetry 分布式追踪集成（可选依赖）。

安装 opentelemetry-api 后自动启用：
    pip install opentelemetry-api

使用示例：
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    trace.set_tracer_provider(TracerProvider())

    ctx = CyberneticsContext(config, tracer=CyberneticsTracer())
    # 每次 emit() 自动创建 span
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core.base import CyberneticsEvent


try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode
    HAS_OPENTELEMETRY = True
except ImportError:  # pragma: no cover
    HAS_OPENTELEMETRY = False

    # 占位类，避免编译错误
    class trace:  # type: ignore[no-redef]
        @staticmethod
        def get_tracer(*_args: Any, **_kwargs: Any) -> Any:
            return None

    class SpanKind:  # type: ignore[no-redef]
        INTERNAL = 0

    class Status:  # type: ignore[no-redef]
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

    class StatusCode:  # type: ignore[no-redef]
        OK = 0
        ERROR = 1


class CyberneticsTracer:
    """
    Cybernetics Agent 追踪器。

    封装 OpenTelemetry tracer，为每个事件发射自动创建 span。
    """

    def __init__(self, tracer_name: str = "cybernetics-agent") -> None:
        self._tracer: Any = None
        if HAS_OPENTELEMETRY:
            self._tracer = trace.get_tracer(tracer_name)

    @property
    def available(self) -> bool:
        """是否可用（opentelemetry 已安装）。"""
        return self._tracer is not None

    def trace_event(self, event: CyberneticsEvent) -> Any:
        """
        为事件创建 span。

        返回 span context manager，用于 with 语句。
        """
        if not self.available:
            return _NullSpanContext()

        event_type = event.event_type.value
        span_name = f"cybernetics.{event_type}"

        # 从事件中提取属性
        attributes: dict[str, Any] = {
            "cybernetics.session_id": event.session_id or "",
            "cybernetics.event_type": event_type,
        }

        payload = event.payload or {}

        # 根据事件类型添加特定属性
        if event_type == "tool_result":
            attributes["cybernetics.tool_name"] = payload.get("tool_name", "")
            attributes["cybernetics.success"] = payload.get("success", True)
            attributes["cybernetics.duration_ms"] = payload.get("duration", 0.0) * 1000
        elif event_type == "tool_error":
            attributes["cybernetics.tool_name"] = payload.get("tool_name", "")
            attributes["cybernetics.error_type"] = payload.get("error_type", "")
        elif event_type == "llm_request":
            attributes["cybernetics.model"] = payload.get("model", "")
            attributes["cybernetics.prompt_tokens"] = payload.get("prompt_tokens", 0)
        elif event_type == "llm_response":
            attributes["cybernetics.model"] = payload.get("model", "")
            attributes["cybernetics.completion_tokens"] = payload.get("completion_tokens", 0)
            attributes["cybernetics.duration_ms"] = payload.get("duration", 0.0) * 1000

        return self._tracer.start_as_current_span(
            span_name,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )

    def set_error(self, error: Exception) -> None:
        """标记当前 span 为失败。"""
        if not self.available:
            return
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_status(Status(StatusCode.ERROR, str(error)))
            current_span.record_exception(error)


class _NullSpanContext:
    """空 span 上下文管理器，用于 opentelemetry 未安装时的回退。"""

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *_args: Any) -> None:
        pass
