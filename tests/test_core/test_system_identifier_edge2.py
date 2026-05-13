"""SystemIdentifier 最终补充"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifierEdgeCases:
    def test_on_event_tool_error_with_type(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search", "error": "timeout", "error_type": "TimeoutError"})
        si.on_event(evt)

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

    def test_on_event_unknown(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.ERROR, "s1", {})
        si.on_event(evt)

    def test_predict_empty(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance()
        assert isinstance(result, dict)

    def test_get_funnel_with_default(self):
        si = SystemIdentifier({}, None)
        funnel = si.get_conversion_funnel(["s1", "s2"])
        assert isinstance(funnel, dict)
