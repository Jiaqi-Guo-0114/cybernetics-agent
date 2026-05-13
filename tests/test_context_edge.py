"""Context 最终补充"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType


class TestContextEdgeCases:
    def test_emit_tool_result(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_tool_result("search", ["r1"])
        ctx.shutdown()

    def test_emit_tool_error(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_tool_error("search", "timeout")
        ctx.shutdown()

    def test_emit_llm_request(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_llm_request("gpt-4", 100)
        ctx.shutdown()

    def test_emit_llm_response(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_llm_response("gpt-4", 50, 0.5)
        ctx.shutdown()

    def test_get_status(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        status = ctx.get_status()
        assert "session_id" in status
        ctx.shutdown()

    def test_emit_raw_event(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, ctx.session_id, {})
        ctx.emit(evt)
        ctx.shutdown()
