"""SystemIdentifier 最终补充测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifierFinal:
    def test_tool_result_no_tool_name(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"duration": 1.0})
        si.on_event(evt)

    def test_tool_error_no_tool_name(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {})
        si.on_event(evt)

    def test_llm_request_no_model(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_REQUEST, "s1", {})
        si.on_event(evt)

    def test_llm_response_no_model(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.LLM_RESPONSE, "s1", {})
        si.on_event(evt)

    def test_stage_transition_no_duration(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2"})
        si.on_event(evt)

    def test_user_input_no_text(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {})
        si.on_event(evt)

    def test_user_feedback_no_type(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {})
        si.on_event(evt)

    def test_get_tool_performance_no_data(self):
        si = SystemIdentifier({}, None)
        perf = si.get_tool_performance("nonexistent")
        assert perf == {}

    def test_get_bottlenecks(self):
        si = SystemIdentifier({}, None)
        status = si.get_status()
        assert isinstance(status, dict)

    def test_predict_empty(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance("normal")
        assert isinstance(result, dict)
