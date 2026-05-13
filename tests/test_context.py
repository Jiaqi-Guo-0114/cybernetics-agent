"""CyberneticsContext 测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestCyberneticsContext:
    def test_init(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        assert ctx.config == cfg
        assert ctx.session_id.startswith("sess_")
        ctx.shutdown()

    def test_emit_tool_result(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_tool_result("search", ["r1"])
        assert ctx.metrics.get_summary() != {}
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

    def test_get_module(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        assert ctx.get_module("nonexistent") is None
        ctx.shutdown()

    def test_get_all_modules(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        assert ctx.get_all_modules() == {}
        ctx.shutdown()

    def test_get_status(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        status = ctx.get_status()
        assert "session_id" in status
        assert "project_name" in status
        ctx.shutdown()

    def test_emit(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        evt = CyberneticsEvent.create(EventType.TOOL_CALL, ctx.session_id, {})
        ctx.emit(evt)
        ctx.shutdown()
