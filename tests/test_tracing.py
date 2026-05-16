"""
OpenTelemetry 追踪测试。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cybernetics_agent import CyberneticsConfig
from cybernetics_agent.context import CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.runtime.tracing import CyberneticsTracer, HAS_OPENTELEMETRY


def test_tracer_without_opentelemetry():
    """测试 tracer 基本功能（有无 opentelemetry 均可）。"""
    tracer = CyberneticsTracer()
    # 这里不强制 assert available 的值，因为环境可能安装了 opentelemetry
    # 重点是 trace_event 不应报错
    ctx = tracer.trace_event(CyberneticsEvent.create(
        event_type=EventType.TOOL_RESULT,
        session_id="s1",
        payload={"tool_name": "search"},
    ))
    with ctx:
        pass  # 不应报错


def test_tracer_set_error_without_opentelemetry():
    """未安装 opentelemetry 时 set_error 应该静默返回。"""
    tracer = CyberneticsTracer()
    tracer.set_error(ValueError("test"))


def test_context_with_tracer():
    """带 tracer 的上下文应该正常工作。"""
    cfg = CyberneticsConfig()
    tracer = CyberneticsTracer()
    ctx = CyberneticsContext(cfg, tracer=tracer)

    # 发射事件不应报错
    ctx.emit_tool_result("search", ["r1"])
    ctx.emit_llm_request("gpt-4", prompt_tokens=100)
    ctx.emit_tool_error("api", "timeout")


def test_context_without_tracer():
    """不带 tracer 的上下文应该正常工作。"""
    cfg = CyberneticsConfig()
    ctx = CyberneticsContext(cfg)
    ctx.emit_tool_result("search", ["r1"])
