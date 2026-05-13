"""SystemIdentifier 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifierFinal:
    def test_on_event_llm_request(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {"model": "gpt-4", "tokens": 100})
        si.on_event(evt)

    def test_on_event_llm_response(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {"model": "gpt-4", "tokens": 50})
        si.on_event(evt)

    def test_on_event_user_input(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "hello"})
        si.on_event(evt)

    def test_on_event_stage_transition(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2", "duration": 1.0})
        si.on_event(evt)

    def test_get_tool_performance_specific(self):
        si = SystemIdentifier({}, None)
        si.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        perf = si.get_tool_performance("search")
        assert isinstance(perf, dict)

    def test_get_conversion_funnel_with_stages(self):
        si = SystemIdentifier({}, None)
        si.on_event(CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "init", "to_stage": "process"}))
        funnel = si.get_conversion_funnel(["init", "process", "done"])
        assert isinstance(funnel, dict)

    def test_predict_performance_with_context(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance("normal", ["s1", "s2"])
        assert isinstance(result, dict)

    def test_get_status(self):
        si = SystemIdentifier({}, None)
        status = si.get_status()
        assert "enabled" in status
        assert "total_samples" in status
