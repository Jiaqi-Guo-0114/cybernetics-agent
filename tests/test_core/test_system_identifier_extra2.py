"""SystemIdentifier 补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifierExtra:
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
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2"})
        si.on_event(evt)

    def test_predict_with_stages(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance("normal", ["s1", "s2"])
        assert isinstance(result, dict)

    def test_get_tool_performance_empty(self):
        si = SystemIdentifier({}, None)
        perf = si.get_tool_performance()
        assert isinstance(perf, dict)
