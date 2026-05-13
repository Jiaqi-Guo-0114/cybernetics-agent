"""Context 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent import CyberneticsConfig, CyberneticsContext
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestContextFinal:
    def test_emit_tool_result_with_data(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_tool_result("search", ["r1", "r2"])
        ctx.shutdown()

    def test_emit_tool_error_with_msg(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_tool_error("search", "timeout error")
        ctx.shutdown()

    def test_emit_llm_request_with_model(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_llm_request("gpt-4", 1000)
        ctx.shutdown()

    def test_emit_llm_response_with_tokens(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        ctx.emit_llm_response("gpt-4", 500, 1.5)
        ctx.shutdown()

    def test_emit_stage_transition(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, ctx.session_id, {"from_stage": "s1", "to_stage": "s2"})
        ctx.emit(evt)
        ctx.shutdown()

    def test_emit_user_feedback(self):
        cfg = CyberneticsConfig()
        ctx = CyberneticsContext(cfg)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, ctx.session_id, {"type": "rating", "rating": 5})
        ctx.emit(evt)
        ctx.shutdown()
