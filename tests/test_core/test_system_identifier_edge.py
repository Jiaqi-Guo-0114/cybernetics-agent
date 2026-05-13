"""SystemIdentifier 边界条件测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from cybernetics_agent.core.system_identifier import SystemIdentifier
from cybernetics_agent.core.base import CyberneticsEvent, EventType

class TestSystemIdentifierEdgeCases:
    def test_on_event_tool_result_with_duration(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 5.0, "success": True})
        si.on_event(evt)
        perf = si.get_tool_performance()
        assert isinstance(perf, dict)

    def test_on_event_tool_error_with_details(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search", "error": "timeout", "error_type": "TimeoutError"})
        si.on_event(evt)

    def test_on_event_stage_transition(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "s1", "to_stage": "s2", "duration": 1.0})
        si.on_event(evt)

    def test_on_event_unknown_type(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.USER_INPUT, "s1", {"text": "hello"})
        si.on_event(evt)

    def test_predict_performance_with_stages(self):
        si = SystemIdentifier({}, None)
        result = si.predict_performance("normal", ["stage1", "stage2"])
        assert isinstance(result, dict)

    def test_get_tool_performance_specific(self):
        si = SystemIdentifier({}, None)
        si.on_event(CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0}))
        perf = si.get_tool_performance("search")
        assert isinstance(perf, dict)

    def test_get_conversion_funnel_with_data(self):
        si = SystemIdentifier({}, None)
        si.on_event(CyberneticsEvent.create(EventType.STAGE_TRANSITION, "s1", {"from_stage": "init", "to_stage": "process"}))
        funnel = si.get_conversion_funnel(["init", "process", "done"])
        assert isinstance(funnel, dict)
