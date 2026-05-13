"""Context 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestContextFinal:
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
