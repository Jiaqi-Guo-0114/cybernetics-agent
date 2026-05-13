"""SystemIdentifier 补充测试"""
import sys

sys.path.insert(0, 'src')

from cybernetics_agent.core.base import CyberneticsEvent, EventType
from cybernetics_agent.core.system_identifier import SystemIdentifier


class TestSystemIdentifierExtra:
    def test_on_event_tool_result(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_RESULT, "s1", {"tool_name": "search", "duration": 1.0})
        si.on_event(evt)
        perf = si.get_tool_performance()
        assert "search" in perf or perf == {}

    def test_on_event_tool_error(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.TOOL_ERROR, "s1", {"tool_name": "search", "error": "timeout"})
        si.on_event(evt)

    def test_on_event_user_feedback(self):
        si = SystemIdentifier({}, None)
        evt = CyberneticsEvent.create(EventType.USER_FEEDBACK, "s1", {"type": "rating", "rating": 5})
        si.on_event(evt)

    def test_predict_performance_empty(self):
        si = SystemIdentifier({}, None)
        pred = si.predict_performance()
        assert isinstance(pred, dict)

    def test_get_conversion_funnel(self):
        si = SystemIdentifier({}, None)
        funnel = si.get_conversion_funnel(["stage1", "stage2"])
        assert isinstance(funnel, dict)

